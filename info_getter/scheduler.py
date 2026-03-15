#!/usr/bin/env python3
"""
Info-Getter 调度模块
负责任务调度、状态管理和主循环
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Scheduler:
    """任务调度器"""
    
    def __init__(self, config_path: str = "config/sources.yaml"):
        self.config = self._load_config(config_path)
        self.state = {
            "last_run": None,
            "total_articles": 0,
            "success_count": 0,
            "failure_count": 0
        }
        
    def _load_config(self, path: str) -> Dict:
        """加载配置"""
        import yaml
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    
    async def run_once(self):
        """执行一次采集任务"""
        logger.info("🚀 开始采集任务")
        start_time = datetime.now()
        
        try:
            # 1. RSS采集
            from info_getter.fetcher.core import Fetcher
            fetcher = Fetcher(self.config)
            articles = await fetcher.fetch_all()
            logger.info(f"📥 RSS采集: {len(articles)} 篇文章")
            
            # 2. Web爬虫采集（Playwright）
            logger.info("🌐 启动Web爬虫...")
            try:
                import subprocess
                result = subprocess.run(
                    ['/Library/Developer/CommandLineTools/usr/bin/python3', 
                     'scripts/crawl_playwright.py'],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                if result.returncode == 0:
                    logger.info("✅ Web爬虫完成")
                else:
                    logger.warning(f"⚠️ Web爬虫出错: {result.stderr[:200]}")
            except Exception as e:
                logger.warning(f"⚠️ Web爬虫失败: {e}")
            
            # 2. 翻译文章并转换为PRD v6.1格式
            from info_getter.translator.core import Translator
            translator = Translator()
            
            translated_articles = []
            for article in articles:
                try:
                    # 翻译标题和摘要
                    translation = translator.translate(
                        title=article.title,
                        summary=article.summary,
                        fallback_to_original=True
                    )
                    
                    # 构建符合PRD v6.1的文章对象
                    from info_getter.publisher.core import Article
                    
                    # 确定source类型
                    source_type_map = {
                        'official': 'official',
                        'tech_media': 'tech_media',
                        'research': 'research',
                        'social': 'social'
                    }
                    source_type = source_type_map.get(article.source_id, 'tech_media')
                    
                    prd_article = Article(
                        id=article.id,
                        title=article.title,
                        title_zh=translation.title if translation.success else article.title,
                        summary=article.summary or '',
                        summary_zh=translation.summary if translation.success else (article.summary or ''),
                        content=article.content or '',
                        category=article.category,
                        publish_date=article.published_at.isoformat() if article.published_at else datetime.now().isoformat(),
                        display_date=article.published_at.strftime('%Y-%m-%d') if article.published_at else datetime.now().strftime('%Y-%m-%d'),
                        source={'name': article.source_name, 'type': source_type},
                        url=article.url,
                        tags=[],
                        is_featured=False,
                        quality_score=0.0,  # 将在发布时计算
                        simhash='',
                        translated=translation.success
                    )
                    
                    translated_articles.append(prd_article)
                    
                except Exception as e:
                    logger.warning(f"翻译失败: {e}")
                    # 翻译失败时仍创建PRD格式文章，但使用原文
                    from info_getter.publisher.core import Article
                    prd_article = Article(
                        id=article.id,
                        title=article.title,
                        title_zh=article.title,  # 无翻译，使用原文
                        summary=article.summary or '',
                        summary_zh=article.summary or '',  # 无翻译，使用原文
                        content=article.content or '',
                        category=article.category,
                        publish_date=article.published_at.isoformat() if article.published_at else datetime.now().isoformat(),
                        display_date=article.published_at.strftime('%Y-%m-%d') if article.published_at else datetime.now().strftime('%Y-%m-%d'),
                        source={'name': article.source_name, 'type': 'tech_media'},
                        url=article.url,
                        tags=[],
                        is_featured=False,
                        quality_score=0.0,
                        simhash='',
                        translated=False
                    )
                    translated_articles.append(prd_article)
            
            logger.info(f"🌐 翻译完成 {len(translated_articles)} 篇")
            
            # 3. 发布文章
            from info_getter.publisher.core import Publisher
            publisher = Publisher()
            
            published_count = 0
            for article in translated_articles:
                try:
                    if publisher.publish(article):
                        published_count += 1
                except Exception as e:
                    logger.error(f"发布失败: {e}")
            
            logger.info(f"📤 发布成功 {published_count} 篇")
            
            # 更新状态
            self.state["last_run"] = start_time.isoformat()
            self.state["total_articles"] += len(articles)
            self.state["success_count"] += published_count
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ 任务完成，耗时 {duration:.1f} 秒")
            
            return {
                "success": True,
                "fetched": len(articles),
                "published": published_count,
                "duration": duration
            }
            
        except Exception as e:
            logger.error(f"❌ 任务失败: {e}")
            self.state["failure_count"] += 1
            return {
                "success": False,
                "error": str(e)
            }
    
    async def run_continuous(self, interval: int = 3600):
        """持续运行"""
        logger.info(f"🔄 启动持续模式，间隔 {interval} 秒")
        
        while True:
            try:
                result = await self.run_once()
                
                if result["success"]:
                    logger.info(f"⏳ 下次运行: {interval} 秒后")
                else:
                    logger.warning("⚠️ 本次运行失败，继续下次")
                
                await asyncio.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("👋 收到停止信号")
                break
            except Exception as e:
                logger.error(f"💥 意外错误: {e}")
                await asyncio.sleep(60)  # 出错后1分钟重试

async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--once', action='store_true', help='运行一次')
    parser.add_argument('--interval', type=int, default=3600, help='运行间隔(秒)')
    args = parser.parse_args()
    
    scheduler = Scheduler()
    
    if args.once:
        result = await scheduler.run_once()
        print(json.dumps(result, indent=2))
    else:
        await scheduler.run_continuous(args.interval)

if __name__ == "__main__":
    asyncio.run(main())
