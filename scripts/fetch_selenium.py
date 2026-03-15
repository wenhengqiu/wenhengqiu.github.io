#!/usr/bin/env python3
"""
Info-Getter 完整采集 - 使用Selenium浏览器爬虫
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
import json
import time
import yaml

# 导入爬虫
try:
    from info_getter.selenium_crawler import crawl_with_selenium
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️ Selenium未安装")

try:
    import feedparser
    FEEDPARSER_AVAILABLE = True
except ImportError:
    FEEDPARSER_AVAILABLE = False
    print("⚠️ feedparser未安装")

# 配置
cutoff_date = datetime.now() - timedelta(days=30)

with open('config/sources.yaml', 'r') as f:
    config = yaml.safe_load(f)

def generate_id(source_id, url):
    """生成唯一ID"""
    import hashlib
    content = f"{source_id}:{url}"
    return hashlib.md5(content.encode()).hexdigest()[:16]

def parse_date(date_str):
    """解析日期"""
    if not date_str:
        return None
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except:
            continue
    return None

def fetch_rss(source):
    """获取RSS"""
    if not FEEDPARSER_AVAILABLE:
        return []
    
    articles = []
    try:
        print(f"  📡 RSS: {source['name']}")
        feed = feedparser.parse(source['url'])
        
        for entry in feed.entries[:30]:
            pub_date = None
            if hasattr(entry, 'published'):
                pub_date = parse_date(entry.published)
            elif hasattr(entry, 'updated'):
                pub_date = parse_date(entry.updated)
            
            if pub_date and pub_date < cutoff_date:
                continue
            
            articles.append({
                'id': generate_id(source['id'], entry.link),
                'title': entry.title,
                'url': entry.link,
                'source': {'name': source['name'], 'type': 'rss'},
                'category': source['category'],
                'published_at': pub_date.isoformat() if pub_date else datetime.now().isoformat(),
                'summary': entry.get('summary', '')[:500],
            })
        
        print(f"    ✅ {len(articles)} 篇")
        return articles
    except Exception as e:
        print(f"    ❌ {e}")
        return []

def fetch_selenium(source):
    """使用Selenium获取Web源"""
    if not SELENIUM_AVAILABLE:
        print(f"  🌐 Web: {source['name']} (Selenium不可用)")
        return []
    
    print(f"  🌐 Selenium: {source['name']}")
    articles = crawl_with_selenium(source['id'], cutoff_date)
    return articles

def classify_and_score(articles):
    """分类和质量评分"""
    keywords = {
        'ai': ['GPT', 'LLM', '大模型', 'Claude', 'Gemini', 'OpenAI', 'DeepMind', 'AI', 'AGI'],
        'robotics': ['机器人', '具身智能', 'Figure', 'Optimus', '宇树', '智元', 'Boston Dynamics'],
        'autonomous': ['自动驾驶', 'FSD', 'ADAS', 'NOA', 'Waymo', '特斯拉', '智驾'],
        'zhuoyu': ['卓驭', '成行平台', '大疆车载', '沈劭劼']
    }
    
    for article in articles:
        # 分类
        text = article['title'] + ' ' + article.get('summary', '')
        scores = {cat: sum(1 for kw in kws if kw in text) for cat, kws in keywords.items()}
        article['category'] = max(scores, key=scores.get) if max(scores.values()) > 0 else 'general'
        
        # 质量评分
        score = 0.5
        source_name = article.get('source', {}).get('name', '').lower()
        if any(s in source_name for s in ['openai', 'deepmind', 'google', 'mit', 'waymo']):
            score += 0.2
        elif any(s in source_name for s in ['techcrunch', 'verge', 'wired']):
            score += 0.15
        
        if len(article['title']) > 20:
            score += 0.1
        if any(kw in article['title'] for kw in ['发布', '推出', '突破', '融资']):
            score += 0.1
        if len(article.get('summary', '')) > 100:
            score += 0.1
        
        article['quality_score'] = min(score, 1.0)
    
    return articles

def main():
    """主函数"""
    print("=" * 70)
    print("🚀 Info-Getter 完整采集 (RSS + Selenium)")
    print(f"⏰ 时间范围: {cutoff_date.strftime('%Y-%m-%d')} 至今")
    print("=" * 70)
    
    all_articles = []
    total_sources = len(config['sources'])
    
    for i, source in enumerate(config['sources'], 1):
        print(f"\n[{i}/{total_sources}] {source['name']}")
        
        source_type = source.get('type', 'rss')
        
        if source_type == 'rss' and FEEDPARSER_AVAILABLE:
            articles = fetch_rss(source)
        elif source_type == 'web' and SELENIUM_AVAILABLE:
            articles = fetch_selenium(source)
        else:
            articles = fetch_rss(source) if FEEDPARSER_AVAILABLE else []
        
        all_articles.extend(articles)
        time.sleep(0.5)
    
    print("\n" + "=" * 70)
    print(f"📥 原始采集: {len(all_articles)} 篇文章")
    
    # 分类和评分
    print("\n🔍 分类和质量评分...")
    all_articles = classify_and_score(all_articles)
    
    # 筛选
    filtered = [a for a in all_articles if a['quality_score'] >= 0.6]
    print(f"🔥 高质量文章 (≥0.6): {len(filtered)}/{len(all_articles)}")
    
    # 保存
    if filtered:
        print("\n💾 保存文章...")
        by_category = {}
        for article in filtered:
            cat = article['category']
            by_category.setdefault(cat, []).append(article)
        
        for category, articles in by_category.items():
            file_path = Path(f'data/articles/research/{category}.json')
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            
            print(f"  ✅ {category}: {len(articles)} 篇")
        
        # Git提交
        print("\n📦 Git提交...")
        import subprocess
        try:
            subprocess.run(['git', 'add', 'data/articles/research/'], check=True)
            subprocess.run(['git', 'commit', '-m', f'[Info-Getter] Selenium采集 {len(filtered)} 篇文章'], check=True)
            subprocess.run(['git', 'push', 'user-pages', 'master'], check=True)
            print("✅ Git推送完成")
        except Exception as e:
            print(f"⚠️ Git操作失败: {e}")
    
    print("\n🎉 完成!")
    print(f"总计: {len(filtered)} 篇高质量文章")

if __name__ == '__main__':
    main()
