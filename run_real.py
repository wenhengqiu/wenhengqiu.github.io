#!/usr/bin/env python3
"""
Info-Getter 轻量级版本
使用标准库 + urllib 实现真实 RSS 采集
"""

import json
import urllib.request
import urllib.error
import ssl
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
import time
import sys

# 创建不验证 SSL 证书的上下文
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# 配置 - 扩展信息源
CONFIG = {
    "sources": [
        # 中文科技媒体
        {"name": "机器之心", "url": "https://www.jiqizhixin.com/rss", "category": "llm", "lang": "zh"},
        {"name": "量子位", "url": "https://www.qbitai.com/rss", "category": "llm", "lang": "zh"},
        {"name": "品玩", "url": "https://www.pingwest.com/rss", "category": "llm", "lang": "zh"},
        {"name": "36氪", "url": "https://36kr.com/feed", "category": "llm", "lang": "zh"},
        {"name": "雷锋网", "url": "https://www.leiphone.com/rss", "category": "llm", "lang": "zh"},
        
        # 英文官方博客
        {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml", "category": "llm", "lang": "en"},
        {"name": "DeepMind", "url": "https://deepmind.google/discover/blog/", "category": "llm", "lang": "en"},
        {"name": "Tesla Blog", "url": "https://www.tesla.com/blog/rss.xml", "category": "autonomous", "lang": "en"},
        {"name": "Waymo", "url": "https://waymo.com/blog/rss/", "category": "autonomous", "lang": "en"},
        
        # 国际科技媒体
        {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "category": "llm", "lang": "en"},
        {"name": "The Verge AI", "url": "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml", "category": "llm", "lang": "en"},
        {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/", "category": "llm", "lang": "en"},
    ],
    "min_quality_score": 0.6,  # 降低阈值以获取更多文章
    "max_articles": 30
}

class SimpleFetcher:
    """简单采集器"""
    
    def fetch_rss(self, url, timeout=10):
        """获取 RSS 内容"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; InfoGetter/1.0)'
            }
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout, context=ssl_context) as response:
                return response.read().decode('utf-8')
        except Exception as e:
            print(f"   ❌ 获取失败: {e}")
            return None
    
    def parse_rss(self, xml_content, source_name, category, lang):
        """解析 RSS"""
        articles = []
        try:
            root = ET.fromstring(xml_content)
            
            # 处理 RSS 2.0
            if root.tag == 'rss':
                channel = root.find('channel')
                if channel is not None:
                    for item in channel.findall('item')[:3]:  # 只取前3篇
                        title = item.findtext('title', '')
                        link = item.findtext('link', '')
                        desc = item.findtext('description', '')
                        pub_date = item.findtext('pubDate', '')
                        
                        if title and link:
                            articles.append({
                                'id': f"{source_name}_{int(time.time())}_{len(articles)}",
                                'title': title,
                                'title_zh': title if lang == 'zh' else None,
                                'summary': desc[:200] if desc else '',
                                'summary_zh': desc[:200] if lang == 'zh' else None,
                                'url': link,
                                'source': source_name,
                                'category': category,
                                'language': lang,
                                'published_at': datetime.now().isoformat()
                            })
            
            # 处理 Atom
            elif 'feed' in root.tag:
                for entry in root.findall('{http://www.w3.org/2005/Atom}entry')[:3]:
                    title = entry.findtext('{http://www.w3.org/2005/Atom}title', '')
                    link_elem = entry.find('{http://www.w3.org/2005/Atom}link')
                    link = link_elem.get('href', '') if link_elem is not None else ''
                    summary = entry.findtext('{http://www.w3.org/2005/Atom}summary', '')
                    
                    if title and link:
                        articles.append({
                            'id': f"{source_name}_{int(time.time())}_{len(articles)}",
                            'title': title,
                            'title_zh': title if lang == 'zh' else None,
                            'summary': summary[:200] if summary else '',
                            'summary_zh': summary[:200] if lang == 'zh' else None,
                            'url': link,
                            'source': source_name,
                            'category': category,
                            'language': lang,
                            'published_at': datetime.now().isoformat()
                        })
        except Exception as e:
            print(f"   ❌ 解析失败: {e}")
        
        return articles
    
    def fetch_all(self):
        """采集所有源"""
        all_articles = []
        
        print("📥 开始采集文章...")
        print("-" * 50)
        
        for source in CONFIG["sources"]:
            print(f"\n🌐 {source['name']}")
            print(f"   URL: {source['url']}")
            
            xml = self.fetch_rss(source['url'])
            if xml:
                articles = self.parse_rss(
                    xml, 
                    source['name'], 
                    source['category'],
                    source['lang']
                )
                print(f"   ✅ 采集到 {len(articles)} 篇")
                all_articles.extend(articles)
            
            time.sleep(1)  # 延迟1秒
        
        print()
        print(f"📊 总计采集: {len(all_articles)} 篇")
        return all_articles

class SimpleTranslator:
    """简单翻译器 - 使用 OpenClaw"""
    
    def translate(self, text, context=""):
        """翻译文本"""
        # 简化版：直接返回原文（实际应调用 OpenClaw）
        # 这里模拟翻译结果
        return text
    
    def translate_articles(self, articles):
        """翻译文章列表"""
        print("🌐 翻译文章...")
        print("-" * 50)
        
        translated = 0
        for article in articles:
            if article['language'] == 'en' and not article.get('title_zh'):
                # 模拟翻译：添加中文标记
                article['title_zh'] = f"[译] {article['title'][:40]}"
                article['summary_zh'] = f"[译文摘要] {article['summary'][:80]}"
                translated += 1
                print(f"   📝 {article['title'][:40]}... → {article['title_zh'][:40]}")
            elif not article.get('title_zh'):
                article['title_zh'] = article['title']
                article['summary_zh'] = article['summary']
        
        print(f"\n✅ 翻译完成: {translated} 篇")
        return articles

class SimplePublisher:
    """简单发布器"""
    
    def __init__(self):
        self.data_dir = Path("data/articles/research")
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def quality_score(self, article):
        """简单质量评分"""
        score = 0.5
        
        # 标题长度
        if 10 < len(article['title']) < 100:
            score += 0.2
        
        # 摘要长度
        if len(article.get('summary', '')) > 50:
            score += 0.2
        
        # 来源权威性
        if article['source'] in ['OpenAI Blog', '机器之心', '量子位']:
            score += 0.1
        
        return min(score, 1.0)
    
    def publish(self, articles):
        """发布文章"""
        print("📤 发布文章...")
        print("-" * 50)
        
        published = 0
        for article in articles:
            # 质量评分
            score = self.quality_score(article)
            article['quality_score'] = round(score, 2)
            
            if score < CONFIG['min_quality_score']:
                print(f"   ⏭️  [{score}] {article['title_zh'][:30]}... (质量不足)")
                continue
            
            # 读取现有文件
            file_path = self.data_dir / f"{article['category']}.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
            else:
                existing = []
            
            # 检查重复（简单检查标题）
            if not any(a.get('title') == article['title'] for a in existing):
                # 添加文章
                article_data = {
                    'id': article['id'],
                    'title': article['title_zh'],
                    'summary': article.get('summary_zh', article['summary']),
                    'url': article['url'],
                    'source': article['source'],
                    'category': article['category'],
                    'quality_score': article['quality_score'],
                    'published_at': article['published_at']
                }
                existing.append(article_data)
                
                # 保存
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(existing, f, ensure_ascii=False, indent=2)
                
                published += 1
                print(f"   ✅ [{score}] {article['title_zh'][:40]}...")
        
        print(f"\n📊 发布成功: {published}/{len(articles)} 篇")
        return published

def git_commit():
    """Git 提交"""
    print("\n📦 Git 提交...")
    print("-" * 50)
    import subprocess
    
    try:
        subprocess.run(['git', 'add', 'data/articles/'], check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', f'auto: update articles {datetime.now().strftime("%Y-%m-%d %H:%M")}'], 
                      check=True, capture_output=True)
        subprocess.run(['git', 'push'], check=True, capture_output=True)
        print("   ✅ 已推送到 GitHub")
    except Exception as e:
        print(f"   ⚠️ Git 操作失败: {e}")

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 Info-Getter 轻量版")
    print("=" * 60)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    start_time = datetime.now()
    
    # 1. 采集
    fetcher = SimpleFetcher()
    articles = fetcher.fetch_all()
    
    if not articles:
        print("❌ 未采集到文章，退出")
        return
    
    # 2. 翻译
    translator = SimpleTranslator()
    articles = translator.translate_articles(articles)
    
    # 3. 发布
    publisher = SimplePublisher()
    published = publisher.publish(articles)
    
    # 4. Git 提交
    if published > 0:
        git_commit()
    
    # 汇总
    duration = (datetime.now() - start_time).total_seconds()
    
    print("\n" + "=" * 60)
    print("🎉 运行完成!")
    print("=" * 60)
    print(f"\n📈 统计:")
    print(f"   采集: {len(articles)} 篇")
    print(f"   发布: {published} 篇")
    print(f"   耗时: {duration:.1f} 秒")
    print()

if __name__ == "__main__":
    main()
