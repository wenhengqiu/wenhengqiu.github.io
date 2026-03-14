"""
Info-Getter Fetcher Core Module
分批并行采集51个信息源

特性:
- asyncio + aiohttp 异步采集
- 支持 RSS、API、网页三种类型
- 分批并行: 每批12个,批次间延迟2秒
- 重试机制和错误处理
"""

import asyncio
import aiohttp
import yaml
import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable
from datetime import datetime
from enum import Enum
import logging
import hashlib
from abc import ABC, abstractmethod

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SourceType(Enum):
    """信息源类型"""
    RSS = "rss"
    API = "api"
    WEB = "web"


class Priority(Enum):
    """优先级"""
    P0 = "p0"
    P1 = "p1"
    P2 = "p2"


@dataclass
class Source:
    """信息源配置"""
    id: str
    name: str
    url: str
    category: str
    priority: Priority
    type: SourceType = SourceType.RSS
    language: str = "en"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Source':
        return cls(
            id=data['id'],
            name=data['name'],
            url=data['url'],
            category=data.get('category', 'general'),
            priority=Priority(data.get('priority', 'p1')),
            type=SourceType(data.get('type', 'rss')),
            language=data.get('language', 'en')
        )


@dataclass
class Article:
    """文章数据"""
    title: str
    url: str
    source_id: str
    source_name: str
    published_at: Optional[datetime] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None
    category: str = "general"
    language: str = "en"
    fetched_at: datetime = field(default_factory=datetime.now)
    
    @property
    def id(self) -> str:
        """生成唯一ID"""
        content = f"{self.source_id}:{self.url}"
        return hashlib.md5(content.encode()).hexdigest()


@dataclass
class FetchResult:
    """采集结果"""
    source: Source
    articles: List[Article] = field(default_factory=list)
    success: bool = False
    error: Optional[str] = None
    retry_count: int = 0
    fetch_time_ms: float = 0.0


class BaseParser(ABC):
    """基础解析器"""
    
    @abstractmethod
    async def parse(self, content: str, source: Source) -> List[Article]:
        """解析内容返回文章列表"""
        pass


class RSSParser(BaseParser):
    """RSS解析器"""
    
    async def parse(self, content: str, source: Source) -> List[Article]:
        """解析RSS XML内容"""
        articles = []
        try:
            root = ET.fromstring(content)
            
            # 处理不同RSS格式
            channel = root.find('.//channel')
            if channel is not None:
                items = channel.findall('.//item')
            else:
                items = root.findall('.//item')
            
            # 处理Atom格式
            if not items:
                items = root.findall('.//{http://www.w3.org/2005/Atom}entry')
            
            for item in items[:20]:  # 限制每源20篇文章
                article = self._parse_item(item, source)
                if article:
                    articles.append(article)
                    
        except ET.ParseError as e:
            logger.error(f"RSS解析错误 {source.name}: {e}")
        except Exception as e:
            logger.error(f"解析异常 {source.name}: {e}")
            
        return articles
    
    def _parse_item(self, item: ET.Element, source: Source) -> Optional[Article]:
        """解析单个RSS条目"""
        try:
            # 获取标题
            title_elem = item.find('title')
            if title_elem is None:
                title_elem = item.find('.//{http://www.w3.org/2005/Atom}title')
            title = title_elem.text if title_elem is not None else "无标题"
            
            # 获取链接
            link_elem = item.find('link')
            if link_elem is None:
                link_elem = item.find('.//{http://www.w3.org/2005/Atom}link')
            url = link_elem.text if link_elem is not None else ""
            if not url and link_elem is not None:
                url = link_elem.get('href', '')
            
            # 获取描述/摘要
            desc_elem = item.find('description') or item.find('summary')
            if desc_elem is None:
                desc_elem = item.find('.//{http://www.w3.org/2005/Atom}summary')
            summary = desc_elem.text if desc_elem is not None else None
            
            # 获取发布时间
            pub_date = None
            date_elem = item.find('pubDate') or item.find('published')
            if date_elem is None:
                date_elem = item.find('.//{http://www.w3.org/2005/Atom}published')
            if date_elem is not None and date_elem.text:
                pub_date = self._parse_date(date_elem.text)
            
            # 获取作者
            author_elem = item.find('author') or item.find('creator')
            if author_elem is None:
                author_elem = item.find('.//{http://www.w3.org/2005/Atom}author')
            author = author_elem.text if author_elem is not None else None
            
            return Article(
                title=title.strip() if title else "无标题",
                url=url.strip() if url else "",
                source_id=source.id,
                source_name=source.name,
                published_at=pub_date,
                summary=summary.strip() if summary else None,
                author=author.strip() if author else None,
                category=source.category,
                language=source.language
            )
        except Exception as e:
            logger.warning(f"解析条目失败 {source.name}: {e}")
            return None
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """解析日期字符串"""
        formats = [
            "%a, %d %b %Y %H:%M:%S %z",
            "%a, %d %b %Y %H:%M:%S GMT",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        return None


class APIParser(BaseParser):
    """API解析器 (用于Hacker News等)"""
    
    async def parse(self, content: str, source: Source) -> List[Article]:
        """解析API返回的JSON内容"""
        articles = []
        try:
            data = json.loads(content)
            
            if source.id == "hackernews":
                articles = await self._parse_hackernews(data, source)
            else:
                # 通用API解析
                articles = self._parse_generic_api(data, source)
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析错误 {source.name}: {e}")
        except Exception as e:
            logger.error(f"API解析异常 {source.name}: {e}")
            
        return articles
    
    async def _parse_hackernews(self, data: Any, source: Source) -> List[Article]:
        """解析Hacker News数据"""
        articles = []
        # HN API返回的是故事ID列表,需要逐个获取
        if isinstance(data, list):
            top_ids = data[:20]  # 前20个
            # 这里简化处理,实际应该并发获取每个故事的详情
            for story_id in top_ids[:5]:  # 限制5个避免过多请求
                articles.append(Article(
                    title=f"HN Story {story_id}",
                    url=f"https://news.ycombinator.com/item?id={story_id}",
                    source_id=source.id,
                    source_name=source.name,
                    category=source.category,
                    language=source.language
                ))
        return articles
    
    def _parse_generic_api(self, data: Any, source: Source) -> List[Article]:
        """通用API数据解析"""
        articles = []
        if isinstance(data, list):
            for item in data[:20]:
                if isinstance(item, dict):
                    articles.append(Article(
                        title=item.get('title', '无标题'),
                        url=item.get('url', item.get('link', '')),
                        source_id=source.id,
                        source_name=source.name,
                        published_at=self._parse_api_date(item.get('published')),
                        summary=item.get('summary') or item.get('description'),
                        author=item.get('author'),
                        category=source.category,
                        language=source.language
                    ))
        return articles
    
    def _parse_api_date(self, date_val: Any) -> Optional[datetime]:
        """解析API日期"""
        if not date_val:
            return None
        if isinstance(date_val, (int, float)):
            return datetime.fromtimestamp(date_val)
        if isinstance(date_val, str):
            try:
                return datetime.fromisoformat(date_val.replace('Z', '+00:00'))
            except:
                pass
        return None


class WebParser(BaseParser):
    """网页解析器 (用于需要爬取的网页)"""
    
    async def parse(self, content: str, source: Source) -> List[Article]:
        """解析网页HTML内容"""
        # 这里简化处理,实际可以使用BeautifulSoup等库
        # 返回空列表表示需要进一步实现
        logger.warning(f"网页解析器尚未完全实现: {source.name}")
        return []


class Fetcher:
    """
    分批并行采集器
    
    特性:
    - 分批并行: 每批batch_size个源
    - 批次间延迟: batch_delay秒
    - 重试机制: 失败自动重试
    - 错误处理: 详细错误记录
    """
    
    def __init__(
        self,
        config_path: str,
        batch_size: int = 12,
        batch_delay: float = 2.0,
        timeout: int = 30,
        retry_times: int = 3,
        concurrency: int = 10
    ):
        self.config_path = config_path
        self.batch_size = batch_size
        self.batch_delay = batch_delay
        self.timeout = timeout
        self.retry_times = retry_times
        self.concurrency = concurrency
        
        self.sources: List[Source] = []
        self.results: List[FetchResult] = []
        
        # 解析器映射
        self.parsers: Dict[SourceType, BaseParser] = {
            SourceType.RSS: RSSParser(),
            SourceType.API: APIParser(),
            SourceType.WEB: WebParser(),
        }
        
        # 加载配置
        self._load_config()
    
    def _load_config(self):
        """加载信息源配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 从配置中读取设置
            fetch_settings = config.get('fetch_settings', {})
            self.batch_size = fetch_settings.get('batch_size', self.batch_size)
            self.batch_delay = fetch_settings.get('batch_delay', self.batch_delay)
            self.timeout = fetch_settings.get('timeout', self.timeout)
            self.retry_times = fetch_settings.get('retry_times', self.retry_times)
            
            # 加载信息源
            for src_data in config.get('sources', []):
                self.sources.append(Source.from_dict(src_data))
            
            logger.info(f"加载了 {len(self.sources)} 个信息源")
            
        except Exception as e:
            logger.error(f"配置加载失败: {e}")
            raise
    
    async def fetch_source(
        self, 
        session: aiohttp.ClientSession, 
        source: Source
    ) -> FetchResult:
        """
        采集单个信息源
        
        Args:
            session: aiohttp会话
            source: 信息源配置
            
        Returns:
            FetchResult: 采集结果
        """
        result = FetchResult(source=source)
        start_time = asyncio.get_event_loop().time()
        
        headers = {
            'User-Agent': 'Info-Getter/1.0 (RSS Aggregator)',
            'Accept': 'application/rss+xml, application/xml, text/xml, application/json, text/html, */*',
        }
        
        for attempt in range(self.retry_times):
            try:
                logger.debug(f"采集 {source.name} (尝试 {attempt + 1}/{self.retry_times})")
                
                async with session.get(
                    source.url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    ssl=False  # 某些RSS源SSL证书有问题
                ) as response:
                    
                    if response.status == 200:
                        content = await response.text()
                        
                        # 使用对应解析器
                        parser = self.parsers.get(source.type, self.parsers[SourceType.RSS])
                        articles = await parser.parse(content, source)
                        
                        result.articles = articles
                        result.success = True
                        result.retry_count = attempt
                        logger.info(f"✓ {source.name}: 获取 {len(articles)} 篇文章")
                        break
                        
                    else:
                        error_msg = f"HTTP {response.status}"
                        logger.warning(f"✗ {source.name}: {error_msg}")
                        result.error = error_msg
                        
            except asyncio.TimeoutError:
                error_msg = f"超时 (>{self.timeout}s)"
                logger.warning(f"✗ {source.name}: {error_msg}")
                result.error = error_msg
                
            except aiohttp.ClientError as e:
                error_msg = f"网络错误: {str(e)}"
                logger.warning(f"✗ {source.name}: {error_msg}")
                result.error = error_msg
                
            except Exception as e:
                error_msg = f"异常: {str(e)}"
                logger.error(f"✗ {source.name}: {error_msg}")
                result.error = error_msg
            
            # 重试前等待
            if attempt < self.retry_times - 1:
                wait_time = (attempt + 1) * 2  # 指数退避
                logger.debug(f"{source.name}: {wait_time}s后重试...")
                await asyncio.sleep(wait_time)
        
        result.fetch_time_ms = (asyncio.get_event_loop().time() - start_time) * 1000
        return result
    
    async def fetch_batch(
        self,
        session: aiohttp.ClientSession,
        batch: List[Source]
    ) -> List[FetchResult]:
        """
        并行采集一批信息源
        
        Args:
            session: aiohttp会话
            batch: 本批次的信息源列表
            
        Returns:
            List[FetchResult]: 采集结果列表
        """
        semaphore = asyncio.Semaphore(self.concurrency)
        
        async def fetch_with_limit(source: Source) -> FetchResult:
            async with semaphore:
                return await self.fetch_source(session, source)
        
        tasks = [fetch_with_limit(source) for source in batch]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常结果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"任务异常 {batch[i].name}: {result}")
                processed_results.append(FetchResult(
                    source=batch[i],
                    success=False,
                    error=str(result)
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def fetch_all(self) -> List[FetchResult]:
        """
        分批并行采集所有信息源
        
        Returns:
            List[FetchResult]: 所有采集结果
        """
        all_results = []
        
        # 按优先级排序 (P0优先)
        sorted_sources = sorted(
            self.sources,
            key=lambda s: 0 if s.priority == Priority.P0 else 1
        )
        
        # 分批处理
        batches = [
            sorted_sources[i:i + self.batch_size]
            for i in range(0, len(sorted_sources), self.batch_size)
        ]
        
        logger.info(f"开始采集: {len(self.sources)} 个源, {len(batches)} 批次, 每批 {self.batch_size} 个")
        
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=10,
            ttl_dns_cache=300,
            use_dns_cache=True,
        )
        
        async with aiohttp.ClientSession(connector=connector) as session:
            for batch_idx, batch in enumerate(batches):
                logger.info(f"\n--- 批次 {batch_idx + 1}/{len(batches)} ({len(batch)} 个源) ---")
                
                batch_results = await self.fetch_batch(session, batch)
                all_results.extend(batch_results)
                
                # 统计本批次
                success_count = sum(1 for r in batch_results if r.success)
                logger.info(f"批次完成: {success_count}/{len(batch)} 成功")
                
                # 批次间延迟 (最后一批不需要)
                if batch_idx < len(batches) - 1:
                    logger.info(f"等待 {self.batch_delay}s 后开始下一批次...")
                    await asyncio.sleep(self.batch_delay)
        
        self.results = all_results
        return all_results
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取采集统计信息"""
        if not self.results:
            return {}
        
        total = len(self.results)
        success = sum(1 for r in self.results if r.success)
        failed = total - success
        total_articles = sum(len(r.articles) for r in self.results)
        avg_time = sum(r.fetch_time_ms for r in self.results) / total if total > 0 else 0
        
        # 按类型统计
        by_type = {}
        for r in self.results:
            key = r.source.type.value
            if key not in by_type:
                by_type[key] = {"total": 0, "success": 0}
            by_type[key]["total"] += 1
            if r.success:
                by_type[key]["success"] += 1
        
        # 按优先级统计
        by_priority = {}
        for r in self.results:
            key = r.source.priority.value
            if key not in by_priority:
                by_priority[key] = {"total": 0, "success": 0}
            by_priority[key]["total"] += 1
            if r.success:
                by_priority[key]["success"] += 1
        
        return {
            "total_sources": total,
            "success": success,
            "failed": failed,
            "success_rate": f"{success/total*100:.1f}%" if total > 0 else "0%",
            "total_articles": total_articles,
            "avg_fetch_time_ms": round(avg_time, 2),
            "by_type": by_type,
            "by_priority": by_priority,
        }
    
    def get_all_articles(self) -> List[Article]:
        """获取所有采集到的文章"""
        articles = []
        for result in self.results:
            if result.success:
                articles.extend(result.articles)
        return articles
    
    def get_failed_sources(self) -> List[Source]:
        """获取采集失败的信息源"""
        return [r.source for r in self.results if not r.success]


async def main():
    """主函数 - 演示用法"""
    config_path = "/Users/jarvis/.openclaw/info-getter-sources-complete.yaml"
    
    fetcher = Fetcher(config_path)
    
    # 执行采集
    results = await fetcher.fetch_all()
    
    # 输出统计
    stats = fetcher.get_statistics()
    print("\n" + "="*50)
    print("采集统计")
    print("="*50)
    print(f"总源数: {stats['total_sources']}")
    print(f"成功: {stats['success']}")
    print(f"失败: {stats['failed']}")
    print(f"成功率: {stats['success_rate']}")
    print(f"总文章数: {stats['total_articles']}")
    print(f"平均采集时间: {stats['avg_fetch_time_ms']}ms")
    
    print("\n按类型统计:")
    for t, s in stats['by_type'].items():
        print(f"  {t}: {s['success']}/{s['total']}")
    
    print("\n按优先级统计:")
    for p, s in stats['by_priority'].items():
        print(f"  {p}: {s['success']}/{s['total']}")
    
    # 显示失败源
    failed = fetcher.get_failed_sources()
    if failed:
        print("\n失败的信息源:")
        for src in failed:
            result = next(r for r in results if r.source.id == src.id)
            print(f"  - {src.name}: {result.error}")
    
    # 显示部分文章
    articles = fetcher.get_all_articles()
    if articles:
        print(f"\n最新文章 (显示前5篇):")
        for art in articles[:5]:
            print(f"  - [{art.source_name}] {art.title[:60]}...")


if __name__ == "__main__":
    asyncio.run(main())
