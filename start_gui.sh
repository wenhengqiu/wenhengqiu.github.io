#!/bin/bash
# Info-Getter GUI 启动脚本

echo "🤖 启动 Info-Getter Dashboard..."
cd "$(dirname "$0")"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python3"
    exit 1
fi

# 运行GUI
python3 info_getter_gui.py
