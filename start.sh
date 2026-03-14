#!/bin/bash
# Info-Getter 启动脚本 (使用 OpenClaw)

set -e

cd "$(dirname "$0")"

echo "🚀 启动 Info-Getter..."
echo "======================"
echo ""

# 检查环境
echo "📋 检查环境..."

# 检查数据目录
mkdir -p data/articles/research data/articles/daily logs

# 检查初始数据文件
for file in llm autonomous robotics zhuoyu; do
    if [ ! -f "data/articles/research/${file}.json" ]; then
        echo "[]" > "data/articles/research/${file}.json"
    fi
done

echo "✅ 环境检查完成"
echo ""

# 运行模式
MODE="${1:-demo}"

case "$MODE" in
    demo)
        echo "🎬 运行演示模式..."
        python3 tests/demo.py
        ;;
    
    once)
        echo "📥 运行单次采集..."
        # 直接运行 Python
        python3 -m info_getter --once 2>&1 | tee logs/run_$(date +%Y%m%d_%H%M%S).log
        ;;
    
    daemon)
        echo "👻 启动守护进程..."
        echo "日志: logs/daemon.log"
        nohup python3 -m info_getter > logs/daemon.log 2>&1 &
        echo $! > .pid
        echo "✅ 守护进程已启动 (PID: $(cat .pid))"
        echo "停止命令: ./start.sh stop"
        ;;
    
    stop)
        if [ -f .pid ]; then
            PID=$(cat .pid)
            if kill -0 $PID 2>/dev/null; then
                echo "🛑 停止守护进程 (PID: $PID)..."
                kill $PID
                rm .pid
                echo "✅ 已停止"
            else
                echo "⚠️ 进程已不存在"
                rm .pid
            fi
        else
            echo "⚠️ 没有运行中的守护进程"
        fi
        ;;
    
    status)
        echo "📊 状态检查"
        echo "==========="
        if [ -f .pid ]; then
            PID=$(cat .pid)
            if kill -0 $PID 2>/dev/null; then
                echo "状态: 🟢 运行中 (PID: $PID)"
            else
                echo "状态: 🔴 已停止"
            fi
        else
            echo "状态: ⚪ 未启动"
        fi
        echo ""
        echo "数据文件:"
        for file in data/articles/research/*.json; do
            if [ -f "$file" ]; then
                count=$(python3 -c "import json; print(len(json.load(open('$file'))))" 2>/dev/null || echo 0)
                echo "  $(basename $file): $count 篇"
            fi
        done
        ;;
    
    *)
        echo "用法: $0 [demo|once|daemon|stop|status]"
        echo ""
        echo "命令:"
        echo "  demo    - 运行演示 (默认)"
        echo "  once    - 单次采集"
        echo "  daemon  - 启动守护进程"
        echo "  stop    - 停止守护进程"
        echo "  status  - 查看状态"
        exit 1
        ;;
esac
