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
            # 1. 采集文章
            from info_getter.fetcher.core import Fetcher
            fetcher = Fetcher(self.config)
            articles = await fetcher.fetch_all()
            logger.info(f"📥 采集到 {len(articles)} 篇文章")
            
            # 2. 翻译文章
            from info_getter.translator.core import Translator
            translator = Translator()
            
            translated_articles = []
            for article in articles:
                try:
                    translated = translator.translate(article)
                    translated_articles.append(translated)
                except Exception as e:
                    logger.warning(f"翻译失败: {e}")
                    translated_articles.append(article)  # 保留原文
            
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
