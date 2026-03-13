"""
Info-Getter Publisher Module

自动发布文章到 GitHub，支持 SimHash 去重和质量评分过滤
"""

from .core import (
    Article,
    SimHash,
    QualityScorer,
    Publisher,
    publish_articles,
    publish_single_article
)

__all__ = [
    'Article',
    'SimHash',
    'QualityScorer',
    'Publisher',
    'publish_articles',
    'publish_single_article'
]

__version__ = '1.0.0'
