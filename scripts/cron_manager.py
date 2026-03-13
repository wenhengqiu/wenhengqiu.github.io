#!/usr/bin/env python3
"""
Info-Getter Cron 任务管理器
用法: python cron_manager.py [--list] [--run <job_id>] [--status]
"""

import json
import yaml
import argparse
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from croniter import croniter

# 配置文件路径
CONFIG_PATH = Path.home() / ".openclaw" / "cron-dashboard.yaml"
STATE_PATH = Path.home() / ".openclaw" / "cron-state.json"

class CronManager:
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
            "jobs": {},
            "last_update": datetime.now().isoformat()
        }
    
    def _save_state(self):
        """保存状态"""
        self.state["last_update"] = datetime.now().isoformat()
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(STATE_PATH, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def _calculate_next_run(self, schedule, timezone="Asia/Shanghai"):
        """计算下次执行时间"""
        try:
            itr = croniter(schedule, datetime.now())
            return itr.get_next(datetime)
        except:
            return None
    
    def _format_duration(self, seconds):
        """格式化持续时间"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            return f"{seconds/60:.1f}m"
        else:
            return f"{seconds/3600:.1f}h"
    
    def _format_time_until(self, target_time):
        """格式化剩余时间"""
        if not target_time:
            return "未知"
        
        now = datetime.now()
        if isinstance(target_time, str):
            target_time = datetime.fromisoformat(target_time)
        
        diff = target_time - now
        
        if diff.total_seconds() < 0:
            return "已过期"
        
        hours = int(diff.total_seconds() // 3600)
        minutes = int((diff.total_seconds() % 3600) // 60)
        
        if hours > 0:
            return f"{hours}小时{minutes}分钟后"
        else:
            return f"{minutes}分钟后"
    
    def list_jobs(self):
        """列出所有任务"""
        print("📅 Info-Getter 定时任务")
        print("=" * 60)
        print()
        
        jobs = self.config.get('jobs', [])
        
        for job in jobs:
            job_id = job['id']
            job_state = self.state.get('jobs', {}).get(job_id, {})
            
            # 计算下次执行时间
            next_run = self._calculate_next_run(job['schedule'])
            
            # 状态图标
            last_status = job_state.get('last_status', 'unknown')
            icon = "🟢" if last_status == "success" else "🔴" if last_status == "failure" else "⚪"
            
            # 是否启用
            enabled = "✓" if job.get('enabled', True) else "✗"
            
            print(f"{icon} [{enabled}] {job['name']}")
            print(f"   ID: {job_id}")
            print(f"   描述: {job.get('description', 'N/A')}")
            print(f"   调度: {job['schedule']}")
            print(f"   下次: {self._format_time_until(next_run)}")
            
            if job_state.get('last_run'):
                print(f"   上次: {job_state.get('last_run', 'N/A')}")
            
            print()
        
        print(f"总计: {len(jobs)} 个任务")
    
    def show_status(self):
        """显示任务状态看板"""
        print("📊 Info-Getter 任务看板")
        print("=" * 60)
        print()
        
        now = datetime.now()
        jobs = self.config.get('jobs', [])
        
        # 统计
        total = len(jobs)
        enabled = sum(1 for j in jobs if j.get('enabled', True))
        
        # 今日执行统计
        today = now.strftime("%Y-%m-%d")
        today_runs = 0
        today_success = 0
        today_failure = 0
        
        for job_id, state in self.state.get('jobs', {}).items():
            history = state.get('history', [])
            for run in history:
                if run.get('time', '').startswith(today):
                    today_runs += 1
                    if run.get('status') == 'success':
                        today_success += 1
                    else:
                        today_failure += 1
        
        print(f"时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"任务: {enabled}/{total} 启用")
        print(f"今日: {today_runs} 次执行 | {today_success} 成功 | {today_failure} 失败")
        print()
        
        # 即将执行的任务
        print("⏰ 即将执行:")
        upcoming = []
        for job in jobs:
            if not job.get('enabled', True):
                continue
            next_run = self._calculate_next_run(job['schedule'])
            if next_run:
                upcoming.append({
                    'name': job['name'],
                    'next_run': next_run,
                    'time_until': self._format_time_until(next_run)
                })
        
        upcoming.sort(key=lambda x: x['next_run'])
        
        for job in upcoming[:5]:
            print(f"   • {job['name']}: {job['time_until']}")
        
        print()
        
        # 最近执行
        print("📝 最近执行:")
        recent_runs = []
        for job_id, state in self.state.get('jobs', {}).items():
            history = state.get('history', [])
            for run in history[-3:]:  # 最近3次
                recent_runs.append({
                    'job': state.get('name', job_id),
                    'time': run.get('time'),
                    'status': run.get('status'),
                    'duration': run.get('duration')
                })
        
        recent_runs.sort(key=lambda x: x.get('time', ''), reverse=True)
        
        for run in recent_runs[:5]:
            icon = "✓" if run['status'] == 'success' else "✗"
            time_str = run.get('time', 'N/A')
            if len(time_str) > 16:
                time_str = time_str[11:16]  # 只显示时间
            print(f"   {icon} {run['job']}: {time_str}")
        
        print()
    
    def run_job(self, job_id):
        """手动执行任务"""
        jobs = self.config.get('jobs', [])
        job = next((j for j in jobs if j['id'] == job_id), None)
        
        if not job:
            print(f"❌ 任务不存在: {job_id}")
            return
        
        print(f"🚀 执行任务: {job['name']}")
        print(f"   命令: {job['command']}")
        print()
        
        # 执行命令
        start_time = datetime.now()
        try:
            result = subprocess.run(
                job['command'],
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            if result.returncode == 0:
                status = "success"
                print(f"✅ 执行成功 ({self._format_duration(duration)})")
            else:
                status = "failure"
                print(f"❌ 执行失败 (code: {result.returncode})")
                if result.stderr:
                    print(f"   错误: {result.stderr[:200]}")
            
            # 更新状态
            if job_id not in self.state['jobs']:
                self.state['jobs'][job_id] = {}
            
            self.state['jobs'][job_id].update({
                'name': job['name'],
                'last_run': start_time.isoformat(),
                'last_status': status,
                'last_duration': duration
            })
            
            # 添加到历史
            if 'history' not in self.state['jobs'][job_id]:
                self.state['jobs'][job_id]['history'] = []
            
            self.state['jobs'][job_id]['history'].append({
                'time': start_time.isoformat(),
                'status': status,
                'duration': duration
            })
            
            # 限制历史记录数量
            self.state['jobs'][job_id]['history'] = \
                self.state['jobs'][job_id]['history'][-100:]
            
            self._save_state()
            
        except subprocess.TimeoutExpired:
            print("⏱️ 执行超时 (5分钟)")
        except Exception as e:
            print(f"❌ 执行异常: {e}")

def main():
    parser = argparse.ArgumentParser(description='Info-Getter Cron 管理器')
    parser.add_argument('--list', action='store_true', help='列出所有任务')
    parser.add_argument('--status', action='store_true', help='显示状态看板')
    parser.add_argument('--run', metavar='JOB_ID', help='手动执行任务')
    
    args = parser.parse_args()
    
    manager = CronManager()
    
    if args.list:
        manager.list_jobs()
    elif args.status:
        manager.show_status()
    elif args.run:
        manager.run_job(args.run)
    else:
        # 默认显示状态
        manager.show_status()

if __name__ == "__main__":
    main()
