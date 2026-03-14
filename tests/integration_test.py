#!/usr/bin/env python3
"""
Info-Getter 集成测试
测试各模块协同工作
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

async def test_fetcher():
    """测试采集模块"""
    print("🧪 测试采集模块...")
    
    try:
        from info_getter.fetcher.core import Fetcher, Source
        
        # 创建测试配置
        test_config = {
            'sources': [
                {
                    'id': 'test_source',
                    'name': 'Test Blog',
                    'url': 'https://example.com/rss',
                    'type': 'rss',
                    'category': 'test',
                    'priority': 'p0'
                }
            ],
            'fetch_settings': {
                'batch_size': 1,
                'timeout': 5
            }
        }
        
        fetcher = Fetcher(test_config)
        print("✅ Fetcher 初始化成功")
        
        # 测试 Source 模型
        source = Source(
            id='test',
            name='Test',
            url='https://test.com',
            type='rss',
            category='test',
            priority='p0'
        )
        print(f"✅ Source 模型: {source.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fetcher 测试失败: {e}")
        return False

async def test_translator():
    """测试翻译模块"""
    print("\n🧪 测试翻译模块...")
    
    try:
        from info_getter.translator.core import translate_article
        
        # 测试翻译
        result = translate_article(
            title="Test Article Title",
            summary="This is a test summary for translation."
        )
        
        print(f"✅ 翻译成功")
        print(f"   原文: Test Article Title")
        print(f"   译文: {result.title}")
        
        return True
        
    except Exception as e:
        print(f"❌ Translator 测试失败: {e}")
        return False

async def test_publisher():
    """测试发布模块"""
    print("\n🧪 测试发布模块...")
    
    try:
        from info_getter.publisher.core import Article, QualityScorer
        
        # 测试 Article 模型
        article = Article(
            id="test_001",
            title="测试文章",
            title_en="Test Article",
            summary="这是一个测试摘要",
            summary_en="This is a test summary",
            content="<p>测试内容</p>",
            url="https://example.com/test",
            source="Test Source",
            source_type="rss",
            published_at=datetime.now(),
            category="test",
            tags=["test"],
            companies=["TestCorp"],
            technologies=["TestTech"],
            language="zh"
        )
        
        print(f"✅ Article 模型: {article.title}")
        
        # 测试质量评分
        scorer = QualityScorer()
        score = scorer.score_article(article)
        print(f"✅ 质量评分: {score:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Publisher 测试失败: {e}")
        return False

async def test_scheduler():
    """测试调度模块"""
    print("\n🧪 测试调度模块...")
    
    try:
        from info_getter.scheduler import Scheduler
        
        scheduler = Scheduler(config_path="config/sources.yaml")
        print("✅ Scheduler 初始化成功")
        print(f"   信息源数量: {len(scheduler.config.get('sources', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Scheduler 测试失败: {e}")
        return False

async def main():
    """运行所有测试"""
    print("=" * 60)
    print("Info-Getter 集成测试")
    print("=" * 60)
    print()
    
    results = []
    
    # 测试各模块
    results.append(("Fetcher", await test_fetcher()))
    results.append(("Translator", await test_translator()))
    results.append(("Publisher", await test_publisher()))
    results.append(("Scheduler", await test_scheduler()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:15} {status}")
    
    print()
    print(f"总计: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
