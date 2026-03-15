# AI Big News 产品需求文档 (PRD)

## 1. 产品概述

### 1.1 产品名称
**AI Big News** - 每日AI圈大事总结

### 1.2 产品定位
每天早上9点自动推送前一天AI行业重要资讯，涵盖人工智能、自动驾驶、具身智能三大领域。

### 1.3 核心价值
- **省时**: 3分钟了解AI圈昨日大事
- **全面**: 覆盖AI、自动驾驶、具身智能三大赛道
- **智能**: AI自动筛选、总结、生成报告
- **准时**: 每天早上9点准时推送

## 2. 功能需求

### 2.1 核心功能

#### 2.1.1 数据采集
- **时间范围**: 前一天0:00-23:59发布的文章
- **数据来源**: Info-Getter已采集的文章库
- **筛选条件**: 
  - 质量分 ≥ 0.7
  - 分类: llm / autonomous / robotics
  - 去重: 相似度 < 0.8

#### 2.1.2 智能总结
- **分类汇总**: 按三大领域分别总结
- **TOP5精选**: 每个领域精选5篇最重要文章
- **一句话摘要**: 每篇文章一句话核心要点
- **今日热点**: 提取3个昨日最热话题

#### 2.1.3 报告生成
- **格式**: Markdown
- **结构**:
  ```
  # AI Big News - 2026年3月15日
  
  ## 📊 昨日概览
  - 总文章数: XX篇
  - 人工智能: XX篇
  - 自动驾驶: XX篇  
  - 具身智能: XX篇
  
  ## 🔥 今日热点
  1. [热点1]: 一句话描述
  2. [热点2]: 一句话描述
  3. [热点3]: 一句话描述
  
  ## 🤖 人工智能 TOP5
  1. [标题] - [来源]
    - 一句话摘要
    - [阅读原文]
  
  ## 🚗 自动驾驶 TOP5
  ...
  
  ## 🤖 具身智能 TOP5
  ...
  
  ## 📈 趋势洞察
  - 昨日行业整体趋势分析
  - 值得关注的技术/产品/公司
  
  ---
  由 Info-Getter + AI Big News 自动生成
  更新时间: 2026-03-15 09:00
  ```

#### 2.1.4 推送渠道
- **主渠道**: 飞书消息 (用户当前渠道)
- **备用渠道**: 邮件订阅 (可选)
- **存储**: 保存到网站 /daily/YYYY-MM-DD.md

### 2.2 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                     AI Big News                         │
├─────────────────────────────────────────────────────────┤
│  Scheduler (每天9:00触发)                                │
│       ↓                                                 │
│  Data Collector (读取昨日文章)                           │
│       ↓                                                 │
│  Article Filter (质量分≥0.7, 去重)                       │
│       ↓                                                 │
│  AI Summarizer (生成摘要、热点、趋势)                     │
│       ↓                                                 │
│  Report Generator (生成Markdown报告)                     │
│       ↓                                                 │
│  Publisher (推送到飞书 + 保存到网站)                      │
└─────────────────────────────────────────────────────────┘
```

## 3. 详细设计

### 3.1 模块设计

#### 3.1.1 Data Collector
```python
class DataCollector:
    """数据采集器"""
    
    def collect_yesterday_articles(self) -> List[Article]:
        """采集前一天的文章"""
        yesterday = datetime.now() - timedelta(days=1)
        
        articles = []
        for category in ['llm', 'autonomous', 'robotics']:
            file_path = f"data/articles/research/{category}.json"
            category_articles = self._load_and_filter(file_path, yesterday)
            articles.extend(category_articles)
        
        return articles
```

#### 3.1.2 Article Filter
```python
class ArticleFilter:
    """文章过滤器"""
    
    def filter(self, articles: List[Article]) -> List[Article]:
        """筛选高质量文章"""
        # 1. 质量分过滤
        filtered = [a for a in articles if a.quality_score >= 0.7]
        
        # 2. 去重
        filtered = self._deduplicate(filtered)
        
        # 3. 排序 (按质量分+时间)
        filtered.sort(key=lambda x: (x.quality_score, x.published_at), reverse=True)
        
        return filtered
```

#### 3.1.3 AI Summarizer
```python
class AISummarizer:
    """AI总结器"""
    
    def summarize(self, articles: List[Article]) -> SummaryReport:
        """生成总结报告"""
        report = SummaryReport()
        
        # 1. 分类统计
        report.stats = self._calculate_stats(articles)
        
        # 2. TOP5精选
        report.top5 = self._select_top5(articles)
        
        # 3. 热点提取
        report.hot_topics = self._extract_hot_topics(articles)
        
        # 4. 趋势分析
        report.trends = self._analyze_trends(articles)
        
        return report
```

#### 3.1.4 Report Generator
```python
class ReportGenerator:
    """报告生成器"""
    
    def generate(self, summary: SummaryReport) -> str:
        """生成Markdown报告"""
        template = self._load_template()
        
        markdown = template.format(
            date=summary.date,
            stats=summary.stats,
            hot_topics=summary.hot_topics,
            top5_llm=summary.top5['llm'],
            top5_autonomous=summary.top5['autonomous'],
            top5_robotics=summary.top5['robotics'],
            trends=summary.trends
        )
        
        return markdown
```

### 3.2 定时任务

```yaml
# cron配置
ai_big_news:
  schedule: "0 9 * * *"  # 每天9:00
  timezone: "Asia/Shanghai"
  command: "python3 scripts/ai_big_news.py"
```

## 4. 数据格式

### 4.1 文章数据结构
```json
{
  "id": "article_001",
  "title": "文章标题",
  "title_zh": "中文标题",
  "summary": "摘要",
  "summary_zh": "中文摘要",
  "url": "https://example.com/article",
  "source": {"name": "来源", "type": "tech_media"},
  "category": "llm",
  "quality_score": 0.85,
  "published_at": "2026-03-14T10:00:00",
  "translated": true
}
```

### 4.2 报告数据结构
```json
{
  "date": "2026-03-15",
  "generated_at": "2026-03-15T09:00:00",
  "stats": {
    "total": 50,
    "llm": 20,
    "autonomous": 15,
    "robotics": 15
  },
  "hot_topics": [
    {"topic": "GPT-5发布", "mentions": 12},
    {"topic": "特斯拉FSD更新", "mentions": 8}
  ],
  "top_articles": {
    "llm": [...],
    "autonomous": [...],
    "robotics": [...]
  }
}
```

## 5. 界面设计

### 5.1 飞书消息格式
```
🌅 AI Big News - 3月15日

📊 昨日概览
━━━━━━━━━━━━━━━━
🤖 AI: 20篇 | 🚗 自驾: 15篇 | 🤖 具身: 15篇

🔥 今日热点
1️⃣ GPT-5即将发布 - OpenAI官方暗示
2️⃣ 特斯拉FSD V13推送 - 纯视觉方案再升级
3️⃣ Figure 02量产 - 人形机器人进入工厂

📰 人工智能 TOP3
• OpenAI发布GPT-4.5 Turbo - 推理能力提升40%
• Claude 4支持100万token上下文
• Google Gemini 2.0多模态能力增强

📰 自动驾驶 TOP3
• 特斯拉FSD V13北美全量推送
• Waymo在奥斯汀开始收费运营
• 小鹏XNGP新增50城

📰 具身智能 TOP3
• Figure 02开始量产交付
• 宇树G1价格降至16万
• 智元远征A2发布

📈 趋势洞察
昨日AI圈重点关注大模型推理能力提升，
自动驾驶端到端方案成为主流，人形机器人
开始从实验室走向工厂。

[查看完整报告] [订阅设置]
```

## 6. 实现计划

### 6.1 第一阶段 (MVP)
- [x] 产品文档 (PRD)
- [ ] 数据采集模块
- [ ] 文章筛选模块
- [ ] 报告生成模块
- [ ] 飞书推送模块
- [ ] 定时任务配置

### 6.2 第二阶段 (优化)
- [ ] AI智能摘要
- [ ] 热点话题提取
- [ ] 趋势分析
- [ ] 邮件订阅
- [ ] 历史报告存档

### 6.3 第三阶段 (高级)
- [ ] 个性化推荐
- [ ] 互动功能 (点赞、收藏)
- [ ] 数据可视化
- [ ] API开放

## 7. 成功指标

- **覆盖率**: 每日覆盖前一日≥80%的重要资讯
- **准时率**: 9:00准时推送率≥95%
- **满意度**: 用户满意度≥4.5/5
- **打开率**: 报告打开率≥70%

## 8. 附录

### 8.1 相关文件
- 代码: `scripts/ai_big_news.py`
- 模板: `templates/ai_big_news.md`
- 配置: `config/ai_big_news.yaml`

### 8.2 依赖服务
- Info-Getter (文章数据源)
- OpenClaw (定时任务、消息推送)
- GitHub Pages (报告存储)

---

**版本**: v1.0
**创建日期**: 2026-03-15
**作者**: Info-Getter Team
