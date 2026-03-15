#!/usr/bin/env python3
"""
Info-Getter 完整采集脚本
- 从所有信息源采集文章
- 时间范围：最近30天
- 完整的筛选和质量评分流程
- 保存到JSON文件（MongoDB未安装时）
"""

import asyncio
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from info_getter.fetcher.core import Fetcher
from info_getter.translator.core import Translator
from info_getter.publisher.core import Publisher, Article, QualityScorer

# 加载配置
import yaml

with open('config/sources.yaml', 'r') as f:
    config = yaml.safe_load(f)

async def fetch_all_sources():
    """从所有信息源采集文章"""
    print("🚀 开始完整采集流程...")
    print(f"📊 信息源数量: {len(config['sources'])}")
    print(f"⏰ 时间范围: 最近30天")
    print("=" * 70)
    
    # 1. 采集文章
    fetcher = Fetcher(config)
    raw_articles = await fetcher.fetch_all()
    print(f"\n📥 原始采集: {len(raw_articles)} 篇文章")
    
    # 2. 筛选30天内的文章
    cutoff_date = datetime.now() - timedelta(days=30)
    recent_articles = []
    for article in raw_articles:
        try:
            pub_date = article.published_at
            if pub_date and pub_date > cutoff_date:
                recent_articles.append(article)
        except:
            pass
    
    print(f"📅 30天内文章: {len(recent_articles)} 篇")
    
    # 3. 翻译和质量评分
    translator = Translator()
    scorer = QualityScorer()
    
    processed_articles = []
    
    for i, raw_article in enumerate(recent_articles, 1):
        print(f"\n📝 处理第 {i}/{len(recent_articles)} 篇文章...")
        
        # 显示文章基本信息
        print(f"   标题: {raw_article.title[:50]}...")
        print(f"   来源: {raw_article.source_name}")
        print(f"   日期: {raw_article.published_at}")
        
        # 翻译
        try:
            translation = translator.translate(
                title=raw_article.title,
                summary=raw_article.summary or '',
                fallback_to_original=True
            )
            print(f"   ✅ 翻译完成")
        except Exception as e:
            print(f"   ⚠️ 翻译失败: {e}")
            translation = None
        
        # 构建Article对象
        article = Article(
            id=raw_article.id,
            title=raw_article.title,
            title_zh=translation.title if translation and translation.success else raw_article.title,
            summary=raw_article.summary or '',
            summary_zh=translation.summary if translation and translation.success else (raw_article.summary or ''),
            content=raw_article.content or '',
            category=raw_article.category,
            publish_date=raw_article.published_at.isoformat() if raw_article.published_at else datetime.now().isoformat(),
            display_date=raw_article.published_at.strftime('%Y-%m-%d') if raw_article.published_at else datetime.now().strftime('%Y-%m-%d'),
            source={'name': raw_article.source_name, 'type': 'tech_media'},
            url=raw_article.url,
            tags=[],
            translated=translation.success if translation else False
        )
        
        # 质量评分
        quality_score = scorer.score(article)
        article.quality_score = quality_score
        
        print(f"   🔥 质量评分: {quality_score:.2f}")
        
        # 筛选：质量分 >= 0.6
        if quality_score >= 0.6:
            processed_articles.append(article)
            print(f"   ✅ 通过筛选，准备保存")
        else:
            print(f"   ❌ 质量分过低，丢弃")
    
    print(f"\n" + "=" * 70)
    print(f"📊 处理完成: {len(processed_articles)}/{len(recent_articles)} 篇文章通过筛选")
    
    # 4. 保存到JSON文件
    if processed_articles:
        publisher = Publisher('data/articles', auto_git=False)
        
        # 按分类保存
        by_category = {}
        for article in processed_articles:
            cat = article.category
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(article)
        
        for category, articles in by_category.items():
            file_path = Path(f'data/articles/research/{category}.json')
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 加载现有文章
            existing = []
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
            
            # 合并并去重
            all_articles = existing + [a.to_dict() for a in articles]
            seen_ids = set()
            unique_articles = []
            for a in all_articles:
                if a['id'] not in seen_ids:
                    seen_ids.add(a['id'])
                    unique_articles.append(a)
            
            # 保存
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(unique_articles, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 保存 {category}: {len(articles)} 篇新文章，总计 {len(unique_articles)} 篇")
        
        # Git提交
        print("\n📦 Git提交...")
        import subprocess
        subprocess.run(['git', 'add', 'data/articles/research/'], check=True)
        subprocess.run(['git', 'commit', '-m', f'[Info-Getter] 采集 {len(processed_articles)} 篇文章'], check=True)
        subprocess.run(['git', 'push', 'user-pages', 'master'], check=True)
        print("✅ Git推送完成")
    
    print("\n🎉 采集流程完成!")
    return processed_articles

if __name__ == '__main__':
    articles = asyncio.run(fetch_all_sources())
