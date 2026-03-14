#!/usr/bin/env python3
"""
Info-Getter 简化运行版本
使用模拟数据展示完整流程
"""

import json
import random
from datetime import datetime
from pathlib import Path

# 模拟信息源
SOURCES = [
    {"name": "OpenAI Blog", "category": "llm", "language": "en"},
    {"name": "机器之心", "category": "llm", "language": "zh"},
    {"name": "Tesla Blog", "category": "autonomous", "language": "en"},
    {"name": "量子位", "category": "general", "language": "zh"},
    {"name": "DeepMind", "category": "llm", "language": "en"},
]

# 模拟文章模板
ARTICLE_TEMPLATES = [
    {
        "title_en": "OpenAI Announces GPT-5 with Revolutionary Features",
        "title_zh": "OpenAI 发布 GPT-5，具有革命性功能",
        "category": "llm"
    },
    {
        "title_en": "Tesla FSD V14 Rolls Out to Beta Testers",
        "title_zh": "特斯拉 FSD V14 向测试用户推送",
        "category": "autonomous"
    },
    {
        "title_en": "Figure AI Demonstrates New Humanoid Robot Capabilities",
        "title_zh": "Figure AI 展示新型人形机器人能力",
        "category": "robotics"
    },
    {
        "title_en": "DeepMind Achieves Breakthrough in Protein Folding",
        "title_zh": "DeepMind 在蛋白质折叠领域取得突破",
        "category": "llm"
    },
]

def fetch_articles():
    """模拟采集文章"""
    print("📥 正在从 51 个信息源采集文章...")
    
    articles = []
    count = random.randint(3, 8)  # 随机采集 3-8 篇
    
    for i in range(count):
        template = random.choice(ARTICLE_TEMPLATES)
        article = {
            "id": f"2026-03-14-{i+1:03d}",
            "title": template["title_en"],
            "title_zh": None,
            "summary": f"This is a summary of the article about {template['title_en'][:30]}...",
            "summary_zh": None,
            "url": f"https://example.com/article/{i+1}",
            "source": random.choice([s["name"] for s in SOURCES]),
            "category": template["category"],
            "language": "en" if random.random() > 0.3 else "zh",
            "published_at": datetime.now().isoformat()
        }
        articles.append(article)
    
    print(f"✅ 采集到 {len(articles)} 篇文章")
    for article in articles:
        print(f"   • [{article['category']}] {article['title'][:50]}...")
    print()
    
    return articles

def translate_articles(articles):
    """模拟翻译文章"""
    print("🌐 正在翻译文章...")
    
    translated = 0
    for article in articles:
        if article["language"] == "en":
            # 查找对应的中文标题
            for template in ARTICLE_TEMPLATES:
                if template["title_en"] == article["title"]:
                    article["title_zh"] = template["title_zh"]
                    article["summary_zh"] = f"这是关于{template['title_zh'][:20]}的文章摘要..."
                    translated += 1
                    break
            else:
                # 默认翻译
                article["title_zh"] = article["title"][:30] + " (中文)"
                article["summary_zh"] = article["summary"][:50] + "..."
                translated += 1
        else:
            article["title_zh"] = article["title"]
            article["summary_zh"] = article["summary"]
    
    print(f"✅ 翻译完成 {translated} 篇文章")
    for article in articles:
        print(f"   • {article['title_zh'][:40]}...")
    print()
    
    return articles

def score_articles(articles):
    """质量评分"""
    print("⭐ 正在进行质量评分...")
    
    for article in articles:
        # 模拟评分 0.6-0.95
        score = random.uniform(0.6, 0.95)
        article["quality_score"] = round(score, 2)
    
    # 按分数排序
    articles.sort(key=lambda x: x["quality_score"], reverse=True)
    
    passed = sum(1 for a in articles if a["quality_score"] >= 0.7)
    
    print(f"✅ 质量评分完成")
    for article in articles:
        status = "通过" if article["quality_score"] >= 0.7 else "过滤"
        print(f"   • [{article['quality_score']}] {article['title_zh'][:30]}... → {status}")
    print()
    
    return articles, passed

def publish_articles(articles):
    """发布文章到本地文件"""
    print("📤 正在发布文章...")
    
    data_dir = Path("data/articles/research")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    published = 0
    for article in articles:
        if article.get("quality_score", 0) < 0.7:
            continue
        
        # 读取现有文件
        file_path = data_dir / f"{article['category']}.json"
        
        if file_path.exists():
            with open(file_path, 'r') as f:
                existing = json.load(f)
        else:
            existing = []
        
        # 检查重复
        if not any(a.get("id") == article["id"] for a in existing):
            # 添加到文件
            article_data = {
                "id": article["id"],
                "title": article["title_zh"],
                "summary": article["summary_zh"],
                "url": article["url"],
                "source": article["source"],
                "category": article["category"],
                "quality_score": article["quality_score"],
                "published_at": article["published_at"]
            }
            existing.append(article_data)
            
            # 保存
            with open(file_path, 'w') as f:
                json.dump(existing, f, ensure_ascii=False, indent=2)
            
            published += 1
            print(f"   ✅ 发布: {article['title_zh'][:40]}...")
    
    print()
    return published

def git_commit():
    """模拟 Git 提交"""
    print("📦 正在提交到 GitHub...")
    print("   git add data/articles/")
    print("   git commit -m 'auto: update articles'")
    print("   git push origin main")
    print("✅ 提交完成")
    print()

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 Info-Getter 运行中")
    print("=" * 60)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    start_time = datetime.now()
    
    # 1. 采集
    articles = fetch_articles()
    
    # 2. 翻译
    articles = translate_articles(articles)
    
    # 3. 评分
    articles, passed = score_articles(articles)
    
    # 4. 发布
    published = publish_articles(articles)
    
    # 5. Git 提交
    git_commit()
    
    # 汇总
    duration = (datetime.now() - start_time).total_seconds()
    
    print("=" * 60)
    print("🎉 运行完成!")
    print("=" * 60)
    print()
    print("📊 本次运行统计:")
    print(f"   采集文章: {len(articles)} 篇")
    print(f"   翻译文章: {sum(1 for a in articles if a['language'] == 'en')} 篇")
    print(f"   通过评分: {passed} 篇")
    print(f"   成功发布: {published} 篇")
    print(f"   耗时: {duration:.1f} 秒")
    print()
    print("📁 数据文件:")
    for file in Path("data/articles/research").glob("*.json"):
        with open(file) as f:
            count = len(json.load(f))
        print(f"   {file.name}: {count} 篇")
    print()
    print("⏰ 下次运行: 1小时后")
    print()

if __name__ == "__main__":
    main()
