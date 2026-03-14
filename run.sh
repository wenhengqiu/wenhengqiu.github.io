#!/bin/bash
# Info-Getter 本地运行脚本
# 用法: ./run.sh [once|daemon|status]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查环境
check_env() {
    log_info "检查运行环境..."
    
    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    
    # 检查依赖
    if ! python3 -c "import aiohttp" 2>/dev/null; then
        log_warning "缺少依赖，尝试安装..."
        pip3 install -r info_getter/requirements.txt --user || {
            log_error "依赖安装失败，请手动安装: pip3 install -r info_getter/requirements.txt"
            exit 1
        }
    fi
    
    # 检查配置文件
    if [ ! -f "config/sources.yaml" ]; then
        log_error "配置文件不存在: config/sources.yaml"
        exit 1
    fi
    
    # 检查数据目录
    mkdir -p data/articles/research
    mkdir -p data/articles/daily
    mkdir -p logs
    
    log_success "环境检查通过"
}

# 运行一次
run_once() {
    log_info "运行单次采集任务..."
    python3 -m info_getter --once 2>&1 | tee logs/run_$(date +%Y%m%d_%H%M%S).log
}

# 守护进程模式
run_daemon() {
    log_info "启动守护进程模式..."
    log_info "按 Ctrl+C 停止"
    echo ""
    
    # 使用 nohup 后台运行
    nohup python3 -m info_getter > logs/daemon_$(date +%Y%m%d_%H%M%S).log 2>&1 &
    PID=$!
    
    echo $PID > .info-getter.pid
    log_success "守护进程已启动 (PID: $PID)"
    log_info "日志文件: logs/daemon_*.log"
    log_info "停止命令: ./run.sh stop"
}

# 停止守护进程
stop_daemon() {
    if [ -f ".info-getter.pid" ]; then
        PID=$(cat .info-getter.pid)
        if kill -0 $PID 2>/dev/null; then
            log_info "停止守护进程 (PID: $PID)..."
            kill $PID
            rm .info-getter.pid
            log_success "守护进程已停止"
        else
            log_warning "进程已不存在"
            rm .info-getter.pid
        fi
    else
        log_warning "没有运行中的守护进程"
    fi
}

# 查看状态
show_status() {
    log_info "Info-Getter 状态"
    echo "===================="
    
    # 检查进程
    if [ -f ".info-getter.pid" ]; then
        PID=$(cat .info-getter.pid)
        if kill -0 $PID 2>/dev/null; then
            echo -e "运行状态: ${GREEN}运行中${NC} (PID: $PID)"
        else
            echo -e "运行状态: ${RED}已停止${NC}"
        fi
    else
        echo -e "运行状态: ${YELLOW}未启动${NC}"
    fi
    
    # 显示配置
    echo ""
    echo "配置信息:"
    echo "  信息源: config/sources.yaml"
    echo "  数据目录: data/articles/"
    echo "  日志目录: logs/"
    
    # 显示最近日志
    echo ""
    echo "最近日志:"
    ls -lt logs/*.log 2>/dev/null | head -5 | awk '{print "  " $9}' || echo "  暂无日志"
    
    # 显示数据量
    echo ""
    echo "数据量统计:"
    for file in data/articles/research/*.json; do
        if [ -f "$file" ]; then
            count=$(python3 -c "import json; print(len(json.load(open('$file'))))" 2>/dev/null || echo 0)
            echo "  $(basename $file): $count 篇"
        fi
    done
}

# 运行演示
run_demo() {
    log_info "运行工作流程演示..."
    python3 tests/demo.py
}

# 主函数
main() {
    case "${1:-demo}" in
        once)
            check_env
            run_once
            ;;
        daemon|start)
            check_env
            run_daemon
            ;;
        stop)
            stop_daemon
            ;;
        status)
            show_status
            ;;
        demo)
            run_demo
            ;;
        restart)
            stop_daemon
            sleep 2
            check_env
            run_daemon
            ;;
        logs)
            tail -f logs/*.log
            ;;
        help|-h|--help)
            echo "Info-Getter 本地运行脚本"
            echo ""
            echo "用法: ./run.sh [命令]"
            echo ""
            echo "命令:"
            echo "  once      运行单次采集任务"
            echo "  daemon    启动守护进程模式"
            echo "  start     同 daemon"
            echo "  stop      停止守护进程"
            echo "  restart   重启守护进程"
            echo "  status    查看运行状态"
            echo "  demo      运行工作流程演示 (默认)"
            echo "  logs      查看实时日志"
            echo "  help      显示帮助"
            ;;
        *)
            log_error "未知命令: $1"
            echo "使用: ./run.sh help 查看帮助"
            exit 1
            ;;
    esac
}

main "$@"
