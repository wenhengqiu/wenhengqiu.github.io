#!/usr/bin/env python3
"""
刷新现有文章数据，转换为PRD v6.1格式
"""

import json
import os
from pathlib import Path

def migrate_article(article):
    """将旧格式文章转换为PRD v6.1格式"""
    # 处理 source 字段
    source = article.get('source', '')
    if isinstance(source, str):
        source = {'name': source, 'type': 'tech_media'}
    
    # 获取标题和摘要
    title = article.get('title', '')
    summary = article.get('summary', '')
    
    # 如果标题以"[译]"开头，说明已有中文翻译
    if title.startswith('[译] '):
        title_zh = title[4:]  # 去掉"[译] "前缀
        title = title  # 保留原标题
    else:
        title_zh = title  # 如果没有标记，使用原标题作为中文标题
    
    # 如果摘要以"[译文摘要]"开头
    if summary.startswith('[译文摘要] '):
        summary_zh = summary[7:]  # 去掉"[译文摘要] "前缀
    else:
        summary_zh = summary
    
    # 构建PRD v6.1格式
    new_article = {
        'id': article.get('id', ''),
        'title': title,
        'title_zh': title_zh,
        'summary': summary,
        'summary_zh': summary_zh,
        'url': article.get('url', ''),
        'source': source,
        'category': article.get('category', 'llm'),
        'quality_score': round(article.get('quality_score', 0.0), 2),
        'published_at': article.get('published_at', ''),
        'translated': title.startswith('[译]') or summary.startswith('[译文摘要]'),
        'tags': article.get('tags', [])
    }
    
    return new_article

def migrate_file(file_path):
    """迁移单个JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            new_data = [migrate_article(article) for article in data]
        else:
            new_data = migrate_article(data)
        
        # 备份原文件
        backup_path = str(file_path) + '.backup'
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 写入新格式
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已迁移: {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ 失败: {file_path} - {e}")
        return False

def main():
    """主函数"""
    data_dir = Path('data/articles/research')
    
    if not data_dir.exists():
        print(f"目录不存在: {data_dir}")
        return
    
    success_count = 0
    fail_count = 0
    
    for json_file in data_dir.glob('*.json'):
        if migrate_file(json_file):
            success_count += 1
        else:
            fail_count += 1
    
    print(f"\n完成: {success_count} 成功, {fail_count} 失败")

if __name__ == '__main__':
    main()
