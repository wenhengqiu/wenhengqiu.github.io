# -*- coding: utf-8 -*-
"""
翻译模块测试
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from translator import create_translator, translate_article, translate_articles, TranslationResult


def test_basic_translation():
    """测试基本翻译功能"""
    print("=" * 60)
    print("Test 1: Basic Translation (Mock)")
    print("=" * 60)
    
    translator = create_translator(use_mock=True)
    
    result = translator.translate(
        title="OpenAI Releases GPT-4o: A New Multimodal Model",
        summary="OpenAI has announced the release of GPT-4o, a new multimodal model that can process text, audio, and images. The model is available to all ChatGPT users."
    )
    
    print(f"Original Title: {result.original_title}")
    print(f"Translated Title: {result.title}")
    print(f"Original Summary: {result.original_summary}")
    print(f"Translated Summary: {result.summary}")
    print(f"Success: {result.success}")
    print()


def test_protected_terms():
    """测试专有名词保护"""
    print("=" * 60)
    print("Test 2: Protected Terms")
    print("=" * 60)
    
    translator = create_translator(use_mock=False)  # 使用真实翻译器测试保护逻辑
    
    # 测试专有名词保护
    text = "Tesla FSD and GPT-4 are developed by OpenAI and Tesla"
    protected, placeholders = translator._protect_terms(text)
    
    print(f"Original: {text}")
    print(f"Protected: {protected}")
    print(f"Placeholders: {placeholders}")
    
    # 恢复
    restored = translator._restore_terms(protected, placeholders)
    print(f"Restored: {restored}")
    print()


def test_length_limit():
    """测试长度限制"""
    print("=" * 60)
    print("Test 3: Length Limit")
    print("=" * 60)
    
    translator = create_translator(use_mock=True, max_title_length=20)
    
    long_title = "This is a very long title that should be truncated to fit within the limit"
    result = translator.translate(title=long_title)
    
    print(f"Original Length: {len(long_title)}")
    print(f"Translated Length: {len(result.title)}")
    print(f"Title: {result.title}")
    print()


def test_fallback():
    """测试降级策略"""
    print("=" * 60)
    print("Test 4: Fallback Strategy")
    print("=" * 60)
    
    # 创建一个会失败的模拟翻译器
    class FailingTranslator:
        def translate(self, title, summary=None, fallback_to_original=True):
            if fallback_to_original:
                return TranslationResult(
                    title=title,
                    summary=summary or "",
                    success=True,  # 降级后视为成功
                    original_title=title,
                    original_summary=summary
                )
            else:
                return TranslationResult(
                    title=title,
                    summary=summary or "",
                    success=False,
                    error_message="Translation failed",
                    original_title=title,
                    original_summary=summary
                )
    
    translator = FailingTranslator()
    
    # 测试降级开启
    result = translator.translate(
        title="Test Title",
        summary="Test Summary",
        fallback_to_original=True
    )
    print(f"With fallback: success={result.success}, title={result.title}")
    
    # 测试降级关闭
    result = translator.translate(
        title="Test Title",
        summary="Test Summary",
        fallback_to_original=False
    )
    print(f"Without fallback: success={result.success}, error={result.error_message}")
    print()


def test_batch_translation():
    """测试批量翻译"""
    print("=" * 60)
    print("Test 5: Batch Translation")
    print("=" * 60)
    
    articles = [
        {"title": "Article 1 about GPT", "summary": "Summary 1"},
        {"title": "Article 2 about Tesla FSD", "summary": "Summary 2"},
        {"title": "Article 3 about OpenAI", "summary": "Summary 3"},
    ]
    
    results = translate_articles(articles, use_mock=True)
    
    for i, result in enumerate(results):
        print(f"Article {i+1}:")
        print(f"  Original: {result.original_title}")
        print(f"  Translated: {result.title}")
    print()


def test_real_translation():
    """测试真实翻译（需要 OpenClaw Gateway 运行）"""
    print("=" * 60)
    print("Test 6: Real Translation (requires OpenClaw Gateway)")
    print("=" * 60)
    
    try:
        result = translate_article(
            title="OpenAI Releases GPT-4o: A Faster, Cheaper Multimodal Model",
            summary="OpenAI announced GPT-4o, a new AI model that is twice as fast and half the price of GPT-4 Turbo. It can process text, audio, and images in real-time."
        )
        
        print(f"Success: {result.success}")
        print(f"Title: {result.title}")
        print(f"Summary: {result.summary}")
        
    except Exception as e:
        print(f"Error (expected if Gateway not running): {e}")
    print()


if __name__ == "__main__":
    print("Running Translator Tests...\n")
    
    test_basic_translation()
    test_protected_terms()
    test_length_limit()
    test_fallback()
    test_batch_translation()
    
    # 可选：测试真实翻译（需要 Gateway 运行）
    # test_real_translation()
    
    print("All tests completed!")
