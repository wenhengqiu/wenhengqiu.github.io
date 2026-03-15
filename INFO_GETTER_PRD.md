# Info-Getter v2.0 产品需求文档 (PRD)

## 1. 产品概述

### 1.1 产品定位
Info-Getter是一款自动化AI行业资讯采集系统，专为数据闭环文章中心提供高质量、结构化的行业内容。

### 1.2 核心目标
- **自动化**: 零人工干预，24小时自动运行
- **高质量**: 智能筛选，只保留优质内容
- **结构化**: 统一元信息格式，便于前端展示
- **多语言**: 自动翻译，中英双语支持

---

## 2. 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    Info-Getter v2.0                      │
├─────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│  │ Fetcher │→ │Translator│→ │ Scorer  │→ │Publisher│   │
│  │  采集器  │  │  翻译器  │  │ 评分器  │  │  发布器  │   │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘   │
├─────────────────────────────────────────────────────────┤
│                    Scheduler 调度器                      │
├─────────────────────────────────────────────────────────┤
│              Data Storage 数据存储层                     │
│         (JSON文件 + Git版本控制 + GitHub Pages)          │
└─────────────────────────────────────────────────────────┘
```

---

## 3. 功能模块

### 3.1 Fetcher 采集器

#### 3.1.1 采集流程与逻辑

```
┌─────────────────────────────────────────────────────────────┐
│                     Fetcher 采集流程                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  加载配置    │───→│  分批采集    │───→│  内容解析    │     │
│  │  sources.yml│    │  10个/批次   │    │  RSS/Web/API │     │
│  └─────────────┘    └──────┬──────┘    └──────┬──────┘     │
│                            │                    │           │
│                            ▼                    ▼           │
│                     ┌─────────────┐    ┌─────────────┐     │
│                     │  关键词匹配  │───→│  相关性筛选  │     │
│                     │  标题+摘要   │    │  质量>0.6   │     │
│                     └─────────────┘    └──────┬──────┘     │
│                                               │            │
│                                               ▼            │
│                                        ┌─────────────┐     │
│                                        │  输出原始文章 │     │
│                                        │  RawArticle  │     │
│                                        └─────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### 3.1.2 关键词匹配规则

每个分类有对应的关键词库，用于判断文章相关性：

| 分类 | 关键词示例 | 匹配规则 |
|------|-----------|----------|
| **ai** | GPT、LLM、大模型、Claude、Gemini、Transformer、OpenAI、DeepMind | 标题或摘要包含任意关键词 |
| **robotics** | 人形机器人、具身智能、Embodied AI、Figure AI、Optimus、波士顿动力 | 标题或摘要包含任意关键词 |
| **autonomous** | FSD、自动驾驶、ADAS、NOA、智驾、Tesla、Waymo、华为ADS | 标题或摘要包含任意关键词 |
| **zhuoyu** | 卓驭、成行平台、大疆车载、双目视觉、沈劭劼 | 标题或摘要包含任意关键词 |

**匹配算法**:
```python
def match_category(article, category_keywords):
    """
    判断文章是否属于某个分类
    
    规则:
    1. 标题匹配权重: 70%
    2. 摘要匹配权重: 30%
    3. 任一关键词匹配即算命中
    4. 多分类命中时，取匹配度最高的分类
    """
    title_score = sum(1 for kw in category_keywords if kw in article.title) * 0.7
    summary_score = sum(1 for kw in category_keywords if kw in article.summary) * 0.3
    return title_score + summary_score
```

#### 3.1.3 相关性筛选标准

文章必须通过以下筛选才能进入后续流程：

| 筛选项 | 条件 | 处理方式 |
|--------|------|----------|
| **分类匹配** | 必须匹配至少一个分类的关键词 | 不匹配则丢弃 |
| **质量初筛** | 标题长度>10字，摘要长度>30字 | 不满足则丢弃 |
| **时效性** | 发布时间在7天内 | 过期文章丢弃 |
| **去重** | SimHash相似度<0.85 | 相似文章丢弃 |
| **语言检测** | 支持中英文 | 其他语言暂不支持 |

#### 3.1.4 信息源配置 (52个源)

**P0 官方博客 (12个)**
| ID | 名称 | 分类 | 类型 | 语言 |
|----|------|------|------|------|
| openai_blog | OpenAI Blog | llm | rss | en |
| deepmind_blog | DeepMind Blog | llm | web | en |
| anthropic_blog | Anthropic | llm | web | en |
| meta_ai_blog | Meta AI | llm | rss | en |
| tesla_blog | Tesla Blog | autonomous | rss | en |
| waymo_blog | Waymo Blog | autonomous | rss | en |
| huawei_auto | 华为智能汽车 | autonomous | rss | zh |
| xiaopeng | 小鹏汽车 | autonomous | rss | zh |
| baidu_apollo | 百度 Apollo | autonomous | rss | zh |
| figure_ai | Figure AI | robotics | web | en |
| boston_dynamics | Boston Dynamics | robotics | rss | en |
| nvidia_blog | NVIDIA Blog | llm | rss | en |

**P1 科技媒体 (25个)**
| ID | 名称 | 分类 | 类型 | 语言 |
|----|------|------|------|------|
| qbitai | 量子位 | general | rss | zh |
| jiqizhixin | 机器之心 | general | rss | zh |
| synced | Synced | llm | rss | en |
| the_verge_ai | The Verge AI | general | rss | en |
| techcrunch_ai | TechCrunch AI | general | rss | en |
| arxiv_ai | arXiv AI | llm | rss | en |
| mit_tech_review | MIT Tech Review | general | rss | en |
| ieee_spectrum | IEEE Spectrum | robotics | rss | en |
| wired_ai | Wired AI | general | rss | en |
| venturebeat_ai | VentureBeat AI | general | rss | en |
| zaker_ai | ZAKER AI | general | rss | zh |
| sina_tech | 新浪科技 | general | rss | zh |
| 36kr_ai | 36氪 AI | general | rss | zh |
| pingwest | PingWest | general | rss | zh |
| tmtpost | 钛媒体 | general | rss | zh |
| cyzone | 创业邦 | general | rss | zh |
| iheima | i黑马 | general | rss | zh |
| leiphone | 雷锋网 | general | rss | zh |
| cnbeta | cnBeta | general | rss | zh |
| solidot | Solidot | general | rss | zh |
| ifanr | 爱范儿 | general | rss | zh |
| donews | DoNews | general | rss | zh |
| techweb | TechWeb | general | rss | zh |
| chinaunix | ChinaUnix | general | rss | zh |
| oschina | 开源中国 | general | rss | zh |

**P2 社区/论文 (14个)**
| ID | 名称 | 分类 | 类型 | 语言 |
|----|------|------|------|------|
| hackernews | Hacker News | general | api | en |
| reddit_ml | Reddit r/MachineLearning | llm | api | en |
| reddit_selfdriving | Reddit r/SelfDrivingCars | autonomous | api | en |
| reddit_robotics | Reddit r/robotics | robotics | api | en |
| twitter_ai | Twitter AI List | llm | api | en |
| papers_with_code | Papers with Code | llm | rss | en |
| arxiv_cs | arXiv CS | llm | rss | en |
| distill_pub | Distill.pub | llm | rss | en |
| openreview | OpenReview | llm | rss | en |
| github_trending | GitHub Trending | general | api | en |
| producthunt | Product Hunt | general | rss | en |
| lobsters | Lobsters | general | rss | en |
| slashdot | Slashdot | general | rss | en |
| phoronix | Phoronix | general | rss | en |

#### 3.1.2 采集策略
- **批次控制**: 每批最多12个源，批次间延迟2秒
- **重试机制**: 失败重试3次，指数退避
- **去重策略**: URL + 标题 SimHash 去重
- **更新频率**: 每小时检查一次

#### 3.1.3 原始数据格式
```python
@dataclass
class RawArticle:
    title: str           # 原文标题
    url: str            # 原文链接
    source_id: str      # 来源ID
    source_name: str    # 来源名称
    published_at: datetime  # 发布时间
    summary: str        # 原文摘要（可选）
    content: str        # 原文内容（可选）
    author: str         # 作者（可选）
```

---

### 3.2 Translator 翻译器

#### 3.2.1 翻译策略
- **标题翻译**: 控制在20字以内
- **摘要翻译**: 控制在100字以内
- **专有名词保护**: GPT、OpenAI、Tesla等不翻译
- **降级策略**: 翻译失败保留原文

#### 3.2.2 翻译模型
- **主模型**: moonshot/kimi-k2.5
- **备用模型**: 本地Ollama（离线场景）
- **API调用**: 通过OpenClaw Gateway

#### 3.2.3 翻译输出
```python
@dataclass
class TranslationResult:
    title_zh: str       # 中文标题
    summary_zh: str     # 中文摘要
    success: bool       # 是否成功
    error_message: str  # 错误信息（如果失败）
```

---

### 3.3 Scorer 评分器 (行业价值导向)

#### 3.3.1 质量评分维度 (优化版)

| 维度 | 权重 | 说明 | 评分重点 |
|------|------|------|----------|
| **行业相关性** | 25% | 关键词匹配度 | 分类关键词命中数量 |
| **信息价值** | 25% | 技术/产品/融资 | 突破(+0.3)、发布(+0.25)、融资(+0.2) |
| **来源权威性** | 20% | 官方>顶级媒体>知名媒体 | 官方博客(1.0)、顶级媒体(0.9)、知名中文(0.8) |
| **时效性** | 15% | 24小时内最高 | 24h(1.0)、48h(0.9)、72h(0.8) |
| **内容质量** | 15% | 标题/摘要/完整性 | 标题适中、摘要详细、元数据完整 |

#### 3.3.2 行业关键词库

```python
INDUSTRY_KEYWORDS = {
    'ai': ['GPT', 'LLM', '大模型', 'Claude', 'Gemini', 'Transformer', 
           'OpenAI', 'DeepMind', 'Anthropic', 'AGI', '多模态', '推理'],
    
    'robotics': ['人形机器人', '具身智能', 'Figure AI', 'Optimus', 
                '宇树', '智元', '波士顿动力', '灵巧手', '运动控制'],
    
    'autonomous': ['FSD', '自动驾驶', 'NOA', '城市NOA', '端到端', 
                  '感知', '决策', '规控', '激光雷达', '纯视觉'],
    
    'zhuoyu': ['卓驭', '成行平台', '大疆车载', '双目视觉', 
              '沈劭劼', '中算力', '7V', '10V']
}
```

#### 3.3.3 信息价值加分项

| 类型 | 关键词 | 加分 |
|------|--------|------|
| **技术突破** | 突破、首次、创新、里程碑、SOTA、新架构、性能提升 | +0.3 |
| **产品发布** | 发布、推出、量产、交付、升级、v2/v3、正式上线 | +0.25 |
| **融资合作** | 融资、估值、投资、战略合作、签约、亿元、独角兽 | +0.2 |
| **数据评测** | 测试、评测、对比、报告、调研、市场份额 | +0.15 |
| **具体数字** | 版本号、数据指标、百分比 | +0.1 |

#### 3.3.4 来源权威性评分

| 来源类型 | 示例 | 分数 |
|----------|------|------|
| **官方博客** | OpenAI、DeepMind、Tesla、Waymo、华为 | 1.0 |
| **顶级媒体** | MIT、IEEE、Nature、TechCrunch、The Verge | 0.9 |
| **知名中文** | 机器之心、量子位、新智元、品玩、36氪 | 0.8 |
| **普通媒体** | 一般科技媒体 | 0.6 |
| **社区/个人** | Reddit、个人博客 | 0.4 |

#### 3.3.5 评分算法

```python
def calculate_quality_score(article):
    """
    行业价值导向的质量评分
    """
    scores = [
        (relevance_score, 0.25),      # 行业相关性 25%
        (information_value_score, 0.25),  # 信息价值 25%
        (authority_score, 0.20),      # 来源权威性 20%
        (freshness_score, 0.15),      # 时效性 15%
        (content_quality_score, 0.15), # 内容质量 15%
    ]
    
    # 加权平均
    weighted_score = sum(s * w for s, w in scores)
    return round(weighted_score, 3)
```

#### 3.3.6 阈值控制

| 阈值 | 分数 | 处理 |
|------|------|------|
| **发布阈值** | ≥0.6 | 发布到网站 |
| **精选阈值** | ≥0.8 | 进入TOP10候选 |
| **低质量过滤** | <0.6 | 直接丢弃 |

---

### 3.4 数据处理流程

#### 3.4.1 完整数据处理流水线

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Info-Getter 数据处理流水线                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  输入: 原始文章 (RawArticle)                                         │
│     │                                                               │
│     ▼                                                               │
│  ┌─────────────────┐                                                │
│  │  1. 分类识别     │ ← 关键词匹配算法                               │
│  │  Category Classifier                                              │
│  └────────┬────────┘                                                │
│           │ 输出: category (ai/robotics/autonomous/zhuoyu)           │
│           ▼                                                         │
│  ┌─────────────────┐                                                │
│  │  2. 智能翻译     │ ← OpenClaw API (moonshot/kimi-k2.5)            │
│  │  Translator                                                       │
│  └────────┬────────┘                                                │
│           │ 输出: title_zh, summary_zh                               │
│           ▼                                                         │
│  ┌─────────────────┐                                                │
│  │  3. 质量评分     │ ← 多维度评分算法                               │
│  │  Quality Scorer                                                   │
│  └────────┬────────┘                                                │
│           │ 输出: quality_score (0-1)                                │
│           ▼                                                         │
│  ┌─────────────────┐                                                │
│  │  4. 格式转换     │ ← 转换为PRD v6.1标准格式                        │
│  │  Format Converter                                                 │
│  └────────┬────────┘                                                │
│           │ 输出: 标准Article对象                                     │
│           ▼                                                         │
│  ┌─────────────────┐                                                │
│  │  5. 质量过滤     │ ← quality_score >= 0.6                         │
│  │  Quality Filter                                                   │
│  └────────┬────────┘                                                │
│           │ 不满足则丢弃                                              │
│           ▼                                                         │
│  ┌─────────────────┐                                                │
│  │  6. 去重检查     │ ← SimHash相似度检查                             │
│  │  Deduplication                                                    │
│  └────────┬────────┘                                                │
│           │ 相似度>=0.85则丢弃                                        │
│           ▼                                                         │
│  ┌─────────────────┐                                                │
│  │  7. 数据存储     │ ← JSON文件 + Git提交                            │
│  │  Data Persistence                                                 │
│  └────────┬────────┘                                                │
│           │                                                         │
│           ▼                                                         │
│  输出: 符合PRD v6.1标准的结构化文章                                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

#### 3.4.2 数据格式转换规则

从原始文章到标准格式的转换映射：

| 原始字段 | 转换规则 | 标准字段 | 说明 |
|---------|---------|---------|------|
| title | 保留原文 | title | 英文/中文原文 |
| title | 翻译为中文 | title_zh | 20字以内 |
| summary | 保留原文 | summary | 英文/中文原文 |
| summary | 翻译为中文 | summary_zh | 100字以内 |
| url | 直接映射 | url | 原文链接 |
| source_name | 包装为对象 | source.name | 来源名称 |
| - | 推断类型 | source.type | official/tech_media/research/social |
| category | 分类识别结果 | category | ai/robotics/autonomous/zhuoyu |
| published_at | ISO 8601格式 | published_at | 发布时间 |
| quality_score | 质量评分结果 | quality_score | 0-1浮点数 |
| - | 固定值 | translated | true/false |
| - | 自动生成 | tags | 关键词提取 |

#### 3.4.3 输出格式 (PRD v6.1 标准)
```json
{
  "id": "openai_20260315_001",
  "title": "OpenAI releases GPT-4.5",
  "title_zh": "OpenAI发布GPT-4.5模型",
  "summary": "OpenAI announced the release of GPT-4.5...",
  "summary_zh": "OpenAI宣布发布GPT-4.5模型，具备更强的推理能力...",
  "url": "https://openai.com/blog/gpt-4-5",
  "source": {
    "name": "OpenAI Blog",
    "type": "official"
  },
  "category": "ai",
  "quality_score": 0.92,
  "published_at": "2026-03-15T10:30:00Z",
  "translated": true,
  "tags": ["GPT-4.5", "大模型", "OpenAI"]
}
```

#### 3.4.2 存储结构
```
data/articles/
├── research/
│   ├── llm.json          # AI/大模型文章
│   ├── autonomous.json   # 自动驾驶文章
│   ├── robotics.json     # 具身智能文章
│   └── zhuoyu.json       # 卓驭科技文章
└── daily/                # 按日期归档（可选）
    └── 2026/
        └── 03/
            └── 15.json
```

#### 3.4.3 Git集成
- **自动提交**: 每次采集后自动git commit
- **提交信息**: `[Info-Getter] 采集XX篇文章，更新于YYYY-MM-DD HH:MM`
- **冲突处理**: 自动rebase，保留本地修改

---

## 4. 调度器 (Scheduler)

### 4.1 运行模式
```bash
# 单次运行
python -m info_getter.scheduler --once

# 持续运行（默认每小时）
python -m info_getter.scheduler --interval 3600

# 调试模式
python -m info_getter.scheduler --once --verbose
```

### 4.2 调度策略
- **定时触发**: 每小时整点执行
- **失败重试**: 失败后5分钟重试，最多3次
- **并发控制**: 单实例运行，防止重复采集

### 4.3 状态监控
```json
{
  "last_run": "2026-03-15T10:00:00Z",
  "next_run": "2026-03-15T11:00:00Z",
  "total_articles": 1523,
  "today_articles": 12,
  "success_rate": 0.95,
  "status": "running"
}
```

---

## 5. 配置管理

### 5.1 配置文件
```yaml
# config/info_getter.yaml

# 采集配置
fetcher:
  batch_size: 12
  batch_delay: 2
  retry_count: 3
  timeout: 30

# 翻译配置
translator:
  model: "moonshot/kimi-k2.5"
  max_title_length: 20
  max_summary_length: 100
  fallback_to_original: true

# 评分配置
scorer:
  quality_threshold: 0.6
  featured_threshold: 0.8

# 发布配置
publisher:
  data_dir: "data/articles"
  auto_git: true
  max_articles_per_file: 1000

# 调度配置
scheduler:
  interval: 3600
  max_runtime: 300
```

### 5.2 环境变量
```bash
export OPENCLAW_API_KEY="sk-xxx"
export INFO_GETTER_LOG_LEVEL="INFO"
export INFO_GETTER_DATA_DIR="/path/to/data"
```

---

## 6. 监控与日志

### 6.1 日志级别
- **INFO**: 正常流程日志
- **WARNING**: 翻译失败、低质量文章过滤
- **ERROR**: 采集失败、发布失败
- **DEBUG**: 详细调试信息

### 6.2 关键指标与监控

#### 6.2.1 核心指标
| 指标 | 说明 | 告警阈值 | 采集频率 |
|------|------|----------|----------|
| 采集成功率 | 成功采集/总源数 | < 80% | 每小时 |
| 翻译成功率 | 成功翻译/总文章 | < 90% | 每小时 |
| 平均质量分 | 发布文章平均分 | < 0.7 | 每天 |
| 运行时长 | 单次采集耗时 | > 300s | 每次 |
| 文章增量 | 新增文章数 | = 0 (6h) | 每小时 |
| API调用次数 | 翻译API调用 | > 500/h | 每小时 |
| 磁盘使用率 | 数据目录大小 | > 90% | 每天 |
| 内存使用率 | 进程内存占用 | > 85% | 每5分钟 |

#### 6.2.2 监控Dashboard
```json
{
  "dashboard": {
    "title": "Info-Getter 监控面板",
    "refresh": "60s",
    "panels": [
      {
        "title": "文章采集趋势",
        "type": "line",
        "metrics": ["articles_fetched", "articles_published"],
        "time_range": "24h"
      },
      {
        "title": "成功率",
        "type": "gauge",
        "metrics": ["fetch_success_rate", "translate_success_rate"],
        "thresholds": [0.8, 0.9, 0.95]
      },
      {
        "title": "质量分布",
        "type": "histogram",
        "metrics": ["quality_score_distribution"],
        "buckets": [0.6, 0.7, 0.8, 0.9, 1.0]
      },
      {
        "title": "来源分布",
        "type": "pie",
        "metrics": ["articles_by_source"]
      },
      {
        "title": "分类分布",
        "type": "bar",
        "metrics": ["articles_by_category"]
      }
    ]
  }
}
```

#### 6.2.3 健康检查端点
```bash
# 健康检查
GET /health

# 返回
{
  "status": "healthy",
  "version": "2.0.0",
  "uptime": "72h15m",
  "checks": {
    "fetcher": "ok",
    "translator": "ok",
    "publisher": "ok",
    "git": "ok",
    "disk": "ok"
  }
}

# 详细状态
GET /status

# 返回
{
  "daemon": {
    "status": "running",
    "pid": 3594,
    "started_at": "2026-03-15T00:00:00Z"
  },
  "last_run": {
    "time": "2026-03-15T10:00:00Z",
    "duration": 45.2,
    "fetched": 51,
    "published": 12
  },
  "statistics": {
    "total_articles": 1523,
    "today_articles": 45,
    "avg_quality_score": 0.78
  }
}
```

### 6.3 日志文件
```
logs/
├── info_getter.log       # 主日志
├── fetcher.log          # 采集日志
├── translator.log       # 翻译日志
├── scorer.log           # 评分日志
└── publisher.log        # 发布日志
```

---

## 7. 部署架构与运维

### 7.1 部署架构

#### 7.1.1 单机部署（当前）
```
┌─────────────────────────────────────────┐
│              Mac/Linux 主机              │
│  ┌─────────────────────────────────┐   │
│  │       Info-Getter Daemon        │   │
│  │  ┌─────────┐    ┌─────────────┐ │   │
│  │  │Scheduler│───→│  Fetcher    │ │   │
│  │  └────┬────┘    └─────────────┘ │   │
│  │       │              ↓          │   │
│  │       │         ┌─────────┐     │   │
│  │       │         │Translator│    │   │
│  │       │         └────┬────┘    │   │
│  │       │              ↓          │   │
│  │       │         ┌─────────┐     │   │
│  │       │         │  Scorer  │    │   │
│  │       │         └────┬────┘    │   │
│  │       │              ↓          │   │
│  │       │         ┌─────────┐     │   │
│  │       └────────→│ Publisher│    │   │
│  │                 └────┬────┘    │   │
│  │                      ↓          │   │
│  └─────────────────────────────────┘   │
│           ↓                             │
│  ┌─────────────────┐                   │
│  │  data/articles/ │                   │
│  │    (JSON文件)    │                   │
│  └────────┬────────┘                   │
│           ↓                             │
│  ┌─────────────────┐                   │
│  │   Git Commit    │                   │
│  └────────┬────────┘                   │
│           ↓                             │
│  ┌─────────────────┐                   │
│  │  GitHub Pages   │                   │
│  └─────────────────┘                   │
└─────────────────────────────────────────┘
```

#### 7.1.2 生产环境部署（推荐）
```
┌─────────────────────────────────────────┐
│           Docker Compose                │
│  ┌─────────────────────────────────┐   │
│  │     Info-Getter Container       │   │
│  │        (Python 3.11)            │   │
│  │  ┌─────────────────────────┐   │   │
│  │  │   Info-Getter Daemon    │   │   │
│  │  └─────────────────────────┘   │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │    Chrome Headless Container    │   │
│  │    (for Web scraping)           │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │      Redis Container            │   │
│  │   (Queue & Cache)               │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### 7.2 部署方式

#### 7.2.1 本地部署（开发）
```bash
# 1. 克隆仓库
git clone https://github.com/wenhengqiu/wenhengqiu.github.io.git
cd wenhengqiu.github.io

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入 OPENCLAW_API_KEY

# 5. 初始化目录
mkdir -p data/articles/research logs

# 6. 启动守护进程
./daemon.sh start
```

#### 7.2.2 Docker部署（生产）
```bash
# 1. 构建镜像
docker-compose build

# 2. 启动服务
docker-compose up -d

# 3. 查看日志
docker-compose logs -f info-getter

# 4. 停止服务
docker-compose down
```

#### 7.2.3 系统服务部署（Linux）
```bash
# 创建systemd服务
sudo tee /etc/systemd/system/info-getter.service << 'EOF'
[Unit]
Description=Info-Getter Daemon
After=network.target

[Service]
Type=simple
User=infogetter
WorkingDirectory=/opt/info-getter
Environment=OPENCLAW_API_KEY=sk-xxx
Environment=INFO_GETTER_LOG_LEVEL=INFO
ExecStart=/opt/info-getter/venv/bin/python -m info_getter.scheduler
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
sudo systemctl enable info-getter
sudo systemctl start info-getter
sudo systemctl status info-getter
```

### 7.2 守护进程管理
```bash
./daemon.sh start    # 启动
./daemon.sh stop     # 停止
./daemon.sh restart  # 重启
./daemon.sh status   # 查看状态
./daemon.sh logs     # 查看日志
```

### 7.3 故障处理与错误恢复

#### 7.3.1 故障分类与处理策略

| 故障类型 | 故障级别 | 自动处理 | 人工介入 |
|----------|----------|----------|----------|
| **采集失败** | 低 | 重试3次，记录失败 | 连续失败24小时 |
| **翻译失败** | 低 | 保留原文，标记状态 | 连续失败10次 |
| **评分异常** | 中 | 使用默认分数 | 质量分持续偏低 |
| **发布失败** | 中 | 自动rebase重试 | Git冲突无法解决 |
| **网络中断** | 高 | 等待恢复后重试 | 超过30分钟 |
| **API限流** | 中 | 指数退避重试 | 持续限流1小时 |
| **内存溢出** | 高 | 分批处理 | 频繁发生 |
| **磁盘满** | 高 | 停止采集 | 立即处理 |

#### 7.3.2 错误恢复流程

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   错误发生   │────→│  错误分类   │────→│  自动处理   │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                                │
                    ┌───────────────────────────┘
                    ▼
           ┌────────────────┐
           │  处理成功？     │
           └───────┬────────┘
                   │
         ┌────────┴────────┐
         ▼                 ▼
   ┌──────────┐      ┌──────────┐
   │   是     │      │   否     │
   └────┬─────┘      └────┬─────┘
        │                 │
        ▼                 ▼
   ┌──────────┐      ┌──────────┐
   │ 继续执行  │      │ 记录日志  │
   └──────────┘      └────┬─────┘
                          │
                          ▼
                   ┌──────────────┐
                   │ 发送告警通知  │
                   └──────┬───────┘
                          │
                          ▼
                   ┌──────────────┐
                   │ 等待人工处理  │
                   └──────────────┘
```

#### 7.3.3 告警通知机制

**通知渠道**:
- 日志文件: `logs/error.log`
- 状态页面: `/status.html`
- 飞书/钉钉: Webhook通知（可选配置）

**告警触发条件**:
```yaml
alerts:
  fetch_failure_rate:
    threshold: 0.20  # 采集失败率>20%
    window: 1h
    
  translate_failure_rate:
    threshold: 0.10  # 翻译失败率>10%
    window: 1h
    
  no_new_articles:
    threshold: 6h    # 6小时无新文章
    
  disk_usage:
    threshold: 0.90  # 磁盘使用率>90%
    
  memory_usage:
    threshold: 0.85  # 内存使用率>85%
```

#### 7.3.4 数据备份与恢复

**自动备份**:
```bash
# 每日凌晨备份
0 0 * * * tar -czf backup/articles-$(date +%Y%m%d).tar.gz data/articles/

# 保留最近7天备份
find backup/ -name "articles-*.tar.gz" -mtime +7 -delete
```

**灾难恢复**:
1. 从Git历史恢复: `git checkout <commit> -- data/articles/`
2. 从备份恢复: `tar -xzf backup/articles-20260315.tar.gz`
3. 重新采集: `./daemon.sh restart`

---

## 8. 版本规划

### 8.1 v2.0 (当前)
- [x] 基础采集、翻译、评分、发布
- [x] 支持RSS/API/Web三种源类型
- [x] 自动Git提交
- [x] 守护进程管理

### 8.2 v2.1 (计划中)
- [ ] 智能摘要生成（非翻译）
- [ ] 图片自动下载与压缩
- [ ] 情感分析标签
- [ ] 热点话题聚类

### 8.3 v2.2 (规划中)
- [ ] 多语言支持（日/韩/德）
- [ ] 视频内容提取
- [ ] 社交媒体监控
- [ ] 实时推送通知

---

## 9. 附录

### 9.1 分类映射表
| 分类ID | 中文名 | 说明 |
|--------|--------|------|
| ai | AI/大模型 | LLM、AGI、算法等 |
| autonomous | 自动驾驶 | 自动驾驶技术、政策等 |
| robotics | 具身智能 | 机器人、人形机器人等 |
| zhuoyu | 卓驭科技 | 卓驭相关产品/技术 |

### 9.2 来源类型
| 类型 | 说明 | 示例 |
|------|------|------|
| official | 官方博客/公告 | OpenAI Blog, Tesla |
| tech_media | 科技媒体 | 量子位, 机器之心 |
| research | 学术/研究 | arXiv, 论文 |
| social | 社交媒体 | Twitter/X, Reddit |

### 9.3 质量评分细则
详见 `docs/quality_scoring.md`

---

**文档版本**: v2.0  
**最后更新**: 2026-03-15  
**作者**: Info-Getter Team
