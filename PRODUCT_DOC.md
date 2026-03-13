# 数据闭环文章中心 - 产品文档 v3.0

## 项目概述

**项目名称：** 数据闭环文章中心 (Data Loop Article Hub)  
**定位：** AI 行业资讯聚合与知识管理平台  
**目标用户：** 关注 AI、自动驾驶、具身智能领域的从业者、研究者、投资者  
**部署平台：** GitHub Pages  
**更新日期：** 2026-03-13

---

## 当前核心数据概览

### 内容规模
| 模块 | 文章数量 | 时间范围 | 更新频率 |
|------|---------|---------|---------|
| 每日必读 | 按日更新 | 2025-08 至今 | 每日 3 次 |
| 自动驾驶研究 | 25+ 篇 | 2026-02 至今 | 实时更新 |
| 具身智能研究 | 15+ 篇 | 2026-02 至今 | 实时更新 |
| 大模型研究 | 15+ 篇 | 2026-02 至今 | 实时更新 |
| 卓驭科技专栏 | 9+ 篇 | 2025-08 至今 | 实时更新 |

### 信息源覆盖
- **官方来源：** 50+ 家企业官网和博客
- **科技媒体：** 20+ 家国内外科技媒体
- **学术会议：** 8 大顶级 AI/机器人会议
- **投资数据：** 10+ 家创投数据平台

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
- **卓驭科技** - https://www.zhuoyutech.com

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

### 采集流程 (含质量检测)

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

3. 质量检测节点 (新增)
   ├─ 【链接有效性检测】验证 original_url 可访问性
   ├─ 【内容完整性检测】检查必填字段是否完整
   ├─ 【格式规范检测】验证 JSON 格式和字段类型
   ├─ 【重复内容检测】避免同一文章多次录入
   └─ 【敏感信息检测】过滤不当内容

4. 人工审核
   ├─ 重要性评估
   ├─ 内容准确性
   └─ 精选标记

5. 数据存储
   ├─ 原始数据备份
   ├─ 结构化存储
   └─ 索引更新

6. 网站部署
   ├─ 生成静态文件
   ├─ 推送到 GitHub
   └─ 自动部署
```

### 质量检测脚本

```bash
# 运行质量检测
node scripts/quality-check.js

# 检测项目：
# - 链接可达性 (HTTP 状态码检查)
# - JSON 格式验证
# - 必填字段检查
# - 日期格式验证
# - 重复 ID 检测
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
          ...
        /02
          2026-02-28.json
          ...
    /research                 # 深度研究
      /autonomous             # 自动驾驶 (25+篇)
        autonomous.json
      /robotics               # 具身智能 (15+篇)
        robotics.json
      /llm                    # 大模型 (15+篇)
        llm.json
      /zhuoyu                 # 卓驭科技 (9+篇)
        zhuoyu.json
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
  /quality                    # 质量检测报告
    link-check-report.json   # 链接检测报告
    validation-report.json   # 数据验证报告
```

---

## 核心功能模块

### 模块 1：每日必读 (Daily Must-Read) - v3.0 升级

**功能描述：**
- 展示每天从多个信息源抓取的最新行业资讯
- 以新闻卡片形式呈现，支持快速浏览
- **【新增】支持按日期查看历史资讯**
- **【新增】日期导航器，快速切换日期**
- **【新增】历史数据缓存，提升加载速度**

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
  "read_count": 0,
  "link_status": "链接状态 [valid|invalid|unknown]"
}
```

**UI 设计 - 每日必读首页：**
```
┌─────────────────────────────────────────────────────────────┐
│  📰 每日必读                                    [日期选择器 ▼] │
│  2026年3月13日 星期五                                        │
├─────────────────────────────────────────────────────────────┤
│  📊 今日概览                                                  │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │  28篇   │ │  8篇    │ │  12篇   │ │  5篇    │           │
│  │ 总资讯  │ │ 大模型  │ │ 自动驾驶│ │ 具身智能│           │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
├─────────────────────────────────────────────────────────────┤
│  🔥 今日要点                                                  │
│  • OpenAI 发布 GPT-5.4 系列模型                              │
│  • 特斯拉 FSD V13 即将推送                                   │
│  • 华为乾崑 ADS 3.0 发布                                     │
├─────────────────────────────────────────────────────────────┤
│  📅 日期导航  [<] 3月12日  [今天]  [>]                       │
├─────────────────────────────────────────────────────────────┤
│  🔍 筛选: [全部] [大模型] [自动驾驶] [具身智能] [产品]       │
├─────────────────────────────────────────────────────────────┤
│  📰 资讯列表                                                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ [大模型] OpenAI 发布 GPT-5.4...              3月13日 │    │
│  │ 摘要: OpenAI 推出 GPT-5.4 及 GPT-5.4 Pro...         │    │
│  │ [OpenAI] 🔗阅读原文  ⭐收藏                        │    │
│  └─────────────────────────────────────────────────────┘    │
│  ...更多资讯                                                 │
└─────────────────────────────────────────────────────────────┘
```

**交互功能：**
- **日期选择器：** 日历组件选择任意日期，支持快捷键 (←/→ 切换日期)
- **日期导航：** 快速切换前一天/后一天，「今天」按钮返回最新
- **分类筛选：** 按大模型/自动驾驶/具身智能/产品等筛选
- **搜索：** 关键词搜索标题和摘要
- **收藏：** 点击星标收藏文章，本地存储
- **阅读原文：** 点击链接跳转原文，新标签页打开
- **键盘快捷键：**
  - `←` / `→` - 切换日期
  - `t` - 返回今天
  - `/` - 聚焦搜索框
  - `esc` - 关闭弹窗

**历史数据查看：**
- 支持查看 2025-08-01 至今的所有历史数据
- 日期选择器限制可选范围
- 无数据日期显示友好提示
- 历史数据支持分类筛选和搜索

---

### 模块 2：数据闭环行业研究 (Industry Research)

**知识分类：**

#### 2.1 技术架构
- 数据采集技术
- 数据标注方法
- 模型训练框架
- 仿真与测试
- 部署与推理

#### 2.2 公司研究
- **自动驾驶 (25+篇)：** Tesla、Waymo、小鹏、华为、百度、蔚来、卓驭科技
- **具身智能 (15+篇)：** Tesla Optimus、Figure AI、智元、宇树、波士顿动力
- **大模型 (15+篇)：** OpenAI、Google、Meta、智谱、月之暗面、MiniMax
- **卓驭科技专栏 (9+篇)：** 成行平台、双目视觉、大疆车载独立历程

#### 2.3 论文解读
- 顶级会议论文
- 开源项目解读
- 技术趋势分析

#### 2.4 投资动态
- 融资新闻
- 并购事件
- 估值分析

---

### 模块 3：信息源管理 (Source Management)

**功能：**
- 信息源列表展示
- 信息源健康度监控
- 更新频率统计
- 内容质量评分
- **【新增】链接有效性监控**

---

### 模块 4：收藏与笔记 (Bookmarks & Notes)

**功能：**
- 用户可收藏感兴趣的文章
- 支持添加个人笔记
- 生成个人阅读清单
- 导出收藏数据
- **【新增】收藏文章链接有效性检测**

---

### 模块 5：数据看板 (Dashboard)

**统计指标：**
- 总文章数
- 今日新增
- 分类占比
- 热门标签
- 活跃信息源
- 信息源覆盖度
- **【新增】链接健康度统计**
- **【新增】内容质量评分趋势**

---

## 技术架构

### 前端
- **框架：** 纯 HTML + CSS + JavaScript
- **样式：** CSS Grid + Flexbox 响应式布局
- **图标：** SVG 内联图标 + Emoji
- **存储：** localStorage (用户数据、阅读历史、收藏)
- **【新增】缓存策略：** SessionStorage 缓存历史数据，减少重复请求

### 数据更新流程

```bash
# 1. 采集数据
node scripts/fetch-news.js

# 2. 质量检测 (新增)
node scripts/quality-check.js
# - 检测链接有效性
# - 验证 JSON 格式
# - 检查必填字段

# 3. 处理数据
node scripts/process-articles.js

# 4. 生成静态文件
node scripts/generate-static.js

# 5. 提交到 GitHub
git add .
git commit -m "Update daily news: $(date +%Y-%m-%d)"
git push origin main

# 6. GitHub Pages 自动部署
```

### 质量检测脚本 (新增)

```javascript
// scripts/quality-check.js

const checks = {
  // 1. 链接有效性检测
  async checkLink(url) {
    try {
      const response = await fetch(url, { method: 'HEAD', timeout: 5000 });
      return { valid: response.ok, status: response.status };
    } catch (error) {
      return { valid: false, error: error.message };
    }
  },
  
  // 2. JSON 格式验证
  validateJSON(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      JSON.parse(content);
      return { valid: true };
    } catch (error) {
      return { valid: false, error: error.message };
    }
  },
  
  // 3. 必填字段检查
  checkRequiredFields(article) {
    const required = ['id', 'title', 'summary', 'original_url', 'publish_date'];
    const missing = required.filter(field => !article[field]);
    return { valid: missing.length === 0, missing };
  },
  
  // 4. 重复 ID 检测
  checkDuplicateIds(articles) {
    const ids = articles.map(a => a.id);
    const duplicates = ids.filter((id, index) => ids.indexOf(id) !== index);
    return { valid: duplicates.length === 0, duplicates };
  }
};
```

---

## 使用说明

### 对于内容维护者

**每日更新流程：**
1. 运行采集脚本获取最新资讯
2. **运行质量检测脚本验证数据** (新增)
3. 审核并编辑文章数据
4. 提交到 GitHub
5. 等待自动部署

**质量检测命令：**
```bash
# 完整质量检测
npm run quality-check

# 仅检测链接
npm run check-links

# 仅验证 JSON
npm run validate-json

# 生成检测报告
npm run quality-report
```

**添加新信息源：**
1. 编辑 `data/sources/sources.json`
2. 添加信息源配置
3. 更新采集脚本
4. **运行质量检测验证** (新增)

### 对于用户

**每日必读使用指南：**
1. 访问首页查看今日最新资讯
2. 使用日期选择器查看历史数据
3. 使用分类筛选关注特定领域
4. 点击星标收藏感兴趣的文章
5. 点击「阅读原文」查看完整内容
6. 使用键盘快捷键提升浏览效率

**历史数据查看：**
1. 点击日期选择器选择任意历史日期
2. 使用左右箭头快速切换日期
3. 点击「今天」返回最新资讯
4. 历史数据支持分类筛选和搜索

---

## 产品体验优化

### 性能优化
- **懒加载：** 图片和卡片滚动懒加载
- **数据缓存：** SessionStorage 缓存历史数据
- **增量更新：** 仅加载新增内容，减少数据传输
- **预加载：** 预加载相邻日期的数据

### 交互优化
- **键盘快捷键：** 支持键盘快速操作
- **手势支持：** 移动端支持左右滑动切换日期
- **加载状态：** 清晰的加载动画和进度提示
- **空状态：** 无数据时显示友好提示和操作引导

### 可访问性
- **语义化 HTML：** 使用正确的标签结构
- **ARIA 标签：** 为交互元素添加 ARIA 属性
- **键盘导航：** 所有功能支持键盘操作
- **高对比度：** 支持深色模式

---

## 未来扩展

- [x] **历史数据查看** - 已支持
- [x] **质量检测流程** - 已支持
- [x] **卓驭科技专栏** - 已支持
- [ ] RSS 订阅支持
- [ ] 邮件订阅推送
- [ ] 微信公众号同步
- [ ] API 接口开放
- [ ] 用户评论系统
- [ ] 多语言支持
- [ ] AI 自动生成摘要
- [ ] 智能推荐系统
- [ ] 文章链接自动巡检
- [ ] 用户阅读行为分析

---

## 更新日志

### v3.0 (2026-03-13)
- 新增卓驭科技专栏，9篇深度文章
- 每日必读支持历史数据查看
- 新增质量检测流程，确保链接有效性
- 优化产品体验，增加键盘快捷键
- 完善数据存储结构，支持质量报告

### v2.0 (2026-03-13)
- 新增具身智能和大模型研究模块
- 优化文章展示，支持链接跳转
- 完善分类体系

### v1.0 (2026-03-12)
- 项目初始化
- 每日必读功能上线
- 自动驾驶研究模块上线

---

**文档版本：** v3.0  
**创建日期：** 2026-03-13  
**作者：** OpenClaw
