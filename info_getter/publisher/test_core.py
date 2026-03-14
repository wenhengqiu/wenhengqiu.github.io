"""
Publisher 模块测试
"""

import json
import os
import sys
import tempfile
import shutil
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from core import (
    Article, SimHash, QualityScorer, Publisher,
    publish_articles, publish_single_article
)


def test_simhash():
    """测试 SimHash 功能"""
    print("=" * 50)
    print("测试 SimHash")
    print("=" * 50)
    
    simhash = SimHash()
    
    # 测试文本
    text1 = "OpenAI 发布 GPT-5 新模型"
    text2 = "OpenAI 发布 GPT-5 新模型"  # 完全相同
    text3 = "Google 发布 Gemini 新版本"  # 不同
    
    hash1 = simhash.compute(text1)
    hash2 = simhash.compute(text2)
    hash3 = simhash.compute(text3)
    
    print(f"Text1: {text1}")
    print(f"Hash1: {hash1}")
    print(f"Text2: {text2}")
    print(f"Hash2: {hash2}")
    print(f"Text3: {text3}")
    print(f"Hash3: {hash3}")
    
    sim_12 = simhash.similarity(hash1, hash2)
    sim_13 = simhash.similarity(hash1, hash3)
    
    print(f"\n相似度 (text1, text2): {sim_12:.3f}")
    print(f"相似度 (text1, text3): {sim_13:.3f}")
    
    assert sim_12 == 1.0, "相同文本相似度应为 1.0"
    assert sim_13 < 0.9, "不同文本相似度应较低"
    
    print("✓ SimHash 测试通过")
    return True


def test_quality_scorer():
    """测试质量评分器"""
    print("\n" + "=" * 50)
    print("测试 QualityScorer")
    print("=" * 50)
    
    scorer = QualityScorer()
    
    # 高质量文章
    good_article = Article(
        id="test001",
        title="OpenAI 发布 GPT-5.4 系列：专业工作与智能体能力大幅提升",
        summary="OpenAI 推出 GPT-5.4 及 GPT-5.4 Pro 模型，面向 ChatGPT、API 及 Codex 平台同步上线，强化专业领域推理和智能体执行能力。",
        content="<p>OpenAI 今日正式推出 GPT-5.4 系列模型，这是 GPT-5 家族的重要升级。</p><p>核心升级：</p><ul><li>专业领域推理能力提升 40%</li><li>智能体执行能力增强</li></ul>",
        category="llm",
        publish_date="2026-03-13",
        display_date="3月13日",
        source="OpenAI",
        url="https://openai.com",
        tags=["OpenAI", "GPT-5.4", "Agent"]
    )
    
    # 低质量文章
    bad_article = Article(
        id="test002",
        title="短",
        summary="摘要",
        content="内容",
        category="",
        publish_date="",
        display_date="",
        source="",
        url="",
        tags=[]
    )
    
    good_score = scorer.score(good_article)
    bad_score = scorer.score(bad_article)
    
    print(f"高质量文章评分: {good_score}")
    print(f"低质量文章评分: {bad_score}")
    
    assert good_score >= 0.7, f"高质量文章应 >= 0.7, 实际 {good_score}"
    assert bad_score < 0.7, f"低质量文章应 < 0.7, 实际 {bad_score}"
    
    print("✓ QualityScorer 测试通过")
    return True


def test_publisher():
    """测试 Publisher 完整流程"""
    print("\n" + "=" * 50)
    print("测试 Publisher")
    print("=" * 50)
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    
    try:
        publisher = Publisher(
            data_dir=temp_dir,
            quality_threshold=0.7,
            similarity_threshold=0.85,
            auto_git=False
        )
        
        # 测试文章
        article1 = Article(
            id="2026-03-14-t001",
            title="测试文章 1：AI 技术突破",
            summary="这是一篇关于 AI 技术突破的测试文章，内容详实。",
            content="<p>详细内容...</p>" * 50,
            category="llm",
            publish_date="2026-03-14",
            display_date="3月14日",
            source="测试源",
            url="https://example.com/1",
            tags=["AI", "测试", "技术"]
        )
        
        # 重复文章（相似度高）
        article2 = Article(
            id="2026-03-14-t002",
            title="测试文章 1：AI 技术突破",  # 相同标题
            summary="这是一篇关于 AI 技术突破的测试文章，内容详实。",  # 相同摘要
            content="<p>不同内容...</p>",
            category="llm",
            publish_date="2026-03-14",
            display_date="3月14日",
            source="测试源",
            url="https://example.com/2",
            tags=["AI", "测试"]
        )
        
        # 低质量文章
        article3 = Article(
            id="2026-03-14-t003",
            title="短",
            summary="摘要",
            content="内容",
            category="llm",
            publish_date="2026-03-14",
            display_date="3月14日",
            source="",
            url="",
            tags=[]
        )
        
        # 发布第一篇文章
        existing = publisher.load_existing_articles()
        result1 = publisher.add_article(article1, existing)
        print(f"文章1发布结果: {result1}")
        assert result1['success'], "文章1应该发布成功"
        
        # 更新现有文章列表
        existing.append(article1)
        
        # 尝试发布重复文章
        result2 = publisher.add_article(article2, existing)
        print(f"文章2发布结果: {result2}")
        assert not result2['success'], "重复文章应该被拒绝"
        assert 'Duplicate' in result2['reason'], "拒绝原因应该是重复"
        
        # 尝试发布低质量文章
        result3 = publisher.add_article(article3, existing)
        print(f"文章3发布结果: {result3}")
        assert not result3['success'], "低质量文章应该被拒绝"
        assert 'Quality' in result3['reason'], "拒绝原因应该是质量低"
        
        # 验证文件是否创建
        target_file = Path(temp_dir) / "research" / "llm.json"
        assert target_file.exists(), f"文件应该存在: {target_file}"
        
        with open(target_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        assert len(saved_data) == 1, "应该只有一篇文章"
        assert saved_data[0]['id'] == "2026-03-14-t001", "ID 应该匹配"
        
        print("✓ Publisher 测试通过")
        return True
        
    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)


def test_publish_multiple():
    """测试批量发布"""
    print("\n" + "=" * 50)
    print("测试批量发布")
    print("=" * 50)
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        articles_data = [
            {
                "id": "2026-03-14-m001",
                "title": "高质量文章 1",
                "summary": "这是一篇高质量的文章摘要，内容详实丰富。",
                "content": "<p>详细内容...</p>" * 100,
                "category": "llm",
                "publishDate": "2026-03-14",
                "displayDate": "3月14日",
                "source": "测试源",
                "url": "https://example.com/m1",
                "tags": ["AI", "测试"]
            },
            {
                "id": "2026-03-14-m002",
                "title": "高质量文章 2",
                "summary": "另一篇高质量的文章摘要，内容同样详实。",
                "content": "<p>详细内容...</p>" * 100,
                "category": "robotics",
                "publishDate": "2026-03-14",
                "displayDate": "3月14日",
                "source": "测试源",
                "url": "https://example.com/m2",
                "tags": ["机器人", "测试"]
            },
            {
                "id": "2026-03-14-m003",
                "title": "低质量",
                "summary": "短",
                "content": "内容",
                "category": "llm",
                "publishDate": "2026-03-14",
                "displayDate": "3月14日",
                "source": "",
                "url": "",
                "tags": []
            }
        ]
        
        result = publish_articles(
            articles_data,
            data_dir=temp_dir,
            quality_threshold=0.7,
            auto_git=False
        )
        
        print(f"批量发布结果:")
        print(f"  总数: {result['total']}")
        print(f"  已发布: {result['published']}")
        print(f"  被拒绝: {result['rejected']}")
        print(f"  重复: {result['duplicates']}")
        print(f"  低质量: {result['low_quality']}")
        
        assert result['total'] == 3, "总数应为 3"
        assert result['published'] == 2, "应发布 2 篇"
        assert result['rejected'] == 1, "应拒绝 1 篇"
        assert result['low_quality'] == 1, "低质量应为 1"
        
        print("✓ 批量发布测试通过")
        return True
        
    finally:
        shutil.rmtree(temp_dir)


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("Info-Getter Publisher 模块测试")
    print("=" * 60)
    
    tests = [
        test_simhash,
        test_quality_scorer,
        test_publisher,
        test_publish_multiple
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            failed += 1
            print(f"✗ {test.__name__} 失败: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
