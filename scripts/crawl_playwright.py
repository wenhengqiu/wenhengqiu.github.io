#!/usr/bin/env python3
"""
Info-Getter Playwright Web爬虫
使用系统Python + Playwright，无需额外配置
"""

import sys
sys.path.insert(0, '/Users/jarvis/Library/Python/3.9/lib/python/site-packages')

from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
from pathlib import Path
import json
import re

# 时间范围
cutoff_date = datetime.now() - timedelta(days=30)

def crawl_deepmind():
    """爬取DeepMind Blog"""
    articles = []
    print("  🔍 DeepMind Blog...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto("https://deepmind.google/discover/blog/", timeout=30000)
            page.wait_for_load_state('networkidle')
            
            # 等待文章加载
            page.wait_for_selector('article, [class*="card"], [class*="post"]', timeout=10000)
            
            # 提取文章
            cards = page.query_selector_all('article, [class*="card"], [class*="post"]')
            print(f"    找到 {len(cards)} 个文章元素")
            
            for card in cards[:20]:
                try:
                    # 标题
                    title_elem = card.query_selector('h2, h3, [class*="title"]')
                    if not title_elem:
                        continue
                    title = title_elem.inner_text().strip()
                    if len(title) < 15:
                        continue
                    
                    # 链接
                    link_elem = card.query_selector('a')
                    href = link_elem.get_attribute('href') if link_elem else ''
                    if href and not href.startswith('http'):
                        href = 'https://deepmind.google' + href
                    
                    articles.append({
                        'id': f"deepmind_{abs(hash(href)) % 100000}",
                        'title': title,
                        'url': href,
                        'source': {'name': 'DeepMind Blog', 'type': 'official'},
                        'category': 'ai',
                        'published_at': datetime.now().isoformat(),
                        'summary': ''
                    })
                    
                except Exception as e:
                    continue
            
        except Exception as e:
            print(f"    ❌ 错误: {e}")
        finally:
            browser.close()
    
    print(f"    ✅ {len(articles)} 篇")
    return articles

def crawl_figure():
    """爬取Figure AI"""
    articles = []
    print("  🔍 Figure AI...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto("https://www.figure.ai/news", timeout=30000)
            page.wait_for_load_state('networkidle')
            
            # 查找新闻链接
            links = page.query_selector_all('a[href*="news"]')
            print(f"    找到 {len(links)} 个链接")
            
            for link in links[:15]:
                try:
                    title = link.inner_text().strip()
                    if len(title) < 20 or len(title) > 200:
                        continue
                    
                    href = link.get_attribute('href')
                    if not href or 'figure.ai' not in href:
                        continue
                    
                    articles.append({
                        'id': f"figure_{abs(hash(href)) % 100000}",
                        'title': title,
                        'url': href,
                        'source': {'name': 'Figure AI', 'type': 'official'},
                        'category': 'robotics',
                        'published_at': datetime.now().isoformat(),
                        'summary': ''
                    })
                    
                except Exception as e:
                    continue
            
        except Exception as e:
            print(f"    ❌ 错误: {e}")
        finally:
            browser.close()
    
    print(f"    ✅ {len(articles)} 篇")
    return articles

def crawl_waymo():
    """爬取Waymo Blog"""
    articles = []
    print("  🔍 Waymo Blog...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto("https://waymo.com/blog/", timeout=30000)
            page.wait_for_load_state('networkidle')
            
            # 等待文章加载
            page.wait_for_selector('article, [class*="post"]', timeout=10000)
            
            posts = page.query_selector_all('article, [class*="post"]')
            print(f"    找到 {len(posts)} 篇文章")
            
            for post in posts[:15]:
                try:
                    title_elem = post.query_selector('h2, h3, [class*="title"]')
                    if not title_elem:
                        continue
                    
                    title = title_elem.inner_text().strip()
                    link_elem = post.query_selector('a')
                    href = link_elem.get_attribute('href') if link_elem else ''
                    
                    articles.append({
                        'id': f"waymo_{abs(hash(href)) % 100000}",
                        'title': title,
                        'url': href,
                        'source': {'name': 'Waymo Blog', 'type': 'official'},
                        'category': 'autonomous',
                        'published_at': datetime.now().isoformat(),
                        'summary': ''
                    })
                    
                except Exception as e:
                    continue
            
        except Exception as e:
            print(f"    ❌ 错误: {e}")
        finally:
            browser.close()
    
    print(f"    ✅ {len(articles)} 篇")
    return articles

def main():
    """主函数"""
    print("=" * 70)
    print("🚀 Info-Getter Playwright Web爬虫")
    print(f"⏰ 时间范围: {cutoff_date.strftime('%Y-%m-%d')} 至今")
    print("=" * 70)
    
    all_articles = []
    
    # 爬取各个源
    all_articles.extend(crawl_deepmind())
    all_articles.extend(crawl_figure())
    all_articles.extend(crawl_waymo())
    
    print("\n" + "=" * 70)
    print(f"📊 总计: {len(all_articles)} 篇文章")
    
    # 显示文章
    if all_articles:
        print("\n文章列表:")
        for i, a in enumerate(all_articles[:10], 1):
            print(f"{i}. [{a['source']['name']}] {a['title'][:50]}...")
    
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
            subprocess.run(['git', 'commit', '-m', f'[Playwright爬虫] 采集 {len(all_articles)} 篇文章'], check=True)
            subprocess.run(['git', 'push', 'user-pages', 'master'], check=True)
            print("✅ Git推送完成")
        except Exception as e:
            print(f"⚠️ Git操作失败: {e}")
    
    print("\n🎉 完成!")
    return all_articles

if __name__ == '__main__':
    main()
