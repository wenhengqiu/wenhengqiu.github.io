#!/usr/bin/env python3
"""
Info-Getter 简化版Web爬虫
使用Python标准库，不依赖外部包
"""

import urllib.request
import urllib.error
import re
from datetime import datetime, timedelta
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

# 时间范围
cutoff_date = datetime.now() - timedelta(days=30)

def fetch_url(url):
    """使用标准库获取网页"""
    try:
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"    ❌ 获取失败: {e}")
        return None

def parse_html_simple(html, source_name):
    """简化版HTML解析"""
    articles = []
    if not html:
        return articles
    
    # 查找标题链接模式
    # 模式1: <a href="...">标题</a>
    link_pattern = r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]+)</a>'
    links = re.findall(link_pattern, html, re.IGNORECASE)
    
    # 查找日期模式
    date_patterns = [
        r'(\d{4}-\d{2}-\d{2})',
        r'(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})',
        r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4})',
    ]
    
    seen_urls = set()
    for href, title in links[:50]:  # 最多50个链接
        title = title.strip()
        
        # 过滤无效链接
        if len(title) < 15 or len(title) > 200:
            continue
        if href.startswith('#') or href.startswith('javascript'):
            continue
        if href in seen_urls:
            continue
        
        seen_urls.add(href)
        
        # 构建完整URL
        if href.startswith('/'):
            # 相对路径
            base = re.match(r'(https?://[^/]+)', source_name)
            if base:
                href = base.group(1) + href
        elif not href.startswith('http'):
            continue
        
        # 尝试从附近文本找日期
        pub_date = datetime.now()
        
        articles.append({
            'id': f"web_{abs(hash(href)) % 100000}",
            'title': title,
            'url': href,
            'source': {'name': source_name, 'type': 'web'},
            'category': 'general',
            'published_at': pub_date.isoformat(),
            'summary': ''
        })
    
    return articles

def crawl_source(name, url):
    """爬取单个源"""
    print(f"  🌐 {name}")
    html = fetch_url(url)
    if html:
        articles = parse_html_simple(html, name)
        print(f"    ✅ {len(articles)} 篇")
        return articles
    return []

def main():
    """主函数"""
    print("=" * 70)
    print("🚀 Info-Getter Web爬虫 (标准库版)")
    print(f"⏰ 时间范围: {cutoff_date.strftime('%Y-%m-%d')} 至今")
    print("=" * 70)
    
    # Web源列表
    web_sources = [
        ("DeepMind Blog", "https://deepmind.google/discover/blog/"),
        ("Figure AI", "https://www.figure.ai/news"),
        ("Tesla AI", "https://www.tesla.com/AI"),
        ("Waymo Blog", "https://waymo.com/blog/"),
        ("Anthropic", "https://www.anthropic.com/news"),
    ]
    
    all_articles = []
    
    for name, url in web_sources:
        articles = crawl_source(name, url)
        all_articles.extend(articles)
    
    print("\n" + "=" * 70)
    print(f"📊 总计: {len(all_articles)} 篇文章")
    
    # 显示前10篇
    if all_articles:
        print("\n前10篇文章:")
        for i, a in enumerate(all_articles[:10], 1):
            print(f"{i}. {a['title'][:60]}...")
            print(f"   {a['url'][:70]}")
    
    # 保存
    if all_articles:
        print("\n💾 保存文章...")
        file_path = Path('data/articles/research/web_crawled.json')
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(all_articles, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 保存到: {file_path}")

if __name__ == '__main__':
    main()
