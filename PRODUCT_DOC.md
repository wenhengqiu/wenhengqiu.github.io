# 数据闭环文章中心 - 产品文档

## 项目概述

**项目名称：** 数据闭环文章中心 (Data Loop Article Hub)  
**定位：** AI 行业资讯聚合与知识管理平台  
**目标用户：** 关注 AI、自动驾驶、具身智能领域的从业者、研究者、投资者  
**部署平台：** GitHub Pages

---

## 核心功能模块

### 模块 1：每日必读 (Daily Must-Read)

**功能描述：**
- 展示每天从多个信息源抓取的最新行业资讯
- 以新闻卡片形式呈现，支持快速浏览
- 支持按日期查看历史资讯

**信息源：**
- 国内：品玩、36氪、机器之心、量子位、雷锋网
- 国际：TechCrunch、The Verge、MIT Technology Review
- 官方：OpenAI Blog、Google AI Blog、各公司官方发布

**数据字段：**
```json
{
  "id": "唯一标识",
  "title": "文章标题",
  "summary": "文章摘要（200字以内）",
  "content": "完整内容或关键段落",
  "source": "信息源名称",
  "source_url": "原文链接",
  "publish_date": "发布日期",
  "category": "分类 [llm|autonomous|robotics|company|product|research]",
  "tags": ["标签数组"],
  "image": "封面图片URL（可选）",
  "is_featured": "是否精选",
  "read_count": "阅读次数（可选）"
}
```

**UI 设计：**
- 顶部：日期选择器 + 今日统计
- 主体：瀑布流/网格卡片布局
- 卡片元素：标题、摘要、标签、来源、时间、原文链接
- 交互：点击展开详情弹窗、分类筛选、关键词搜索

---

### 模块 2：数据闭环行业研究 (Industry Research)

**功能描述：**
- 结构化存储行业知识，形成知识库
- 按主题分类整理深度文章和研究报告
- 支持知识图谱式关联浏览

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

#### 2.3 行业报告
- 市场分析
- 技术趋势
- 投资动态
- 政策法规

**数据字段：**
```json
{
  "id": "唯一标识",
  "type": "类型 [article|report|company|technology]",
  "title": "标题",
  "abstract": "摘要",
  "content": "正文内容（Markdown格式）",
  "author": "作者",
  "source": "来源",
  "source_url": "原文链接",
  "publish_date": "发布日期",
  "update_date": "更新日期",
  "category": "主分类",
  "subcategory": "子分类",
  "tags": ["标签数组"],
  "related_articles": ["关联文章ID数组"],
  "is_key_article": "是否核心文章",
  "read_time": "预计阅读时间"
}
```

**UI 设计：**
- 左侧：知识分类导航树
- 右侧：文章列表/详情
- 支持：目录大纲、关联文章推荐、标签云

---

### 模块 3：资讯时间轴 (Timeline)

**功能描述：**
- 以时间轴形式展示重要行业事件
- 支持按公司/技术类型筛选
- 可查看事件详情和相关报道

**适用场景：**
- 追踪某公司的发展历程
- 了解某项技术的演进路线
- 回顾行业重大事件

**数据字段：**
```json
{
  "id": "唯一标识",
  "date": "事件日期",
  "title": "事件标题",
  "description": "事件描述",
  "type": "事件类型 [product_launch|funding|partnership|breakthrough|policy]",
  "company": "相关公司",
  "category": "领域分类",
  "related_links": ["相关链接数组"],
  "importance": "重要程度 [high|medium|low]"
}
```

**UI 设计：**
- 垂直时间轴布局
- 左右交替排列
- 支持缩放和时间范围选择

---

### 模块 4：收藏与笔记 (Bookmarks & Notes)

**功能描述：**
- 用户可收藏感兴趣的文章（使用 localStorage）
- 支持添加个人笔记
- 生成个人阅读清单

**数据存储：**
- 使用浏览器 localStorage 存储用户数据
- 支持导出/导入收藏列表

**UI 设计：**
- 收藏夹页面
- 笔记侧边栏
- 阅读历史

---

### 模块 5：数据看板 (Dashboard)

**功能描述：**
- 展示网站数据统计
- 行业热度趋势
- 信息源分布

**统计指标：**
- 总文章数
- 今日新增
- 分类占比
- 热门标签
- 活跃信息源

**UI 设计：**
- 图表可视化（使用轻量级图表库）
- 实时数据更新
- 支持时间范围筛选

---

## 技术架构

### 前端技术栈
- **框架：** 纯 HTML + CSS + JavaScript（无框架，便于 GitHub Pages 部署）
- **样式：** CSS Grid + Flexbox 响应式布局
- **图标：** SVG 内联图标
- **存储：** 
  - 文章数据：JSON 文件
  - 用户数据：localStorage

### 数据结构

```
/data
  /articles
    /daily          # 每日资讯
      2026-03-13.json
      2026-03-12.json
    /research       # 行业研究
      autonomous/   # 自动驾驶
      robotics/     # 具身智能
      llm/          # 大模型
  /timeline         # 时间轴数据
  /stats            # 统计数据

/assets
  /css
  /js
  /images

index.html          # 首页 - 每日必读
research.html       # 行业研究
timeline.html       # 时间轴
bookmarks.html      # 收藏夹
dashboard.html      # 数据看板
```

### 数据更新流程

1. **每日资讯更新：**
   - 爬虫/手动收集资讯
   - 生成 JSON 数据文件
   - 提交到 GitHub
   - GitHub Pages 自动部署

2. **行业研究更新：**
   - 整理深度文章
   - 更新 Markdown/JSON
   - 提交到 GitHub

---

## 页面设计规范

### 色彩方案
```css
:root {
  --primary: #667eea;        /* 主色：紫色渐变 */
  --primary-dark: #764ba2;
  --accent: #4ecdc4;         /* 强调色：青色 */
  --warning: #ff6b6b;        /* 警告色：红色 */
  --success: #44a08d;        /* 成功色：绿色 */
  --dark: #1a1a2e;           /* 深色背景 */
  --light: #f8f9fa;          /* 浅色背景 */
  --text: #333;              /* 正文 */
  --text-light: #666;        /* 次要文字 */
  --border: #e8e8e8;         /* 边框 */
}
```

### 字体规范
- 标题：系统默认无衬线字体
- 正文：-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei'
- 代码：'SF Mono', Monaco, monospace

### 布局规范
- 最大宽度：1400px
- 卡片圆角：16px
- 按钮圆角：20px（胶囊形）或 8px（方形）
- 间距系统：4px, 8px, 12px, 16px, 20px, 24px, 32px

### 响应式断点
- 桌面：> 1024px
- 平板：768px - 1024px
- 手机：< 768px

---

## 开发计划

### 第一阶段：核心功能（MVP）
- [ ] 首页 - 每日必读模块
- [ ] 文章卡片组件
- [ ] 分类筛选功能
- [ ] 搜索功能
- [ ] 详情弹窗

### 第二阶段：知识库
- [ ] 行业研究页面
- [ ] 知识分类导航
- [ ] 文章详情页
- [ ] 关联文章推荐

### 第三阶段：增强功能
- [ ] 时间轴页面
- [ ] 收藏夹功能
- [ ] 数据看板
- [ ] 数据导出

### 第四阶段：优化迭代
- [ ] 性能优化
- [ ] SEO 优化
- [ ] 用户体验优化
- [ ] 更多数据源接入

---

## 使用说明

### 对于内容维护者

1. **添加每日资讯：**
   - 编辑 `/data/articles/daily/YYYY-MM-DD.json`
   - 按格式添加文章数据
   - 提交到 GitHub

2. **添加研究文章：**
   - 在 `/data/articles/research/` 对应分类下创建文件
   - 使用 Markdown 格式编写内容
   - 更新索引文件

3. **更新时间轴：**
   - 编辑 `/data/timeline/events.json`
   - 添加新事件

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
- [ ] 用户评论系统（使用 GitHub Issues）
- [ ] 多语言支持

---

**文档版本：** v1.0  
**创建日期：** 2026-03-13  
**作者：** OpenClaw
