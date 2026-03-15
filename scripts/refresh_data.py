#!/usr/bin/env python3
"""
数据刷新脚本
重新分类所有文章并刷新数据
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime

# 导入分类器
import sys
sys.path.insert(0, '/Users/jarvis/.openclaw/workspace/dataloop-website')
from info_getter.classifier import ArticleClassifier

def load_all_articles():
    """加载所有文章"""
    data_dir = Path('/Users/jarvis/.openclaw/workspace/dataloop-website/data/articles/research')
    
    all_articles = []
    source_files = {}
    
    for json_file in data_dir.glob('*.json'):
        if json_file.name.endswith('.backup'):
            continue
        
        with open(json_file, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        item['_source_file'] = json_file.name
                    all_articles.extend(data)
                    source_files[json_file.name] = data
            except:
                pass
    
    return all_articles, source_files

def reclassify_articles(articles):
    """重新分类文章"""
    classifier = ArticleClassifier()
    
    print("=" * 70)
    print("🔄 重新分类文章")
    print("=" * 70)
    
    reclassified = {
        'llm': [],
        'autonomous': [],
        'robotics': [],
        'zhuoyu': []
    }
    
    for article in articles:
        title = article.get('title', '')
        summary = article.get('summary', '')
        
        category, confidence, details = classifier.classify(title, summary)
        
        # 更新文章分类
        article['category'] = category
        article['classification_confidence'] = confidence
        
        # 添加到对应分类
        if category in reclassified:
            reclassified[category].append(article)
        else:
            reclassified['llm'].append(article)  # 默认分类
    
    # 显示统计
    print("\n分类结果:")
    for cat, items in reclassified.items():
        cat_name = classifier.CATEGORY_KEYWORDS.get(cat, {}).get('name', cat)
        print(f"  {cat_name:12s} ({cat:12s}): {len(items):3d} 篇")
    
    return reclassified

def save_reclassified_articles(reclassified):
    """保存重新分类的文章"""
    data_dir = Path('/Users/jarvis/.openclaw/workspace/dataloop-website/data/articles/research')
    
    print("\n" + "=" * 70)
    print("💾 保存分类后的文章")
    print("=" * 70)
    
    for category, articles in reclassified.items():
        # 清理文章数据（移除内部字段）
        clean_articles = []
        for article in articles:
            clean_article = {k: v for k, v in article.items() 
                           if not k.startswith('_')}
            clean_articles.append(clean_article)
        
        # 按日期排序
        clean_articles.sort(key=lambda x: x.get('published_at', ''), reverse=True)
        
        # 保存
        output_file = data_dir / f"{category}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(clean_articles, f, ensure_ascii=False, indent=2)
        
        print(f"  {category:12s}: {len(clean_articles):3d} 篇 → {output_file}")
    
    # 清理其他文件
    for other_file in ['web_crawled.json', 'zhuoyu_cdp.json']:
        other_path = data_dir / other_file
        if other_path.exists():
            # 备份后清空
            backup_path = data_dir / f"{other_file}.merged"
            other_path.rename(backup_path)
            with open(other_path, 'w', encoding='utf-8') as f:
                json.dump([], f)
            print(f"  {other_file:12s}: 已合并并清空")

def git_commit():
    """Git提交"""
    print("\n" + "=" * 70)
    print("📤 Git提交")
    print("=" * 70)
    
    try:
        subprocess.run(['git', 'add', 'data/articles/research/'], 
                     check=True, cwd='/Users/jarvis/.openclaw/workspace/dataloop-website')
        subprocess.run(['git', 'commit', '-m', '[数据刷新] 重新分类所有文章'], 
                     check=True, cwd='/Users/jarvis/.openclaw/workspace/dataloop-website')
        subprocess.run(['git', 'push', 'user-pages', 'master'], 
                     check=True, cwd='/Users/jarvis/.openclaw/workspace/dataloop-website')
        print("✅ Git推送完成")
    except Exception as e:
        print(f"⚠️ Git操作失败: {e}")

def main():
    """主函数"""
    print("🚀 数据刷新脚本")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 加载所有文章
    all_articles, source_files = load_all_articles()
    print(f"\n📊 加载了 {len(all_articles)} 篇文章")
    
    # 2. 重新分类
    reclassified = reclassify_articles(all_articles)
    
    # 3. 保存
    save_reclassified_articles(reclassified)
    
    # 4. Git提交
    git_commit()
    
    print("\n" + "=" * 70)
    print("🎉 数据刷新完成!")
    print("=" * 70)

if __name__ == '__main__':
    main()
