# 数据闭环文章中心 - 产品文档 v2.0

## 项目概述

**项目名称：** 数据闭环文章中心 (Data Loop Article Hub)  
**定位：** AI 行业资讯聚合与知识管理平台  
**目标用户：** 关注 AI、自动驾驶、具身智能领域的从业者、研究者、投资者  
**部署平台：** GitHub Pages  
**更新日期：** 2026-03-13

---

## 信息源体系 (Sources)

### 1. 科研论文 (Research Papers)

#### 顶级会议
- **CVPR** - IEEE/CVF Conference on Computer Vision and Pattern Recognition
- **ICCV** - International Conference on Computer Vision
- **ECCV** - European Conference on Computer Vision
- **NeurIPS** - Neural Information Processing Systems
- **ICML** - International Conference on Machine Learning
- **ICLR** - International Conference on Learning Representations
- **RSS** - Robotics: Science and Systems
- **CoRL** - Conference on Robot Learning

#### 论文平台
- **arXiv** (cs.AI, cs.CV, cs.RO, cs.LG)
- **Papers With Code**
- **OpenReview**
- **Semantic Scholar**

### 2. 官方发布 (Official Releases)

#### 大模型公司
- **OpenAI Blog** - https://openai.com/blog
- **Google AI Blog** - https://ai.googleblog.com
- **DeepMind Blog** - https://deepmind.google/discover/blog
- **Anthropic** - https://www.anthropic.com/news
- **Meta AI** - https://ai.meta.com/blog
- **Cohere** - https://cohere.com/blog
- **Stability AI** - https://stability.ai/news

#### 中国大模型
- **智谱 AI** - https://chatglm.cn
- **月之暗面** - https://kimi.moonshot.cn
- **MiniMax** - https://www.minimaxi.com
- **零一万物** - https://www.01.ai
- **百川智能** - https://www.baichuan-ai.com
- **阶跃星辰** - https://www.stepfun.com

#### 自动驾驶
- **Tesla AI** - https://www.tesla.com/AI
- **Waymo Blog** - https://waymo.com/blog
- **Cruise** - https://getcruise.com/news
- **小鹏汽车** - https://www.xiaopeng.com/news
- **华为智能汽车** - https://auto.huawei.com
- **百度 Apollo** - https://apollo.auto

#### 具身智能
- **Figure AI** - https://www.figure.ai/news
- **波士顿动力** - https://bostondynamics.com/news
- **特斯拉 Optimus** - https://www.tesla.com/optimus
- **宇树科技** - https://www.unitree.com
- **智元机器人** - https://www.zhiyuan-robot.com

### 3. 科技媒体 (Tech Media)

#### 国内
- **机器之心** - https://www.jiqizhixin.com
- **量子位** - https://www.qbitai.com
- **雷锋网** - https://www.leiphone.com
- **品玩** - https://www.pingwest.com
- **36氪** - https://36kr.com
- **极客公园** - https://www.geekpark.net
- **InfoQ** - https://www.infoq.cn

#### 国际
- **TechCrunch** - https://techcrunch.com/category/artificial-intelligence
- **The Verge** - https://www.theverge.com/ai-artificial-intelligence
- **MIT Technology Review** - https://www.technologyreview.com/topic/artificial-intelligence
- **VentureBeat** - https://venturebeat.com/ai
- **Wired** - https://www.wired.com/tag/artificial-intelligence
- **IEEE Spectrum** - https://spectrum.ieee.org/artificial-intelligence

### 4. 投资与创业 (Investment & Startup)

- **IT桔子** - https://www.itjuzi.com
- **企名片** - https://www.qimingpian.com
- **Crunchbase** - https://www.crunchbase.com/hub/artificial-intelligence-companies
- **PitchBook** - https://pitchbook.com/news/articles/ai-startups
- **动脉网** - https://www.vbdata.cn (AI医疗)

### 5. 开源社区 (Open Source)

- **GitHub Trending** - https://github.com/trending
- **Hugging Face** - https://huggingface.co/blog
- **Papers With Code** - https://paperswithcode.com
- **Reddit r/MachineLearning** - https://www.reddit.com/r/MachineLearning
- **Twitter/X AI Community**

### 6. 政策法规 (Policy & Regulation)

- **中国信通院** - http://www.caict.ac.cn
- **国家网信办** - http://www.cac.gov.cn
- **欧盟 AI Act** - https://artificial-intelligence-act.com
- **白宫 AI 政策** - https://www.whitehouse.gov/ai

---

## 文章采集与存储流程

### 采集流程

```
1. 定时扫描信息源 (每日 6:00 / 12:00 / 18:00)
   ├─ RSS 订阅
   ├─ API 接口
   ├─ 网页抓取
   └─ 人工精选

2. 内容处理
   ├─ 去重检测
   ├─ 分类打标
   ├─ 摘要生成
   └─ 质量评分

3. 人工审核
   ├─ 重要性评估
   ├─ 内容准确性
   └─ 精选标记

4. 数据存储
   ├─ 原始数据备份
   ├─ 结构化存储
   └─ 索引更新

5. 网站部署
   ├─ 生成静态文件
   ├─ 推送到 GitHub
   └─ 自动部署
```

### 数据存储结构

```
/data
  /articles
    /daily                    # 每日资讯
      /2026
        /03
          2026-03-13.json
          2026-03-12.json
    /research                 # 深度研究
      /autonomous             # 自动驾驶
        tesla-fsd.json
        waymo-approach.json
      /robotics               # 具身智能
        figure-ai-helix.json
        tesla-optimus.json
      /llm                    # 大模型
        gpt-4-architecture.json
        kimi-training.json
    /papers                   # 论文解读
      /2026
        03/
          rss-2026-03-13.json
  /sources                    # 信息源配置
    sources.json              # 信息源列表
    rss-feeds.json           # RSS订阅列表
  /stats                      # 统计数据
    daily-stats.json         # 每日统计
    source-stats.json        # 信息源统计
```

---

## 核心功能模块

### 模块 1：每日必读 (Daily Must-Read)

**功能描述：**
- 展示每天从多个信息源抓取的最新行业资讯
- 以新闻卡片形式呈现，支持快速浏览
- 支持按日期查看历史资讯

**数据字段：**
```json
{
  "id": "2026-03-13-001",
  "title": "文章标题",
  "summary": "文章摘要（200字以内）",
  "content": "完整内容或关键段落（HTML格式）",
  "source": {
    "name": "信息源名称",
    "type": "信息源类型 [paper|official|media|startup|opensource|policy]",
    "url": "信息源URL",
    "icon": "信息源图标"
  },
  "original_url": "原文链接",
  "publish_date": "2026-03-13",
  "display_date": "3月13日",
  "fetch_date": "2026-03-13T08:30:00Z",
  "category": "分类 [llm|autonomous|robotics|company|product|research|paper|investment]",
  "tags": ["标签数组"],
  "companies": ["相关公司"],
  "technologies": ["相关技术"],
  "importance": "重要程度 [high|medium|low]",
  "is_featured": true,
  "is_read": false,
  "read_count": 0
}
```

**UI 设计：**
- 顶部：日期选择器 + 今日统计 + 信息源筛选
- 主体：瀑布流/网格卡片布局
- 卡片元素：标题、摘要、标签、来源、时间、原文链接
- 交互：点击展开详情弹窗、分类筛选、关键词搜索

### 模块 2：数据闭环行业研究 (Industry Research)

**知识分类：**

#### 2.1 技术架构
- 数据采集技术
- 数据标注方法
- 模型训练框架
- 仿真与测试
- 部署与推理

#### 2.2 公司研究
- **自动驾驶：** Tesla、Waymo、小鹏、华为、百度、蔚来
- **具身智能：** Tesla Optimus、Figure AI、智元、宇树、波士顿动力
- **大模型：** OpenAI、Google、Meta、智谱、月之暗面、MiniMax

#### 2.3 论文解读
- 顶级会议论文
- 开源项目解读
- 技术趋势分析

#### 2.4 投资动态
- 融资新闻
- 并购事件
- 估值分析

### 模块 3：信息源管理 (Source Management)

**功能：**
- 信息源列表展示
- 信息源健康度监控
- 更新频率统计
- 内容质量评分

### 模块 4：收藏与笔记 (Bookmarks & Notes)

**功能：**
- 用户可收藏感兴趣的文章
- 支持添加个人笔记
- 生成个人阅读清单
- 导出收藏数据

### 模块 5：数据看板 (Dashboard)

**统计指标：**
- 总文章数
- 今日新增
- 分类占比
- 热门标签
- 活跃信息源
- 信息源覆盖度

---

## 技术架构

### 前端
- **框架：** 纯 HTML + CSS + JavaScript
- **样式：** CSS Grid + Flexbox 响应式布局
- **图标：** SVG 内联图标
- **存储：** localStorage (用户数据)

### 数据更新流程

```bash
# 1. 采集数据
node scripts/fetch-news.js

# 2. 处理数据
node scripts/process-articles.js

# 3. 生成静态文件
node scripts/generate-static.js

# 4. 提交到 GitHub
git add .
git commit -m "Update daily news: $(date +%Y-%m-%d)"
git push origin main

# 5. GitHub Pages 自动部署
```

---

## 使用说明

### 对于内容维护者

**每日更新流程：**
1. 运行采集脚本获取最新资讯
2. 审核并编辑文章数据
3. 提交到 GitHub
4. 等待自动部署

**添加新信息源：**
1. 编辑 `data/sources/sources.json`
2. 添加信息源配置
3. 更新采集脚本

### 对于用户

1. 访问网站浏览最新资讯
2. 使用分类筛选感兴趣的内容
3. 搜索关键词查找文章
4. 收藏文章（浏览器本地存储）
5. 点击原文链接查看完整内容

---

## 未来扩展

- [ ] RSS 订阅支持
- [ ] 邮件订阅推送
- [ ] 微信公众号同步
- [ ] API 接口开放
- [ ] 用户评论系统
- [ ] 多语言支持
- [ ] AI 自动生成摘要
- [ ] 智能推荐系统

---

**文档版本：** v2.0  
**创建日期：** 2026-03-13  
**作者：** OpenClaw
