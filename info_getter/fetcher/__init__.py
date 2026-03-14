"""
Info-Getter Fetcher Module

分批并行采集信息源
"""

from .core import (
    Fetcher,
    Source,
    Article,
    FetchResult,
    SourceType,
    Priority,
    BaseParser,
    RSSParser,
    APIParser,
    WebParser,
)

__all__ = [
    'Fetcher',
    'Source',
    'Article',
    'FetchResult',
    'SourceType',
    'Priority',
    'BaseParser',
    'RSSParser',
    'APIParser',
    'WebParser',
]

__version__ = "1.0.0"
