#!/usr/bin/env python3
"""
Info-Getter Web爬虫 - 使用Python标准库 + SSL禁用
直接在Mac上运行，无需安装额外包
"""

import urllib.request
import urllib.error
import ssl
import re
import json
from datetime import datetime, timedelta
from pathlib import Path

# 禁用SSL验证
ssl._create_default_https_context = ssl._create_unverified_context

# 时间范围
cutoff_date = datetime.now() - timedelta(days=30)

def fetch_url(url):
    """获取网页内容"""
    try:
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"    ❌ 获取失败: {str(e)[:50]}")
        return None

def extract_articles_deepmind(html):
    """提取DeepMind文章"""
    articles = []
    if not html:
        return articles
    
    # DeepMind使用特定数据结构
    # 查找文章链接和标题
    patterns = [
        # 文章卡片模式
        r'<a[^>]+href="(/discover/blog/[^"]+)"[^>]*>\s*<[^>]+>\s*<h[^>]+>([^<]+)</h',
        r'<a[^>]+href="(/discover/blog/[^"]+)"[^>]*>[^<]*<[^>]+>([^<]{20,200})</',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
        for href, title in matches:
            title = re.sub(r'<[^>]+>', '', title).strip()
            if len(title) < 20:
                continue
            
            articles.append({
                'id': f"deepmind_{hash(href) % 100000}",
                'title': title,
                'url': f"https://deepmind.google{href}",
                'source': {'name': 'DeepMind Blog', 'type': 'official'},
                'category': 'ai',
                'published_at': datetime.now().isoformat(),
                'summary': ''
            })
    
    return articles

def extract_articles_figure(html):
    """提取Figure AI文章"""
    articles = []
    if not html:
        return articles
    
    # Figure AI页面结构
    # 查找新闻链接
    pattern = r'<a[^>]+href="(/news/[^"]+)"[^>]*>([^<]{20,200})</a>'
    matches = re.findall(pattern, html, re.IGNORECASE)
    
    for href, title in matches:
        title = re.sub(r'<[^>]+>', '', title).strip()
        articles.append({
            'id': f"figure_{hash(href) % 100000}",
            'title': title,
            'url': f"https://www.figure.ai{href}",
            'source': {'name': 'Figure AI', 'type': 'official'},
            'category': 'robotics',
            'published_at': datetime.now().isoformat(),
            'summary': ''
        })
    
    return articles

def extract_articles_waymo(html):
    """提取Waymo文章"""
    articles = []
    if not html:
        return articles
    
    # Waymo博客结构
    pattern = r'<a[^>]+href="(/blog/[^"]+)"[^>]*>[^<]*<[^>]+>([^<]{20,200})</'
    matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
    
    for href, title in matches:
        title = re.sub(r'<[^>]+>', '', title).strip()
        if 'blog' in href.lower():
            articles.append({
                'id': f"waymo_{hash(href) % 100000}",
                'title': title,
                'url': f"https://waymo.com{href}",
                'source': {'name': 'Waymo Blog', 'type': 'official'},
                'category': 'autonomous',
                'published_at': datetime.now().isoformat(),
                'summary': ''
            })
    
    return articles

def crawl_web_sources():
    """爬取所有Web源"""
    print("=" * 70)
    print("🚀 Info-Getter Web爬虫")
    print(f"⏰ 时间范围: {cutoff_date.strftime('%Y-%m-%d')} 至今")
    print("=" * 70)
    
    sources = [
        ("DeepMind Blog", "https://deepmind.google/discover/blog/", extract_articles_deepmind),
        ("Figure AI", "https://www.figure.ai/news", extract_articles_figure),
        ("Waymo Blog", "https://waymo.com/blog/", extract_articles_waymo),
    ]
    
    all_articles = []
    
    for name, url, extractor in sources:
        print(f"\n🌐 {name}")
        print(f"   URL: {url}")
        
        html = fetch_url(url)
        if html:
            print(f"   📄 页面大小: {len(html)} 字符")
            articles = extractor(html)
            print(f"   ✅ 提取 {len(articles)} 篇文章")
            all_articles.extend(articles)
            
            # 显示前3篇
            for a in articles[:3]:
                print(f"      - {a['title'][:50]}...")
        else:
            print(f"   ❌ 无法获取页面")
    
    print("\n" + "=" * 70)
    print(f"📊 总计: {len(all_articles)} 篇文章")
    
    # 保存
    if all_articles:
        print("\n💾 保存文章...")
        file_path = Path('data/articles/research/web_crawled.json')
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(all_articles, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 保存到: {file_path}")
        
        # Git提交
        import subprocess
        try:
            subprocess.run(['git', 'add', 'data/articles/research/'], check=True)
            subprocess.run(['git', 'commit', '-m', f'[Web爬虫] 采集 {len(all_articles)} 篇文章'], check=True)
            subprocess.run(['git', 'push', 'user-pages', 'master'], check=True)
            print("✅ Git推送完成")
        except Exception as e:
            print(f"⚠️ Git操作失败: {e}")
    
    return all_articles

if __name__ == '__main__':
    articles = crawl_web_sources()
    print("\n🎉 完成!")
