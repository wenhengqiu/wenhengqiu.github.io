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

#### 3.1.1 信息源配置 (51个源)

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

### 3.3 Scorer 评分器

#### 3.3.1 质量评分维度
| 维度 | 权重 | 说明 |
|------|------|------|
| 来源权威性 | 30% | 官方>媒体>社区 |
| 内容时效性 | 25% | 24小时内最高分 |
| 标题质量 | 20% | 关键词、清晰度 |
| 内容完整性 | 15% | 摘要长度、信息量 |
| 技术深度 | 10% | 技术术语密度 |

#### 3.3.2 评分标准
```python
quality_score = (
    source_authority * 0.30 +
    freshness * 0.25 +
    title_quality * 0.20 +
    content_completeness * 0.15 +
    technical_depth * 0.10
)
```

#### 3.3.3 阈值控制
- **发布阈值**: quality_score ≥ 0.6
- **精选阈值**: quality_score ≥ 0.8 (进入TOP10候选)
- **低质量过滤**: quality_score < 0.6 直接丢弃

---

### 3.4 Publisher 发布器

#### 3.4.1 输出格式 (PRD v6.1 标准)
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
