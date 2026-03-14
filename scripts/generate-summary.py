#!/usr/bin/env python3
"""
Daily Summary Generator
生成每日信息总结，用于今日要点展示
"""

import json
import os
from datetime import datetime

def load_articles():
    """加载所有文章"""
    articles = []
    categories = ['llm', 'autonomous', 'robotics', 'zhuoyu']
    base_path = 'data/articles/research'
    
    for cat in categories:
        try:
            with open(f'{base_path}/{cat}.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                for article in data:
                    article['category'] = cat
                    articles.append(article)
        except Exception as e:
            print(f"Error loading {cat}: {e}")
    
    return articles

def get_today_articles(articles):
    """获取今日文章"""
    today = datetime.now().strftime('%Y-%m-%d')
    today_articles = []
    
    for article in articles:
        pub_date = article.get('published_at', '') or article.get('publish_date', '')
        if pub_date.startswith(today):
            today_articles.append(article)
    
    return today_articles

def generate_summary(articles):
    """生成每日总结"""
    if not articles:
        return {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "highlights": [],
            "trend": "今日暂无新文章",
            "stats": {"total": 0, "llm": 0, "autonomous": 0, "robotics": 0, "zhuoyu": 0}
        }
    
    # 按质量分数排序
    sorted_articles = sorted(articles, key=lambda x: x.get('quality_score', 0), reverse=True)
    
    # 提取 Top 5 作为要点
    highlights = []
    for article in sorted_articles[:5]:
        title = article.get('title_zh', article.get('title', ''))
        if title:
            highlights.append(title[:60] + '...' if len(title) > 60 else title)
    
    # 统计各分类数量
    stats = {
        "total": len(articles),
        "llm": len([a for a in articles if a.get('category') == 'llm']),
        "autonomous": len([a for a in articles if a.get('category') == 'autonomous']),
        "robotics": len([a for a in articles if a.get('category') == 'robotics']),
        "zhuoyu": len([a for a in articles if a.get('category') == 'zhuoyu'])
    }
    
    # 生成趋势总结
    categories_present = [k for k, v in stats.items() if v > 0 and k != 'total']
    if len(categories_present) == 1:
        trend = f"今日重点关注{categories_present[0]}领域，共更新 {stats['total']} 篇文章"
    else:
        trend = f"今日 AI 行业多领域更新，共 {stats['total']} 篇文章，涵盖 {', '.join(categories_present)} 等方向"
    
    return {
        "date": datetime.now().strftime('%Y-%m-%d'),
        "highlights": highlights,
        "trend": trend,
        "stats": stats
    }

def save_summary(summary):
    """保存总结到文件"""
    # 确保目录存在
    date = datetime.now()
    year = date.strftime('%Y')
    month = date.strftime('%m')
    day = date.strftime('%d')
    
    dir_path = f'data/summary/{year}/{month}'
    os.makedirs(dir_path, exist_ok=True)
    
    file_path = f'{dir_path}/{day}.json'
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    # 同时保存到最新文件
    with open('data/summary/latest.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"Summary saved to {file_path}")
    return file_path

def main():
    """主函数"""
    print("Generating daily summary...")
    
    # 加载文章
    articles = load_articles()
    print(f"Total articles: {len(articles)}")
    
    # 获取今日文章
    today_articles = get_today_articles(articles)
    print(f"Today's articles: {len(today_articles)}")
    
    # 生成总结
    summary = generate_summary(today_articles)
    print(f"Highlights: {len(summary['highlights'])}")
    print(f"Stats: {summary['stats']}")
    
    # 保存总结
    save_summary(summary)
    
    print("Daily summary generated successfully!")
    return summary

if __name__ == '__main__':
    main()
