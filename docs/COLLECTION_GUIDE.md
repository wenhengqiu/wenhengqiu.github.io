# 数据闭环文章中心 - 信息源采集指南

## 快速开始

### 1. 安装依赖

```bash
cd /Users/jarvis/.openclaw/workspace/dataloop-website
npm install xml2js
```

### 2. 运行采集脚本

```bash
# 采集今日资讯
node scripts/fetch-news.js

# 采集指定日期
node scripts/fetch-news.js --date=2026-03-13

# 采集指定信息源
node scripts/fetch-news.js --source=arxiv
```

### 3. 提交更新

```bash
git add data/articles/
git commit -m "Update daily news: $(date +%Y-%m-%d)"
git push origin main
```

---

## 信息源分类

### 📄 科研论文
- arXiv (cs.AI, cs.CV, cs.RO, cs.LG)
- Papers With Code
- OpenReview

### 🏢 官方发布
- OpenAI Blog
- Google AI Blog
- DeepMind Blog
- Anthropic
- Meta AI
- Tesla AI
- Waymo Blog
- Figure AI

### 📰 科技媒体
- 机器之心
- 量子位
- 雷锋网
- 品玩
- 36氪
- TechCrunch AI
- MIT Technology Review

### 💰 投资创业
- IT桔子
- Crunchbase AI

### 🌟 开源社区
- Hugging Face Blog
- GitHub Trending

### ⚖️ 政策法规
- 中国信通院

---

## 手动添加文章

当自动采集无法满足需求时，可以手动添加文章：

1. 编辑 `data/articles/daily/YYYY/MM/YYYY-MM-DD.json`
2. 按以下格式添加文章：

```json
{
  "id": "2026-03-13-001",
  "title": "文章标题",
  "summary": "文章摘要（200字以内）",
  "content": "HTML格式的完整内容",
  "source": {
    "name": "信息源名称",
    "type": "信息源类型",
    "url": "信息源URL"
  },
  "original_url": "原文链接",
  "publish_date": "2026-03-13",
  "display_date": "3月13日",
  "category": "llm",
  "tags": ["OpenAI", "GPT", "大模型"],
  "companies": ["OpenAI"],
  "technologies": ["GPT-5", "LLM"],
  "importance": "high",
  "is_featured": true
}
```

---

## 文章分类说明

| 分类 | 说明 | 示例 |
|------|------|------|
| llm | 大语言模型 | GPT、Claude、Kimi |
| autonomous | 自动驾驶 | FSD、Waymo、小鹏 |
| robotics | 具身智能 | Figure AI、Optimus |
| company | 公司动态 | 融资、人事变动 |
| product | 产品发布 | 新品上线、更新 |
| research | 技术研究 | 论文、算法 |
| investment | 投资动态 | 融资、并购 |
| policy | 政策法规 | AI监管、标准 |

---

## 更新频率建议

| 信息源类型 | 更新频率 | 建议采集时间 |
|-----------|---------|-------------|
| 科研论文 | 每日 | 08:00 |
| 官方发布 | 每日 | 09:00, 18:00 |
| 科技媒体 | 每日 | 08:00, 12:00, 18:00 |
| 投资创业 | 每日 | 10:00 |
| 开源社区 | 每日 | 20:00 |
| 政策法规 | 每周 | 周一 10:00 |

---

## 自动化部署

### 使用 GitHub Actions

创建 `.github/workflows/update-news.yml`:

```yaml
name: Update Daily News

on:
  schedule:
    - cron: '0 8,12,18 * * *'  # 每天 8:00, 12:00, 18:00 UTC
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm install xml2js
      
      - name: Fetch news
        run: node scripts/fetch-news.js
      
      - name: Commit and push
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add data/articles/
          git diff --staged --quiet || git commit -m "Update daily news: $(date +%Y-%m-%d)"
          git push
```

---

## 数据备份

文章数据存储在 `data/articles/` 目录，建议定期备份：

```bash
# 备份到本地
cp -r data/articles ~/Backups/dataloop-articles-$(date +%Y%m%d)

# 或使用 git 标签
git tag -a "backup-$(date +%Y%m%d)" -m "Daily backup"
git push origin "backup-$(date +%Y%m%d)"
```

---

## 注意事项

1. **尊重版权**：只采集公开可访问的内容，遵守 robots.txt
2. **请求频率**：避免频繁请求，建议间隔 1 秒以上
3. **数据质量**：人工审核重要文章，确保准确性
4. **去重处理**：相同标题或内容的文章自动去重
5. **错误处理**：网络错误时重试，记录失败的信息源

---

**文档版本：** 1.0  
**更新日期：** 2026-03-13
