#!/bin/bash
# Info-Getter Docker 运行脚本

set -e

echo "🐳 Info-Getter Docker 启动脚本"
echo "================================"

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装"
    echo "请安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装"
    echo "请安装 Docker Compose"
    exit 1
fi

# 构建镜像
echo ""
echo "🔨 构建 Docker 镜像..."
docker-compose build

# 启动服务
echo ""
echo "🚀 启动服务..."
docker-compose up -d mongo selenium-hub chrome

# 等待服务就绪
echo ""
echo "⏳ 等待服务就绪..."
sleep 10

# 运行采集
echo ""
echo "📡 开始采集文章..."
docker-compose run --rm info-getter

# 显示结果
echo ""
echo "📊 采集完成!"
echo ""

# 复制数据到本地
docker-compose cp info-getter:/app/data/articles/research ./data/articles/

echo "✅ 数据已保存到本地"
echo ""

# 可选：停止服务
read -p "是否停止Docker服务? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose down
    echo "🛑 服务已停止"
fi
