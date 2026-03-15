#!/usr/bin/env python3
"""
Info-Getter Web爬虫模块
用于采集需要网页爬取的信息源
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import re
import time

logger = logging.getLogger(__name__)


class WebCrawler:
    """Web爬虫基类"""
    
    def __init__(self, timeout: int = 30, delay: float = 1.0):
        self.timeout = timeout
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch(self, url: str) -> Optional[str]:
        """获取网页内容"""
        try:
            time.sleep(self.delay)  # 礼貌延迟
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"获取失败 {url}: {e}")
            return None
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """解析日期字符串"""
        if not date_str:
            return None
        
        formats = [
            "%B %d, %Y",
            "%b %d, %Y",
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
            "%d %B %Y",
            "%d %b %Y",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except:
                continue
        
        return None


class DeepMindCrawler(WebCrawler):
    """DeepMind Blog 爬虫"""
    
    def crawl(self, cutoff_date: datetime) -> List[Dict]:
        """爬取DeepMind Blog文章"""
        articles = []
        base_url = "https://deepmind.google/discover/blog/"
        
        print(f"  🔍 爬取 DeepMind Blog...")
        
        html = self.fetch(base_url)
        if not html:
            return articles
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # 查找文章卡片
        cards = soup.find_all('div', class_=re.compile('card|post|article', re.I))
        
        for card in cards[:20]:  # 限制数量
            try:
                # 标题和链接
                title_elem = card.find(['h2', 'h3', 'a'], class_=re.compile('title|headline', re.I))
                if not title_elem:
                    title_elem = card.find('a')
                
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                link = title_elem.get('href', '')
                if link and not link.startswith('http'):
                    link = 'https://deepmind.google' + link
                
                # 日期
                date_elem = card.find(['time', 'span', 'div'], class_=re.compile('date|time', re.I))
                date_str = date_elem.get_text(strip=True) if date_elem else ''
                pub_date = self.parse_date(date_str)
                
                # 筛选时间
                if pub_date and pub_date < cutoff_date:
                    continue
                
                # 摘要
                summary_elem = card.find(['p', 'div'], class_=re.compile('summary|excerpt|description', re.I))
                summary = summary_elem.get_text(strip=True)[:300] if summary_elem else ''
                
                articles.append({
                    'id': f"deepmind_{hash(title) % 100000}",
                    'title': title,
                    'url': link,
                    'source': {'name': 'DeepMind Blog', 'type': 'official'},
                    'category': 'ai',
                    'published_at': pub_date.isoformat() if pub_date else datetime.now().isoformat(),
                    'summary': summary
                })
                
            except Exception as e:
                logger.warning(f"解析文章失败: {e}")
                continue
        
        print(f"    ✅ 获取 {len(articles)} 篇文章")
        return articles


class OpenAICrawler(WebCrawler):
    """OpenAI Blog 爬虫（备用，RSS为主）"""
    
    def crawl(self, cutoff_date: datetime) -> List[Dict]:
        """爬取OpenAI Blog（RSS已覆盖，此处为备用）"""
        return []  # RSS已覆盖


class FigureAICrawler(WebCrawler):
    """Figure AI 爬虫"""
    
    def crawl(self, cutoff_date: datetime) -> List[Dict]:
        """爬取Figure AI新闻"""
        articles = []
        url = "https://www.figure.ai/news"
        
        print(f"  🔍 爬取 Figure AI...")
        
        html = self.fetch(url)
        if not html:
            return articles
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # 查找新闻条目
        items = soup.find_all(['article', 'div', 'a'], class_=re.compile('news|post|item', re.I))
        
        for item in items[:15]:
            try:
                title_elem = item.find(['h2', 'h3', 'h4', 'span'])
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                if len(title) < 10:
                    continue
                
                # 链接
                link_elem = item.find('a', href=True)
                link = link_elem['href'] if link_elem else ''
                if link and not link.startswith('http'):
                    link = 'https://www.figure.ai' + link
                
                # 日期（Figure AI可能没有明确日期，使用当前时间）
                pub_date = datetime.now()
                
                articles.append({
                    'id': f"figure_{hash(title) % 100000}",
                    'title': title,
                    'url': link or 'https://www.figure.ai/news',
                    'source': {'name': 'Figure AI', 'type': 'official'},
                    'category': 'robotics',
                    'published_at': pub_date.isoformat(),
                    'summary': ''
                })
                
            except Exception as e:
                continue
        
        print(f"    ✅ 获取 {len(articles)} 篇文章")
        return articles


class TeslaAICrawler(WebCrawler):
    """Tesla AI/Optimus 爬虫"""
    
    def crawl(self, cutoff_date: datetime) -> List[Dict]:
        """爬取Tesla AI内容"""
        articles = []
        url = "https://www.tesla.com/AI"
        
        print(f"  🔍 爬取 Tesla AI...")
        
        html = self.fetch(url)
        if not html:
            return articles
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Tesla页面结构特殊，查找新闻或博客链接
        links = soup.find_all('a', href=re.compile('blog|news', re.I))
        
        for link in links[:10]:
            try:
                title = link.get_text(strip=True)
                if len(title) < 10:
                    continue
                
                href = link.get('href', '')
                if href and not href.startswith('http'):
                    href = 'https://www.tesla.com' + href
                
                articles.append({
                    'id': f"tesla_{hash(title) % 100000}",
                    'title': title,
                    'url': href or 'https://www.tesla.com/blog',
                    'source': {'name': 'Tesla AI', 'type': 'official'},
                    'category': 'robotics',
                    'published_at': datetime.now().isoformat(),
                    'summary': ''
                })
                
            except Exception as e:
                continue
        
        print(f"    ✅ 获取 {len(articles)} 篇文章")
        return articles


class WaymoCrawler(WebCrawler):
    """Waymo Blog 爬虫"""
    
    def crawl(self, cutoff_date: datetime) -> List[Dict]:
        """爬取Waymo Blog"""
        articles = []
        url = "https://waymo.com/blog/"
        
        print(f"  🔍 爬取 Waymo Blog...")
        
        html = self.fetch(url)
        if not html:
            return articles
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # 查找博客文章
        posts = soup.find_all('article', class_=re.compile('post|blog', re.I))
        
        for post in posts[:15]:
            try:
                title_elem = post.find(['h2', 'h3', 'h1'])
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                
                # 链接
                link_elem = post.find('a', href=True)
                link = link_elem['href'] if link_elem else ''
                if link and not link.startswith('http'):
                    link = 'https://waymo.com' + link
                
                # 日期
                date_elem = post.find('time') or post.find(class_=re.compile('date', re.I))
                date_str = date_elem.get_text(strip=True) if date_elem else ''
                pub_date = self.parse_date(date_str)
                
                if pub_date and pub_date < cutoff_date:
                    continue
                
                articles.append({
                    'id': f"waymo_{hash(title) % 100000}",
                    'title': title,
                    'url': link,
                    'source': {'name': 'Waymo Blog', 'type': 'official'},
                    'category': 'autonomous',
                    'published_at': pub_date.isoformat() if pub_date else datetime.now().isoformat(),
                    'summary': ''
                })
                
            except Exception as e:
                continue
        
        print(f"    ✅ 获取 {len(articles)} 篇文章")
        return articles


class AnthropicCrawler(WebCrawler):
    """Anthropic 爬虫"""
    
    def crawl(self, cutoff_date: datetime) -> List[Dict]:
        """爬取Anthropic新闻"""
        articles = []
        url = "https://www.anthropic.com/news"
        
        print(f"  🔍 爬取 Anthropic...")
        
        html = self.fetch(url)
        if not html:
            return articles
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # 查找新闻条目
        items = soup.find_all(['article', 'a', 'div'], class_=re.compile('news|post|item', re.I))
        
        for item in items[:15]:
            try:
                title_elem = item.find(['h2', 'h3', 'h4'])
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                if len(title) < 5:
                    continue
                
                link = item.get('href', '')
                if link and not link.startswith('http'):
                    link = 'https://www.anthropic.com' + link
                
                articles.append({
                    'id': f"anthropic_{hash(title) % 100000}",
                    'title': title,
                    'url': link or 'https://www.anthropic.com/news',
                    'source': {'name': 'Anthropic', 'type': 'official'},
                    'category': 'ai',
                    'published_at': datetime.now().isoformat(),
                    'summary': ''
                })
                
            except Exception as e:
                continue
        
        print(f"    ✅ 获取 {len(articles)} 篇文章")
        return articles


# 爬虫映射表
CRAWLERS = {
    'deepmind_blog': DeepMindCrawler,
    'figure_ai': FigureAICrawler,
    'tesla_optimus': TeslaAICrawler,
    'waymo_blog': WaymoCrawler,
    'anthropic_blog': AnthropicCrawler,
}


def crawl_web_source(source_id: str, source_config: dict, cutoff_date: datetime) -> List[Dict]:
    """
    爬取Web类型信息源
    
    Args:
        source_id: 信息源ID
        source_config: 信息源配置
        cutoff_date: 截止日期
    
    Returns:
        文章列表
    """
    crawler_class = CRAWLERS.get(source_id)
    
    if not crawler_class:
        logger.warning(f"未找到爬虫实现: {source_id}")
        return []
    
    try:
        crawler = crawler_class()
        return crawler.crawl(cutoff_date)
    except Exception as e:
        logger.error(f"爬虫执行失败 {source_id}: {e}")
        return []
