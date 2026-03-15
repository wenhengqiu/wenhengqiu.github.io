#!/usr/bin/env python3
"""
Info-Getter Selenium浏览器爬虫
用于采集JavaScript动态渲染的网站
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import time

logger = logging.getLogger(__name__)


class SeleniumCrawler:
    """Selenium浏览器爬虫基类"""
    
    def __init__(self, headless: bool = True, timeout: int = 30):
        self.timeout = timeout
        self.driver = None
        self.headless = headless
        self._init_driver()
    
    def _init_driver(self):
        """初始化浏览器驱动"""
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        
        options = Options()
        
        if self.headless:
            options.add_argument('--headless')
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        # 禁用图片和CSS加速加载
        prefs = {
            'profile.managed_default_content_settings.images': 2,
            'profile.managed_default_content_settings.stylesheets': 2,
        }
        options.add_experimental_option('prefs', prefs)
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(self.timeout)
            logger.info("✅ Selenium浏览器启动成功")
        except Exception as e:
            logger.error(f"❌ 浏览器启动失败: {e}")
            raise
    
    def fetch(self, url: str) -> bool:
        """加载网页"""
        try:
            self.driver.get(url)
            # 等待页面加载
            time.sleep(3)
            return True
        except Exception as e:
            logger.error(f"页面加载失败 {url}: {e}")
            return False
    
    def find_elements(self, by: By, value: str, timeout: int = 10):
        """查找元素"""
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((by, value))
            )
        except TimeoutException:
            return []
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """解析日期"""
        if not date_str:
            return None
        
        formats = [
            "%B %d, %Y",
            "%b %d, %Y",
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
            "%d %B %Y",
            "%d %b %Y",
            "%m/%d/%Y",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except:
                continue
        
        return None
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            logger.info("✅ 浏览器已关闭")


class DeepMindSeleniumCrawler(SeleniumCrawler):
    """DeepMind Blog Selenium爬虫"""
    
    def crawl(self, cutoff_date: datetime) -> List[Dict]:
        """爬取DeepMind Blog"""
        articles = []
        url = "https://deepmind.google/discover/blog/"
        
        print(f"  🔍 Selenium爬取 DeepMind Blog...")
        
        if not self.fetch(url):
            return articles
        
        try:
            # 等待文章卡片加载
            cards = self.find_elements(By.CSS_SELECTOR, 'article, .card, .post-item, [class*="post"]', timeout=15)
            
            if not cards:
                # 尝试其他选择器
                cards = self.driver.find_elements(By.TAG_NAME, 'article')
            
            print(f"    找到 {len(cards)} 个文章元素")
            
            for card in cards[:20]:
                try:
                    # 标题
                    title_elem = card.find_element(By.CSS_SELECTOR, 'h2, h3, .title, [class*="title"]')
                    title = title_elem.text.strip()
                    
                    if len(title) < 10:
                        continue
                    
                    # 链接
                    link_elem = card.find_element(By.CSS_SELECTOR, 'a')
                    href = link_elem.get_attribute('href')
                    
                    # 日期
                    date_elem = card.find_elements(By.CSS_SELECTOR, 'time, .date, [class*="date"]')
                    date_str = date_elem[0].text if date_elem else ''
                    pub_date = self.parse_date(date_str)
                    
                    # 时间筛选
                    if pub_date and pub_date < cutoff_date:
                        continue
                    
                    # 摘要
                    summary_elem = card.find_elements(By.CSS_SELECTOR, 'p, .summary, [class*="summary"]')
                    summary = summary_elem[0].text[:300] if summary_elem else ''
                    
                    articles.append({
                        'id': f"deepmind_{abs(hash(href)) % 100000}",
                        'title': title,
                        'url': href,
                        'source': {'name': 'DeepMind Blog', 'type': 'official'},
                        'category': 'ai',
                        'published_at': pub_date.isoformat() if pub_date else datetime.now().isoformat(),
                        'summary': summary
                    })
                    
                except NoSuchElementException:
                    continue
                except Exception as e:
                    logger.warning(f"解析文章失败: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"爬取失败: {e}")
        
        print(f"    ✅ 获取 {len(articles)} 篇文章")
        return articles


class FigureAISeleniumCrawler(SeleniumCrawler):
    """Figure AI Selenium爬虫"""
    
    def crawl(self, cutoff_date: datetime) -> List[Dict]:
        """爬取Figure AI"""
        articles = []
        url = "https://www.figure.ai/news"
        
        print(f"  🔍 Selenium爬取 Figure AI...")
        
        if not self.fetch(url):
            return articles
        
        try:
            # Figure AI可能有动态加载，等待一下
            time.sleep(5)
            
            # 查找新闻条目
            items = self.driver.find_elements(By.CSS_SELECTOR, 'article, .news-item, [class*="news"], [class*="post"]')
            
            if not items:
                items = self.driver.find_elements(By.TAG_NAME, 'a')
            
            print(f"    找到 {len(items)} 个元素")
            
            for item in items[:15]:
                try:
                    # 获取文本
                    text = item.text.strip()
                    if len(text) < 20 or len(text) > 200:
                        continue
                    
                    # 链接
                    href = item.get_attribute('href')
                    if not href or 'figure.ai' not in href:
                        continue
                    
                    articles.append({
                        'id': f"figure_{abs(hash(href)) % 100000}",
                        'title': text,
                        'url': href,
                        'source': {'name': 'Figure AI', 'type': 'official'},
                        'category': 'robotics',
                        'published_at': datetime.now().isoformat(),
                        'summary': ''
                    })
                    
                except Exception as e:
                    continue
            
        except Exception as e:
            logger.error(f"爬取失败: {e}")
        
        print(f"    ✅ 获取 {len(articles)} 篇文章")
        return articles


class WaymoSeleniumCrawler(SeleniumCrawler):
    """Waymo Blog Selenium爬虫"""
    
    def crawl(self, cutoff_date: datetime) -> List[Dict]:
        """爬取Waymo Blog"""
        articles = []
        url = "https://waymo.com/blog/"
        
        print(f"  🔍 Selenium爬取 Waymo Blog...")
        
        if not self.fetch(url):
            return articles
        
        try:
            # 等待文章加载
            posts = self.find_elements(By.CSS_SELECTOR, 'article, .post, [class*="post"]', timeout=15)
            
            print(f"    找到 {len(posts)} 篇文章")
            
            for post in posts[:15]:
                try:
                    # 标题
                    title_elem = post.find_element(By.CSS_SELECTOR, 'h2, h3, .title')
                    title = title_elem.text.strip()
                    
                    # 链接
                    link_elem = post.find_element(By.CSS_SELECTOR, 'a')
                    href = link_elem.get_attribute('href')
                    
                    # 日期
                    date_elems = post.find_elements(By.CSS_SELECTOR, 'time, .date')
                    date_str = date_elems[0].text if date_elems else ''
                    pub_date = self.parse_date(date_str)
                    
                    if pub_date and pub_date < cutoff_date:
                        continue
                    
                    articles.append({
                        'id': f"waymo_{abs(hash(href)) % 100000}",
                        'title': title,
                        'url': href,
                        'source': {'name': 'Waymo Blog', 'type': 'official'},
                        'category': 'autonomous',
                        'published_at': pub_date.isoformat() if pub_date else datetime.now().isoformat(),
                        'summary': ''
                    })
                    
                except Exception as e:
                    continue
            
        except Exception as e:
            logger.error(f"爬取失败: {e}")
        
        print(f"    ✅ 获取 {len(articles)} 篇文章")
        return articles


# 爬虫映射
SELENIUM_CRAWLERS = {
    'deepmind_blog': DeepMindSeleniumCrawler,
    'figure_ai': FigureAISeleniumCrawler,
    'waymo_blog': WaymoSeleniumCrawler,
}


def crawl_with_selenium(source_id: str, cutoff_date: datetime) -> List[Dict]:
    """
    使用Selenium爬取Web源
    
    Args:
        source_id: 信息源ID
        cutoff_date: 截止日期
    
    Returns:
        文章列表
    """
    crawler_class = SELENIUM_CRAWLERS.get(source_id)
    
    if not crawler_class:
        logger.warning(f"未找到Selenium爬虫: {source_id}")
        return []
    
    crawler = None
    try:
        crawler = crawler_class(headless=True)
        return crawler.crawl(cutoff_date)
    except Exception as e:
        logger.error(f"Selenium爬虫失败 {source_id}: {e}")
        return []
    finally:
        if crawler:
            crawler.close()


if __name__ == '__main__':
    # 测试
    from datetime import timedelta
    
    cutoff = datetime.now() - timedelta(days=30)
    
    print("🚀 测试Selenium爬虫")
    print("=" * 70)
    
    # 测试DeepMind
    articles = crawl_with_selenium('deepmind_blog', cutoff)
    print(f"\nDeepMind: {len(articles)} 篇文章")
    for a in articles[:3]:
        print(f"  - {a['title'][:50]}...")
