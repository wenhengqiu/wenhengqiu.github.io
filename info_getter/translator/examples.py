# -*- coding: utf-8 -*-
"""
翻译模块使用示例

演示如何使用 Info-Getter 翻译模块进行文章翻译
"""

from translator import (
    create_translator,
    translate_article,
    translate_articles,
    TranslatorConfig,
)


def example_1_basic_usage():
    """示例1：基本用法"""
    print("=" * 60)
    print("示例 1: 基本用法")
    print("=" * 60)
    
    # 翻译单篇文章
    result = translate_article(
        title="OpenAI Releases GPT-4o: A New Multimodal Model",
        summary="OpenAI has announced the release of GPT-4o, a new multimodal model that can process text, audio, and images. The model is available to all ChatGPT users."
    )
    
    print(f"原文标题: {result.original_title}")
    print(f"中文标题: {result.title}")
    print(f"原文摘要: {result.original_summary}")
    print(f"中文摘要: {result.summary}")
    print(f"翻译状态: {'成功' if result.success else '失败'}")
    print()


def example_2_custom_config():
    """示例2：自定义配置"""
    print("=" * 60)
    print("示例 2: 自定义配置")
    print("=" * 60)
    
    # 创建自定义翻译器
    translator = create_translator(
        model="moonshot/kimi-k2.5",  # 指定模型
        max_title_length=15,          # 标题限制15字
        max_summary_length=80,        # 摘要限制80字
        protected_terms={"OpenAI", "GPT", "ChatGPT", "API"}  # 自定义保护词
    )
    
    result = translator.translate(
        title="Building AI Applications with OpenAI API",
        summary="Learn how to build powerful AI applications using the OpenAI API and GPT models."
    )
    
    print(f"标题 ({len(result.title)}字): {result.title}")
    print(f"摘要 ({len(result.summary)}字): {result.summary}")
    print()


def example_3_batch_translation():
    """示例3：批量翻译"""
    print("=" * 60)
    print("示例 3: 批量翻译")
    print("=" * 60)
    
    # 准备多篇文章
    articles = [
        {
            "title": "Tesla FSD Beta 12.3 Released",
            "summary": "Tesla has started rolling out FSD Beta 12.3 to customers with significant improvements in urban driving."
        },
        {
            "title": "Google DeepMind Announces Gemini 1.5",
            "summary": "Google DeepMind has announced Gemini 1.5 with a breakthrough in long-context understanding, supporting up to 1 million tokens."
        },
        {
            "title": "Waymo Expands to Los Angeles",
            "summary": "Waymo is expanding its autonomous ride-hailing service to Los Angeles, making it the third city after Phoenix and San Francisco."
        },
    ]
    
    # 批量翻译
    results = translate_articles(articles)
    
    for i, result in enumerate(results, 1):
        print(f"文章 {i}:")
        print(f"  原文: {result.original_title}")
        print(f"  译文: {result.title}")
        print(f"  状态: {'✓' if result.success else '✗'}")
        print()


def example_4_protected_terms():
    """示例4：专有名词保护"""
    print("=" * 60)
    print("示例 4: 专有名词保护")
    print("=" * 60)
    
    translator = create_translator()
    
    # 包含多个专有名词的文本
    text = "Tesla FSD vs Waymo: A Comparison of Self-Driving Technologies"
    
    print(f"原文: {text}")
    print(f"保护的专有名词:")
    
    # 检查哪些词会被保护
    for term in ["Tesla", "FSD", "Waymo"]:
        if term in TranslatorConfig.PROTECTED_TERMS:
            print(f"  - {term}")
    
    result = translator.translate(title=text)
    print(f"译文: {result.title}")
    print()


def example_5_error_handling():
    """示例5：错误处理和降级"""
    print("=" * 60)
    print("示例 5: 错误处理和降级")
    print("=" * 60)
    
    translator = create_translator()
    
    # 正常翻译
    result = translator.translate(
        title="Normal Title",
        summary="Normal summary text here."
    )
    print(f"正常翻译: {result.title}")
    
    # 降级策略演示
    # 当翻译失败时，fallback_to_original=True 会保留原文
    result = translator.translate(
        title="Important News",
        fallback_to_original=True  # 失败时返回原文
    )
    print(f"降级策略: 失败时保留原文 = {result.title}")
    print()


def example_6_integration_with_fetcher():
    """示例6：与 Fetcher 集成"""
    print("=" * 60)
    print("示例 6: 与 Fetcher 集成")
    print("=" * 60)
    
    # 模拟从 Fetcher 获取的文章数据
    fetched_articles = [
        {
            "source": "OpenAI Blog",
            "title": "GPT-4o System Card",
            "summary": "We are sharing details about the safety work for GPT-4o, including our preparedness framework evaluations and third-party assessments.",
            "url": "https://openai.com/index/gpt-4o-system-card/",
            "published": "2024-05-28"
        },
        {
            "source": "Tesla Blog", 
            "title": "Tesla FSD Beta Now Available to All Owners in North America",
            "summary": "Full Self-Driving Beta is now available to anyone in North America who has purchased the FSD package.",
            "url": "https://www.tesla.com/blog/fsd-beta-available",
            "published": "2024-03-15"
        }
    ]
    
    print("模拟从 Fetcher 获取的文章:")
    for article in fetched_articles:
        print(f"  - {article['source']}: {article['title']}")
    
    print("\n翻译后:")
    # 提取需要翻译的内容
    to_translate = [
        {"title": a["title"], "summary": a["summary"]}
        for a in fetched_articles
    ]
    
    results = translate_articles(to_translate)
    
    for article, result in zip(fetched_articles, results):
        print(f"  [{article['source']}]")
        print(f"    标题: {result.title}")
        print(f"    摘要: {result.summary}")
        print()


if __name__ == "__main__":
    print("Info-Getter 翻译模块使用示例\n")
    
    # 运行所有示例
    example_1_basic_usage()
    example_2_custom_config()
    example_3_batch_translation()
    example_4_protected_terms()
    example_5_error_handling()
    example_6_integration_with_fetcher()
    
    print("=" * 60)
    print("示例运行完成!")
    print("=" * 60)
