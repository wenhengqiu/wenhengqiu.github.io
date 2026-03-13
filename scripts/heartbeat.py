#!/usr/bin/env python3
"""
Info-Getter 心跳监控脚本
用法: python heartbeat.py [--check] [--status] [--daemon]
"""

import json
import time
import argparse
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import yaml

# 配置文件路径
CONFIG_PATH = Path.home() / ".openclaw" / "heartbeat-monitor.yaml"
STATE_PATH = Path.home() / ".openclaw" / "heartbeat-state.json"

class HeartbeatMonitor:
    def __init__(self):
        self.config = self._load_config()
        self.state = self._load_state()
    
    def _load_config(self):
        """加载配置"""
        with open(CONFIG_PATH, 'r') as f:
            return yaml.safe_load(f)
    
    def _load_state(self):
        """加载状态"""
        if STATE_PATH.exists():
            with open(STATE_PATH, 'r') as f:
                return json.load(f)
        return {
            "last_update": datetime.now().isoformat(),
            "system_status": "unknown",
            "components": {},
            "alerts": []
        }
    
    def _save_state(self):
        """保存状态"""
        self.state["last_update"] = datetime.now().isoformat()
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(STATE_PATH, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def check_component(self, component):
        """检查单个组件"""
        component_id = component['id']
        check_config = component['check']
        
        try:
            if check_config['type'] == 'process':
                result = self._check_process(check_config)
            elif check_config['type'] == 'http':
                result = self._check_http(check_config)
            elif check_config['type'] == 'file':
                result = self._check_file(check_config)
            elif check_config['type'] == 'disk':
                result = self._check_disk(check_config)
            elif check_config['type'] == 'memory':
                result = self._check_memory(check_config)
            else:
                result = {"status": "unknown", "error": "Unknown check type"}
            
            return result
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _check_process(self, config):
        """检查进程"""
        pid_file = config.get('pid_file')
        process_name = config.get('process_name')
        
        if pid_file and Path(pid_file).exists():
            with open(pid_file) as f:
                pid = int(f.read().strip())
            # 检查进程是否存在
            result = subprocess.run(['kill', '-0', str(pid)], capture_output=True)
            if result.returncode == 0:
                return {"status": "healthy", "pid": pid}
        
        # 通过进程名检查
        if process_name:
            result = subprocess.run(['pgrep', '-f', process_name], capture_output=True)
            if result.returncode == 0:
                return {"status": "healthy", "pid": int(result.stdout.strip())}
        
        return {"status": "down", "error": "Process not found"}
    
    def _check_http(self, config):
        """检查HTTP服务"""
        import urllib.request
        
        url = config['url']
        timeout = config.get('response_timeout', 10)
        expected_status = config.get('expected_status', 200)
        
        try:
            req = urllib.request.Request(url, method=config.get('method', 'GET'))
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status == expected_status:
                    return {"status": "healthy", "response_time": 0}
                else:
                    return {"status": "unhealthy", "error": f"Status {response.status}"}
        except Exception as e:
            return {"status": "down", "error": str(e)}
    
    def _check_file(self, config):
        """检查文件"""
        file_path = Path(config['file_path'])
        max_age = config.get('max_age', 300)
        min_size = config.get('min_size', 0)
        
        if not file_path.exists():
            return {"status": "down", "error": "File not found"}
        
        stat = file_path.stat()
        age = time.time() - stat.st_mtime
        
        if age > max_age:
            return {"status": "unhealthy", "error": f"File too old ({age}s)"}
        
        if stat.st_size < min_size:
            return {"status": "unhealthy", "error": f"File too small ({stat.st_size}b)"}
        
        return {"status": "healthy", "age": age, "size": stat.st_size}
    
    def _check_disk(self, config):
        """检查磁盘空间"""
        import shutil
        
        path = config.get('path', '/')
        warning = config.get('warning_threshold', 80)
        critical = config.get('critical_threshold', 90)
        
        usage = shutil.disk_usage(path)
        percent = (usage.used / usage.total) * 100
        
        if percent >= critical:
            return {"status": "critical", "usage_percent": percent}
        elif percent >= warning:
            return {"status": "warning", "usage_percent": percent}
        else:
            return {"status": "healthy", "usage_percent": percent}
    
    def _check_memory(self, config):
        """检查内存使用"""
        try:
            with open('/proc/meminfo') as f:
                lines = f.readlines()
            
            mem_total = int(lines[0].split()[1])
            mem_available = int(lines[2].split()[1])
            
            used = mem_total - mem_available
            percent = (used / mem_total) * 100
            
            warning = config.get('warning_threshold', 80)
            critical = config.get('critical_threshold', 95)
            
            if percent >= critical:
                return {"status": "critical", "usage_percent": percent}
            elif percent >= warning:
                return {"status": "warning", "usage_percent": percent}
            else:
                return {"status": "healthy", "usage_percent": percent}
                
        except Exception as e:
            return {"status": "unknown", "error": str(e)}
    
    def check_all(self):
        """检查所有组件"""
        print("🔍 开始健康检查...")
        print()
        
        healthy_count = 0
        failed_components = []
        
        for component in self.config.get('components', []):
            component_id = component['id']
            component_name = component['name']
            
            # 执行检查
            result = self.check_component(component)
            
            # 更新状态
            if component_id not in self.state['components']:
                self.state['components'][component_id] = {
                    "name": component_name,
                    "status": "unknown",
                    "failure_count": 0,
                    "last_check": None
                }
            
            prev_status = self.state['components'][component_id]['status']
            new_status = result['status']
            
            self.state['components'][component_id].update({
                "status": new_status,
                "last_check": datetime.now().isoformat(),
                "details": result
            })
            
            # 更新失败计数
            if new_status not in ['healthy', 'warning']:
                self.state['components'][component_id]['failure_count'] += 1
                failed_components.append(component_name)
            else:
                self.state['components'][component_id]['failure_count'] = 0
                healthy_count += 1
            
            # 显示结果
            status_icon = "🟢" if new_status == "healthy" else "🟡" if new_status == "warning" else "🔴"
            print(f"{status_icon} {component_name}: {new_status}")
            if 'error' in result:
                print(f"   错误: {result['error']}")
        
        # 计算系统健康度
        total = len(self.config.get('components', []))
        health_score = (healthy_count / total * 100) if total > 0 else 0
        
        if health_score >= 95:
            system_status = "healthy"
        elif health_score >= 80:
            system_status = "good"
        elif health_score >= 60:
            system_status = "warning"
        else:
            system_status = "critical"
        
        self.state['system_status'] = system_status
        self.state['health_score'] = health_score
        self.state['failed_components'] = failed_components
        
        # 保存状态
        self._save_state()
        
        print()
        print(f"系统状态: {system_status} ({health_score:.1f}%)")
        
        return health_score
    
    def show_status(self):
        """显示当前状态"""
        print("💓 Info-Getter 健康状态")
        print("=" * 50)
        print()
        
        print(f"系统状态: {self.state.get('system_status', 'unknown')}")
        print(f"健康度: {self.state.get('health_score', 0):.1f}%")
        print(f"最后更新: {self.state.get('last_update', 'N/A')}")
        print()
        
        print("组件状态:")
        for component_id, info in self.state.get('components', {}).items():
            status = info.get('status', 'unknown')
            icon = "🟢" if status == "healthy" else "🟡" if status == "warning" else "🔴"
            print(f"  {icon} {info.get('name', component_id)}: {status}")
        
        print()
    
    def run_daemon(self):
        """守护进程模式"""
        interval = self.config.get('heartbeat', {}).get('interval', 30)
        
        print(f"🚀 心跳监控启动 (间隔: {interval}s)")
        print()
        
        while True:
            try:
                self.check_all()
                time.sleep(interval)
            except KeyboardInterrupt:
                print("\n👋 监控停止")
                break
            except Exception as e:
                print(f"❌ 监控错误: {e}")
                time.sleep(interval)

def main():
    parser = argparse.ArgumentParser(description='Info-Getter 心跳监控')
    parser.add_argument('--check', action='store_true', help='执行一次健康检查')
    parser.add_argument('--status', action='store_true', help='显示当前状态')
    parser.add_argument('--daemon', action='store_true', help='守护进程模式')
    
    args = parser.parse_args()
    
    monitor = HeartbeatMonitor()
    
    if args.daemon:
        monitor.run_daemon()
    elif args.status:
        monitor.show_status()
    else:
        # 默认执行一次检查
        monitor.check_all()

if __name__ == "__main__":
    main()
