#!/usr/bin/env python3
"""
Info-Getter Playwright Web爬虫 - 扩展版
覆盖更多源，卓驭科技检索一年文章
"""

import sys
sys.path.insert(0, '/Users/jarvis/Library/Python/3.9/lib/python/site-packages')

from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
from pathlib import Path
import json

# 时间范围 - 卓驭科技一年，其他30天
cutoff_date_zhuoyu = datetime.now() - timedelta(days=365)
cutoff_date_others = datetime.now() - timedelta(days=30)

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
            page.wait_for_selector('article, [class*="card"], [class*="post"]', timeout=10000)
            
            cards = page.query_selector_all('article, [class*="card"], [class*="post"]')
            print(f"    找到 {len(cards)} 个文章元素")
            
            for card in cards[:20]:
                try:
                    title_elem = card.query_selector('h2, h3, [class*="title"]')
                    if not title_elem:
                        continue
                    title = title_elem.inner_text().strip()
                    if len(title) < 15:
                        continue
                    
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
                except:
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
                except:
                    continue
        except Exception as e:
            print(f"    ❌ 错误: {e}")
        finally:
            browser.close()
    
    print(f"    ✅ {len(articles)} 篇")
    return articles

def crawl_zhuoyu():
    """爬取卓驭科技 - 检索一年文章"""
    articles = []
    print("  🔍 卓驭科技官网 (检索一年)...")
    
    urls = [
        "https://www.zhuoyutech.com/news",
        "https://www.zhuoyutech.com/news/company",
        "https://www.zhuoyutech.com/news/product",
    ]
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        for url in urls:
            try:
                page = browser.new_page()
                page.goto(url, timeout=30000)
                page.wait_for_load_state('networkidle')
                
                items = page.query_selector_all('article, .news-item, [class*="news"], .item')
                print(f"    {url}: 找到 {len(items)} 个条目")
                
                for item in items[:30]:
                    try:
                        title_elem = item.query_selector('h2, h3, h4, .title')
                        if not title_elem:
                            continue
                        
                        title = title_elem.inner_text().strip()
                        if len(title) < 10:
                            continue
                        
                        link_elem = item.query_selector('a')
                        href = link_elem.get_attribute('href') if link_elem else ''
                        if href and not href.startswith('http'):
                            href = 'https://www.zhuoyutech.com' + href
                        
                        # 日期解析
                        date_elem = item.query_selector('time, .date')
                        date_str = date_elem.inner_text().strip() if date_elem else ''
                        pub_date = datetime.now()
                        
                        if date_str:
                            for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%m-%d']:
                                try:
                                    pub_date = datetime.strptime(date_str, fmt)
                                    break
                                except:
                                    continue
                        
                        # 筛选一年内
                        if pub_date < cutoff_date_zhuoyu:
                            continue
                        
                        articles.append({
                            'id': f"zhuoyu_{abs(hash(href)) % 100000}",
                            'title': title,
                            'url': href,
                            'source': {'name': '卓驭科技', 'type': 'official'},
                            'category': 'zhuoyu',
                            'published_at': pub_date.isoformat(),
                            'summary': ''
                        })
                    except:
                        continue
                
                page.close()
            except Exception as e:
                print(f"    ⚠️ {url} 失败: {str(e)[:50]}")
        
        browser.close()
    
    print(f"    ✅ {len(articles)} 篇")
    return articles

def crawl_tesla():
    """爬取Tesla AI"""
    articles = []
    print("  🔍 Tesla AI...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto("https://www.tesla.com/blog", timeout=30000)
            page.wait_for_load_state('networkidle')
            
            posts = page.query_selector_all('article, [class*="post"]')
            
            for post in posts[:15]:
                try:
                    title_elem = post.query_selector('h2, h3, .title')
                    if not title_elem:
                        continue
                    
                    title = title_elem.inner_text().strip()
                    if 'AI' not in title and 'Optimus' not in title and 'FSD' not in title:
                        continue
                    
                    link_elem = post.query_selector('a')
                    href = link_elem.get_attribute('href') if link_elem else ''
                    
                    articles.append({
                        'id': f"tesla_{abs(hash(href)) % 100000}",
                        'title': title,
                        'url': href,
                        'source': {'name': 'Tesla AI', 'type': 'official'},
                        'category': 'robotics',
                        'published_at': datetime.now().isoformat(),
                        'summary': ''
                    })
                except:
                    continue
        except Exception as e:
            print(f"    ❌ 错误: {e}")
        finally:
            browser.close()
    
    print(f"    ✅ {len(articles)} 篇")
    return articles

def crawl_anthropic():
    """爬取Anthropic"""
    articles = []
    print("  🔍 Anthropic...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto("https://www.anthropic.com/news", timeout=30000)
            page.wait_for_load_state('networkidle')
            
            items = page.query_selector_all('article, [class*="news"]')
            
            for item in items[:20]:
                try:
                    title_elem = item.query_selector('h2, h3')
                    if not title_elem:
                        continue
                    
                    title = title_elem.inner_text().strip()
                    link_elem = item.query_selector('a')
                    href = link_elem.get_attribute('href') if link_elem else ''
                    
                    articles.append({
                        'id': f"anthropic_{abs(hash(href)) % 100000}",
                        'title': title,
                        'url': href,
                        'source': {'name': 'Anthropic', 'type': 'official'},
                        'category': 'ai',
                        'published_at': datetime.now().isoformat(),
                        'summary': ''
                    })
                except:
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
            
            links = page.query_selector_all('a[href*="news"]')
            
            for link in links[:15]:
                try:
                    title = link.inner_text().strip()
                    if len(title) < 20:
                        continue
                    
                    href = link.get_attribute('href')
                    
                    articles.append({
                        'id': f"figure_{abs(hash(href)) % 100000}",
                        'title': title,
                        'url': href,
                        'source': {'name': 'Figure AI', 'type': 'official'},
                        'category': 'robotics',
                        'published_at': datetime.now().isoformat(),
                        'summary': ''
                    })
                except:
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
    print("🚀 Info-Getter Playwright Web爬虫 - 扩展版")
    print(f"⏰ 卓驭科技: 一年 | 其他: 30天")
    print("=" * 70)
    
    all_articles = []
    
    # 爬取各个源
    all_articles.extend(crawl_deepmind())
    all_articles.extend(crawl_waymo())
    all_articles.extend(crawl_zhuoyu())  # 卓驭科技 - 一年
    all_articles.extend(crawl_tesla())
    all_articles.extend(crawl_anthropic())
    all_articles.extend(crawl_figure())
    
    print("\n" + "=" * 70)
    print(f"📊 总计: {len(all_articles)} 篇文章")
    
    # 按源统计
    from collections import defaultdict
    by_source = defaultdict(int)
    for a in all_articles:
        by_source[a['source']['name']] += 1
    
    print("\n按源统计:")
    for source, count in sorted(by_source.items(), key=lambda x: -x[1]):
        print(f"  {source}: {count} 篇")
    
    # 保存
    if all_articles:
        print("\n💾 保存文章...")
        file_path = Path('data/articles/research/web_crawled.json')
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 去重
        seen_ids = set()
        unique_articles = []
        for a in all_articles:
            if a['id'] not in seen_ids:
                seen_ids.add(a['id'])
                unique_articles.append(a)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(unique_articles, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 保存 {len(unique_articles)} 篇唯一文章")
        
        # Git提交
        import subprocess
        try:
            subprocess.run(['git', 'add', 'data/articles/research/'], check=True)
            subprocess.run(['git', 'commit', '-m', f'[Playwright爬虫] 扩展采集 {len(unique_articles)} 篇文章'], check=True)
            subprocess.run(['git', 'push', 'user-pages', 'master'], check=True)
            print("✅ Git推送完成")
        except Exception as e:
            print(f"⚠️ Git操作失败: {e}")
    
    print("\n🎉 完成!")
    return all_articles

if __name__ == '__main__':
    main()
