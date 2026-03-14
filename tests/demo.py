#!/usr/bin/env python3
"""
Info-Getter 集成演示（简化版）
展示各模块协同工作流程
"""

import sys
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

def demo_workflow():
    """演示完整工作流程"""
    print("=" * 60)
    print("🚀 Info-Getter 工作流程演示")
    print("=" * 60)
    print()
    
    # 1. 模拟采集
    print("📥 步骤 1: 采集文章")
    print("-" * 40)
    
    mock_articles = [
        {
            "id": "2026-03-14-001",
            "title": "OpenAI Releases GPT-5",
            "title_zh": None,  # 待翻译
            "summary": "OpenAI has announced the release of GPT-5 with significant improvements...",
            "summary_zh": None,  # 待翻译
            "url": "https://openai.com/blog/gpt-5",
            "source": "OpenAI Blog",
            "category": "llm",
            "language": "en",
            "published_at": datetime.now().isoformat()
        },
        {
            "id": "2026-03-14-002",
            "title": "特斯拉 FSD V14 开始测试",
            "title_zh": None,
            "summary": "特斯拉开始向北美用户推送 FSD V14 版本...",
            "summary_zh": None,
            "url": "https://www.tesla.com/blog/fsd-v14",
            "source": "Tesla Blog",
            "category": "autonomous",
            "language": "zh",
            "published_at": datetime.now().isoformat()
        }
    ]
    
    print(f"✅ 从 51 个信息源采集到 {len(mock_articles)} 篇文章")
    for article in mock_articles:
        print(f"   • [{article['category']}] {article['title'][:40]}...")
    print()
    
    # 2. 模拟翻译
    print("🌐 步骤 2: 翻译文章")
    print("-" * 40)
    
    for article in mock_articles:
        if article['language'] == 'en':
            # 模拟翻译
            article['title_zh'] = "OpenAI 发布 GPT-5 模型"
            article['summary_zh'] = "OpenAI 发布 GPT-5，性能大幅提升，支持多模态输入..."
            print(f"✅ 翻译: {article['title'][:30]}... → {article['title_zh']}")
        else:
            # 中文文章直接使用
            article['title_zh'] = article['title']
            article['summary_zh'] = article['summary']
            print(f"✅ 中文: {article['title_zh'][:30]}...")
    
    print()
    
    # 3. 模拟质量评分
    print("⭐ 步骤 3: 质量评分")
    print("-" * 40)
    
    for article in mock_articles:
        # 模拟评分
        score = 0.85 if article['category'] == 'llm' else 0.78
        article['quality_score'] = score
        
        if score >= 0.7:
            print(f"✅ [{score:.2f}] {article['title_zh'][:30]}... → 通过")
        else:
            print(f"❌ [{score:.2f}] {article['title_zh'][:30]}... → 过滤")
    
    print()
    
    # 4. 模拟发布
    print("📤 步骤 4: 发布到 GitHub")
    print("-" * 40)
    
    published = 0
    for article in mock_articles:
        if article.get('quality_score', 0) >= 0.7:
            # 模拟发布
            print(f"✅ 发布: {article['title_zh'][:30]}...")
            print(f"   文件: data/articles/research/{article['category']}.json")
            published += 1
    
    print()
    print(f"📊 发布统计: {published}/{len(mock_articles)} 篇")
    print()
    
    # 5. 模拟 Git 提交
    print("📦 步骤 5: Git 提交")
    print("-" * 40)
    print("✅ git add data/articles/")
    print("✅ git commit -m 'auto: update articles 2026-03-14 11:00'")
    print("✅ git push origin main")
    print()
    
    # 汇总
    print("=" * 60)
    print("🎉 工作流程完成!")
    print("=" * 60)
    print()
    print("📈 本次运行统计:")
    print(f"   采集文章: {len(mock_articles)} 篇")
    print(f"   翻译文章: {sum(1 for a in mock_articles if a['language'] == 'en')} 篇")
    print(f"   发布文章: {published} 篇")
    print(f"   耗时: 2.3 秒")
    print()
    print("⏰ 下次运行: 1小时后")
    print()

def show_architecture():
    """展示系统架构"""
    print("=" * 60)
    print("🏗️ Info-Getter 系统架构")
    print("=" * 60)
    print()
    
    print("模块组成:")
    print("  📦 info_getter/")
    print("     ├── fetcher/          # 采集模块")
    print("     │   └── core.py       # 51个信息源采集")
    print("     ├── translator/       # 翻译模块")
    print("     │   └── core.py       # OpenClaw翻译")
    print("     ├── publisher/        # 发布模块")
    print("     │   └── core.py       # GitHub同步")
    print("     ├── scheduler.py      # 调度器")
    print("     └── __main__.py       # 入口")
    print()
    
    print("数据流:")
    print("  51个信息源 → Fetcher → Translator → Publisher → GitHub")
    print("     ↓            ↓           ↓           ↓")
    print("   RSS/API    英文→中文   质量评分   自动提交")
    print()
    
    print("部署:")
    print("  🐳 Docker + Docker Compose")
    print("  ⏰ 每小时自动运行")
    print("  💓 心跳监控 + 告警")
    print()

def show_sources():
    """展示信息源"""
    print("=" * 60)
    print("📡 信息源列表 (51个)")
    print("=" * 60)
    print()
    
    sources = {
        "官方博客 (12个)": [
            "OpenAI, DeepMind, Anthropic, Meta AI",
            "Tesla, Waymo, 华为, 小鹏, 百度",
            "Figure AI, 宇树科技, 卓驭科技"
        ],
        "科技媒体 (10个)": [
            "机器之心, 量子位, 品玩, 36氪, 雷锋网",
            "TechCrunch, The Verge, MIT Tech Review"
        ],
        "HN热门博客 (20个)": [
            "Joel on Software, Coding Horror, Martin Fowler",
            "Distill.pub, Lilian Weng, Sebastian Ruder",
            "Paul Graham, Sam Altman, Stratechery"
        ],
        "社区论文 (9个)": [
            "Hacker News, Reddit, arXiv",
            "Papers With Code, HuggingFace"
        ]
    }
    
    for category, items in sources.items():
        print(f"【{category}】")
        for item in items:
            print(f"  • {item}")
        print()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--demo', action='store_true', help='运行工作流程演示')
    parser.add_argument('--arch', action='store_true', help='展示系统架构')
    parser.add_argument('--sources', action='store_true', help='展示信息源')
    
    args = parser.parse_args()
    
    if args.arch:
        show_architecture()
    elif args.sources:
        show_sources()
    else:
        # 默认运行演示
        demo_workflow()
        print("\n")
        show_architecture()
