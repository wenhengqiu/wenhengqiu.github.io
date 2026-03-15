#!/bin/bash
# MongoDB 启动脚本 (本地开发)

# 检查 MongoDB 是否已安装
if ! command -v mongod &> /dev/null; then
    echo "❌ MongoDB 未安装"
    echo "请安装 MongoDB:"
    echo "  macOS: brew install mongodb-community"
    echo "  Ubuntu: sudo apt-get install mongodb"
    echo "  或使用 Docker: docker run -d -p 27017:27017 --name mongodb mongo:latest"
    exit 1
fi

# 检查 MongoDB 是否已运行
if pgrep -x "mongod" > /dev/null; then
    echo "✅ MongoDB 已在运行"
else
    echo "🚀 启动 MongoDB..."
    
    # 创建数据目录
    mkdir -p ~/data/mongodb
    
    # 启动 MongoDB
    mongod --dbpath ~/data/mongodb --fork --logpath ~/data/mongodb/mongod.log
    
    if [ $? -eq 0 ]; then
        echo "✅ MongoDB 启动成功"
        echo "📊 数据库: infgetter_db"
        echo "🔗 连接: mongodb://localhost:27017"
    else
        echo "❌ MongoDB 启动失败"
        exit 1
    fi
fi

# 显示状态
echo ""
echo "📈 MongoDB 状态:"
mongosh --eval "db.stats()" --quiet 2>/dev/null || mongo --eval "db.stats()" --quiet 2>/dev/null || echo "无法获取状态"
