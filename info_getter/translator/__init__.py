# -*- coding: utf-8 -*-
"""
Info-Getter Translator Module
翻译模块 - 使用 OpenClaw 大模型进行智能翻译

Usage:
    from translator import translate_article, translate_articles, create_translator
    
    # 单篇文章翻译
    result = translate_article(
        title="OpenAI Releases GPT-4o",
        summary="OpenAI has announced..."
    )
    print(result.title)  # 中文标题
    print(result.summary)  # 中文摘要
    
    # 批量翻译
    articles = [
        {"title": "Title 1", "summary": "Summary 1"},
        {"title": "Title 2", "summary": "Summary 2"},
    ]
    results = translate_articles(articles)
"""

from .core import (
    OpenClawTranslator,
    MockTranslator,
    TranslatorConfig,
    TranslationResult,
    create_translator,
    translate_article,
    translate_articles,
)

__version__ = "1.0.0"
__all__ = [
    "OpenClawTranslator",
    "MockTranslator", 
    "TranslatorConfig",
    "TranslationResult",
    "create_translator",
    "translate_article",
    "translate_articles",
]
