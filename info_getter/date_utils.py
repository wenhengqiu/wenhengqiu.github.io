#!/usr/bin/env python3
"""
Info-Getter 文章日期处理模块
确保文章按正确的发布日期存储和检索
"""

from datetime import datetime, timedelta
from typing import Optional
import re


def parse_date(date_str: str) -> Optional[datetime]:
    """
    解析各种日期格式
    
    支持的格式:
    - %Y-%m-%d %H:%M:%S
    - %Y-%m-%dT%H:%M:%S
    - %Y-%m-%dT%H:%M:%SZ
    - %Y-%m-%dT%H:%M:%S%z
    - %a, %d %b %Y %H:%M:%S %z (RSS格式)
    - %Y-%m-%d
    - %B %d, %Y
    - %b %d, %Y
    """
    if not date_str:
        return None
    
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S GMT",
        "%Y-%m-%d",
        "%B %d, %Y",
        "%b %d, %Y",
        "%d %B %Y",
        "%d %b %Y",
        "%m/%d/%Y",
        "%Y/%m/%d",
    ]
    
    # 清理字符串
    date_str = date_str.strip()
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    # 尝试ISO格式
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except:
        pass
    
    return None


def is_recent_article(published_at: datetime, days: int = 30) -> bool:
    """
    检查文章是否在指定天数内发布
    
    Args:
        published_at: 发布日期
        days: 天数阈值（默认30天）
    
    Returns:
        是否是近期文章
    """
    if not published_at:
        return False
    
    cutoff_date = datetime.now() - timedelta(days=days)
    return published_at >= cutoff_date


def format_article_date(published_at: datetime) -> dict:
    """
    格式化文章日期为存储格式
    
    Returns:
        {
            'published_at': ISO格式,
            'display_date': 显示格式 YYYY-MM-DD,
            'year': 年份,
            'month': 月份,
            'day': 日期
        }
    """
    if not published_at:
        published_at = datetime.now()
    
    return {
        'published_at': published_at.isoformat(),
        'display_date': published_at.strftime('%Y-%m-%d'),
        'year': published_at.year,
        'month': published_at.month,
        'day': published_at.day
    }


def get_date_range(days: int = 30) -> tuple:
    """
    获取日期范围
    
    Returns:
        (开始日期, 结束日期)
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date


def filter_articles_by_date(articles: list, days: int = 30) -> list:
    """
    筛选指定天数内的文章
    
    Args:
        articles: 文章列表
        days: 天数阈值
    
    Returns:
        筛选后的文章列表
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    
    filtered = []
    for article in articles:
        pub_date = article.get('published_at')
        if pub_date:
            if isinstance(pub_date, str):
                pub_date = parse_date(pub_date)
            if pub_date and pub_date >= cutoff_date:
                filtered.append(article)
        else:
            # 没有日期的文章也保留（可能是新采集的）
            filtered.append(article)
    
    return filtered


def sort_articles_by_date(articles: list, reverse: bool = True) -> list:
    """
    按日期排序文章
    
    Args:
        articles: 文章列表
        reverse: 是否倒序（最新的在前）
    
    Returns:
        排序后的文章列表
    """
    def get_date(article):
        pub_date = article.get('published_at')
        if pub_date:
            if isinstance(pub_date, str):
                return parse_date(pub_date) or datetime.min
            return pub_date
        return datetime.min
    
    return sorted(articles, key=get_date, reverse=reverse)


# 测试
if __name__ == '__main__':
    # 测试日期解析
    test_dates = [
        "2024-03-15 10:30:00",
        "2024-03-15T10:30:00Z",
        "Fri, 15 Mar 2024 10:30:00 GMT",
        "March 15, 2024",
        "2024-03-15",
    ]
    
    print("日期解析测试:")
    for date_str in test_dates:
        result = parse_date(date_str)
        print(f"  {date_str:30s} -> {result}")
    
    # 测试日期范围
    start, end = get_date_range(30)
    print(f"\n近30天范围: {start.strftime('%Y-%m-%d')} 至 {end.strftime('%Y-%m-%d')}")
