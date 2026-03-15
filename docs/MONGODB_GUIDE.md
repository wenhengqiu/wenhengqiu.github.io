# Info-Getter MongoDB 使用指南

## 概述

Info-Getter 现已支持 MongoDB 数据库存储，提供比 JSON 文件更强大的数据管理和查询能力。

## 特性

- ✅ 高性能数据存储和查询
- ✅ 自动去重（基于文章ID）
- ✅ 多维度索引（分类、质量分、时间、来源）
- ✅ 灵活的查询接口（分类、时间、关键词搜索）
- ✅ 实时统计分析
- ✅ 支持本地和云端部署

## 安装

### 1. 安装 MongoDB

**macOS:**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Ubuntu:**
```bash
sudo apt-get install mongodb
sudo systemctl start mongodb
```

**Docker (推荐):**
```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### 2. 安装 Python 依赖

```bash
pip install pymongo
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置 MongoDB 连接字符串
```

## 启动 MongoDB

```bash
# 使用脚本启动（本地开发）
./scripts/start_mongodb.sh

# 或使用 Docker
docker start mongodb
```

## 数据库结构

```
infgetter_db/
├── articles/          # 文章集合
│   ├── id (唯一索引)
│   ├── category (索引)
│   ├── quality_score (索引)
│   ├── published_at (索引)
│   └── source.name (索引)
├── sources/           # 信息源集合
│   └── id (唯一索引)
├── logs/              # 采集日志集合
│   └── timestamp (索引)
└── stats/             # 统计信息集合
```

## 使用示例

### 基础使用

```python
from info_getter.db import get_db

# 获取数据库实例
db = get_db()

# 保存单篇文章
db.save_article({
    "id": "article_001",
    "title": "OpenAI releases GPT-5",
    "title_zh": "OpenAI发布GPT-5",
    "category": "ai",
    "quality_score": 0.95,
    # ... 其他字段
})

# 批量保存文章
articles = [article1, article2, article3]
result = db.save_articles(articles)
print(f"新增: {result['success']}, 重复: {result['duplicates']}")
```

### 查询文章

```python
# 按分类获取文章
ai_articles = db.get_articles_by_category("ai", limit=50)

# 获取高质量文章（TOP10候选）
top_articles = db.get_top_articles(min_score=0.8, limit=10)

# 获取最近24小时的文章
recent = db.get_recent_articles(hours=24)

# 搜索文章
results = db.search_articles("GPT-5", limit=20)

# 根据ID获取文章
article = db.get_article_by_id("article_001")
```

### 统计分析

```python
# 获取统计信息
stats = db.get_statistics()
print(f"总文章数: {stats['total_articles']}")
print(f"今日新增: {stats['today_articles']}")
print(f"平均质量分: {stats['avg_quality_score']}")
print(f"分类统计: {stats['by_category']}")
```

### 信息源管理

```python
# 保存信息源
db.save_source({
    "id": "openai_blog",
    "name": "OpenAI Blog",
    "url": "https://openai.com/blog/rss.xml",
    "category": "ai",
    "priority": "p0"
})

# 获取信息源
sources = db.get_sources(category="ai", priority="p0")
```

### 日志记录

```python
# 记录采集日志
db.log_fetch(
    run_id="run_20260315_001",
    source_id="openai_blog",
    status="success",
    articles_count=5
)

# 获取日志
logs = db.get_logs(run_id="run_20260315_001")
```

## MongoDB Atlas 云端部署

### 1. 创建 Atlas 账户

访问 https://www.mongodb.com/cloud/atlas 注册免费账户

### 2. 创建集群

- 选择 Shared Cluster（免费）
- 选择最近的区域（如 AWS Singapore）

### 3. 配置连接

```bash
# 在 .env 文件中配置
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
```

### 4. 连接测试

```python
from info_getter.db import get_db

db = get_db("mongodb+srv://user:pass@cluster.mongodb.net")
print(db.get_statistics())
```

## 数据备份

```bash
# 导出数据
mongodump --db infgetter_db --out ./backup/$(date +%Y%m%d)

# 导入数据
mongorestore --db infgetter_db ./backup/20260315/infgetter_db
```

## 监控命令

```bash
# 查看数据库状态
mongosh infgetter_db --eval "db.stats()"

# 查看集合统计
mongosh infgetter_db --eval "db.articles.stats()"

# 查看文章数量
mongosh infgetter_db --eval "db.articles.countDocuments()"

# 查看最近文章
mongosh infgetter_db --eval "db.articles.find().sort({published_at: -1}).limit(5)"
```

## 故障排查

### 连接失败

```
检查 MongoDB 是否运行: pgrep -x mongod
检查端口: lsof -i :27017
检查防火墙: sudo ufw status
```

### 权限错误

```bash
# 创建用户
mongosh infgetter_db
db.createUser({
    user: "infgetter",
    pwd: "password",
    roles: [{role: "readWrite", db: "infgetter_db"}]
})
```

## 性能优化

- 已创建复合索引优化查询性能
- 使用 upsert 避免重复插入
- 批量操作减少数据库往返
- 连接池自动管理

## 注意事项

1. MongoDB 是可选功能，JSON 文件保存仍然保留
2. 如果 MongoDB 连接失败，会自动降级到仅 JSON 模式
3. 定期备份重要数据
4. 生产环境建议使用 MongoDB Atlas 或副本集部署
