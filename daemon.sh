#!/bin/bash
# Info-Getter 守护进程

cd "$(dirname "$0")"

start() {
    echo "🚀 启动 Info-Getter 守护进程..."
    
    if [ -f .daemon.pid ]; then
        PID=$(cat .daemon.pid)
        if kill -0 $PID 2>/dev/null; then
            echo "⚠️  已在运行 (PID: $PID)"
            return
        fi
    fi
    
    mkdir -p logs
    
    nohup bash -c '
        while true; do
            echo "[$(date "+%Y-%m-%d %H:%M:%S")] 开始采集..." >> logs/daemon.log
            python3 run_real.py >> logs/daemon.log 2>&1
            echo "[$(date "+%Y-%m-%d %H:%M:%S")] 等待1小时..." >> logs/daemon.log
            sleep 3600
        done
    ' > /dev/null 2>&1 &
    
    echo $! > .daemon.pid
    echo "✅ 已启动 (PID: $!)"
}

stop() {
    if [ -f .daemon.pid ]; then
        PID=$(cat .daemon.pid)
        if kill -0 $PID 2>/dev/null; then
            echo "🛑 停止 (PID: $PID)..."
            kill $PID
            rm .daemon.pid
            echo "✅ 已停止"
        else
            echo "⚠️  已停止"
            rm .daemon.pid
        fi
    else
        echo "⚠️  未运行"
    fi
}

status() {
    if [ -f .daemon.pid ]; then
        PID=$(cat .daemon.pid)
        if kill -0 $PID 2>/dev/null; then
            echo "🟢 运行中 (PID: $PID)"
            echo ""
            tail -3 logs/daemon.log 2>/dev/null || echo "暂无日志"
        else
            echo "🔴 已停止"
            rm .daemon.pid
        fi
    else
        echo "⚪ 未启动"
    fi
}

case "$1" in
    start) start ;;
    stop) stop ;;
    restart) stop; sleep 2; start ;;
    status|*) status ;;
esac
