# Info-Getter MongoDB 数据库模块
# 用于存储采集的文章、信息源、日志和统计信息

from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, ConnectionFailure
import os
import logging

logger = logging.getLogger(__name__)


class InfoGetterDB:
    """Info-Getter MongoDB 数据库管理类"""
    
    def __init__(self, connection_string: str = None, db_name: str = "infgetter_db"):
        """
        初始化数据库连接
        
        Args:
            connection_string: MongoDB连接字符串，默认从环境变量获取
            db_name: 数据库名称
        """
        self.connection_string = connection_string or os.getenv(
            "MONGODB_URI", 
            "mongodb://localhost:27017"
        )
        self.db_name = db_name
        self.client = None
        self.db = None
        
        # 集合引用
        self.articles = None
        self.sources = None
        self.logs = None
        self.stats = None
        
        self._connect()
    
    def _connect(self):
        """建立数据库连接"""
        try:
            self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
            self.db = self.client[self.db_name]
            
            # 初始化集合
            self.articles = self.db["articles"]
            self.sources = self.db["sources"]
            self.logs = self.db["logs"]
            self.stats = self.db["stats"]
            
            # 创建索引
            self._create_indexes()
            
            logger.info(f"✅ MongoDB连接成功: {self.db_name}")
            
        except ConnectionFailure as e:
            logger.error(f"❌ MongoDB连接失败: {e}")
            raise
    
    def _create_indexes(self):
        """创建数据库索引"""
        # 文章集合索引
        self.articles.create_index([("id", ASCENDING)], unique=True)
        self.articles.create_index([("category", ASCENDING)])
        self.articles.create_index([("quality_score", DESCENDING)])
        self.articles.create_index([("published_at", DESCENDING)])
        self.articles.create_index([("source.name", ASCENDING)])
        self.articles.create_index([("tags", ASCENDING)])
        
        # 信息源集合索引
        self.sources.create_index([("id", ASCENDING)], unique=True)
        self.sources.create_index([("category", ASCENDING)])
        self.sources.create_index([("priority", ASCENDING)])
        
        # 日志集合索引
        self.logs.create_index([("timestamp", DESCENDING)])
        self.logs.create_index([("run_id", ASCENDING)])
        
        logger.info("✅ 数据库索引创建完成")
    
    def save_article(self, article: Dict[str, Any]) -> bool:
        """
        保存单篇文章
        
        Args:
            article: 文章数据字典，符合PRD v6.1格式
            
        Returns:
            是否保存成功
        """
        try:
            # 添加元数据
            article["created_at"] = datetime.now().isoformat()
            article["updated_at"] = article["created_at"]
            
            # 使用upsert，避免重复
            result = self.articles.update_one(
                {"id": article["id"]},
                {"$set": article, "$setOnInsert": {"created_at": article["created_at"]}},
                upsert=True
            )
            
            if result.upserted_id:
                logger.info(f"✅ 新文章入库: {article.get('title_zh', article.get('title', '无标题'))[:30]}...")
                return True
            else:
                logger.debug(f"📝 文章已存在，更新: {article['id']}")
                return True
                
        except Exception as e:
            logger.error(f"❌ 文章保存失败: {e}")
            return False
    
    def save_articles(self, articles: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        批量保存文章
        
        Args:
            articles: 文章列表
            
        Returns:
            统计结果 {"success": x, "failed": y, "duplicates": z}
        """
        stats = {"success": 0, "failed": 0, "duplicates": 0}
        
        for article in articles:
            try:
                article["created_at"] = datetime.now().isoformat()
                article["updated_at"] = article["created_at"]
                
                result = self.articles.update_one(
                    {"id": article["id"]},
                    {"$set": article, "$setOnInsert": {"created_at": article["created_at"]}},
                    upsert=True
                )
                
                if result.upserted_id:
                    stats["success"] += 1
                else:
                    stats["duplicates"] += 1
                    
            except Exception as e:
                logger.error(f"❌ 批量保存失败: {e}")
                stats["failed"] += 1
        
        logger.info(f"📊 批量保存完成: 新增{stats['success']}, 重复{stats['duplicates']}, 失败{stats['failed']}")
        return stats
    
    def get_article_by_id(self, article_id: str) -> Optional[Dict]:
        """根据ID获取文章"""
        return self.articles.find_one({"id": article_id}, {"_id": 0})
    
    def get_articles_by_category(self, category: str, limit: int = 100) -> List[Dict]:
        """
        按分类获取文章
        
        Args:
            category: 分类名称 (ai/robotics/autonomous/zhuoyu)
            limit: 返回数量限制
            
        Returns:
            文章列表
        """
        cursor = self.articles.find(
            {"category": category},
            {"_id": 0}
        ).sort("published_at", DESCENDING).limit(limit)
        
        return list(cursor)
    
    def get_top_articles(self, category: str = None, min_score: float = 0.8, limit: int = 10) -> List[Dict]:
        """
        获取高质量文章（TOP10候选）
        
        Args:
            category: 分类筛选（可选）
            min_score: 最低质量分
            limit: 返回数量
            
        Returns:
            高质量文章列表
        """
        query = {"quality_score": {"$gte": min_score}}
        if category:
            query["category"] = category
        
        cursor = self.articles.find(
            query,
            {"_id": 0}
        ).sort("quality_score", DESCENDING).limit(limit)
        
        return list(cursor)
    
    def get_recent_articles(self, hours: int = 24, category: str = None) -> List[Dict]:
        """
        获取最近N小时的文章
        
        Args:
            hours: 小时数
            category: 分类筛选（可选）
            
        Returns:
            文章列表
        """
        from datetime import timedelta
        
        cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        query = {"published_at": {"$gte": cutoff_time}}
        if category:
            query["category"] = category
        
        cursor = self.articles.find(
            query,
            {"_id": 0}
        ).sort("published_at", DESCENDING)
        
        return list(cursor)
    
    def search_articles(self, keyword: str, limit: int = 50) -> List[Dict]:
        """
        搜索文章
        
        Args:
            keyword: 搜索关键词
            limit: 返回数量限制
            
        Returns:
            匹配的文章列表
        """
        query = {
            "$or": [
                {"title": {"$regex": keyword, "$options": "i"}},
                {"title_zh": {"$regex": keyword, "$options": "i"}},
                {"summary": {"$regex": keyword, "$options": "i"}},
                {"summary_zh": {"$regex": keyword, "$options": "i"}},
                {"tags": keyword}
            ]
        }
        
        cursor = self.articles.find(query, {"_id": 0}).limit(limit)
        return list(cursor)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取文章统计信息
        
        Returns:
            统计字典
        """
        total = self.articles.count_documents({})
        
        # 按分类统计
        category_stats = list(self.articles.aggregate([
            {"$group": {"_id": "$category", "count": {"$sum": 1}}}
        ]))
        
        # 按来源统计
        source_stats = list(self.articles.aggregate([
            {"$group": {"_id": "$source.name", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]))
        
        # 平均质量分
        avg_quality = list(self.articles.aggregate([
            {"$group": {"_id": None, "avg": {"$avg": "$quality_score"}}}
        ]))
        
        # 今日新增
        from datetime import timedelta
        today_start = (datetime.now() - timedelta(days=1)).isoformat()
        today_count = self.articles.count_documents({"created_at": {"$gte": today_start}})
        
        return {
            "total_articles": total,
            "today_articles": today_count,
            "avg_quality_score": avg_quality[0]["avg"] if avg_quality else 0,
            "by_category": {item["_id"]: item["count"] for item in category_stats},
            "top_sources": [{"name": item["_id"], "count": item["count"]} for item in source_stats]
        }
    
    def save_source(self, source: Dict[str, Any]) -> bool:
        """保存信息源配置"""
        try:
            self.sources.update_one(
                {"id": source["id"]},
                {"$set": source},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"❌ 信息源保存失败: {e}")
            return False
    
    def get_sources(self, category: str = None, priority: str = None) -> List[Dict]:
        """获取信息源列表"""
        query = {}
        if category:
            query["category"] = category
        if priority:
            query["priority"] = priority
        
        return list(self.sources.find(query, {"_id": 0}))
    
    def log_fetch(self, run_id: str, source_id: str, status: str, 
                  articles_count: int = 0, error: str = None):
        """记录采集日志"""
        log_entry = {
            "run_id": run_id,
            "source_id": source_id,
            "status": status,  # success/failed
            "articles_count": articles_count,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        
        self.logs.insert_one(log_entry)
    
    def get_logs(self, run_id: str = None, limit: int = 100) -> List[Dict]:
        """获取采集日志"""
        query = {}
        if run_id:
            query["run_id"] = run_id
        
        cursor = self.logs.find(query, {"_id": 0}).sort("timestamp", DESCENDING).limit(limit)
        return list(cursor)
    
    def close(self):
        """关闭数据库连接"""
        if self.client:
            self.client.close()
            logger.info("✅ MongoDB连接已关闭")


# 单例模式，全局数据库实例
_db_instance = None

def get_db(connection_string: str = None) -> InfoGetterDB:
    """获取数据库实例（单例）"""
    global _db_instance
    if _db_instance is None:
        _db_instance = InfoGetterDB(connection_string)
    return _db_instance


def reset_db():
    """重置数据库实例（用于测试）"""
    global _db_instance
    if _db_instance:
        _db_instance.close()
    _db_instance = None
