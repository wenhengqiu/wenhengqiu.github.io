#!/usr/bin/env python3
"""
清理脚本：删除关键字段为空的文章
"""

import json
from pathlib import Path

def clean_empty_articles():
    """清理关键字段为空的文章"""
    data_dir = Path('/Users/jarvis/.openclaw/workspace/dataloop-website/data/articles/research')
    
    categories = ['llm', 'autonomous', 'robotics', 'zhuoyu']
    total_removed = 0
    
    for cat in categories:
        file_path = data_dir / f"{cat}.json"
        if not file_path.exists():
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        original_count = len(data)
        
        # 过滤掉关键字段为空的文章
        filtered = []
        for article in data:
            # 检查关键字段
            has_id = article.get('id') and str(article.get('id')).strip() != ''
            has_title = article.get('title') and str(article.get('title')).strip() != ''
            has_url = article.get('url') and str(article.get('url')).strip() != ''
            has_category = article.get('category') and str(article.get('category')).strip() != ''
            has_summary = article.get('summary') and str(article.get('summary')).strip() != '' and str(article.get('summary')).strip() != 'nan'
            
            if has_id and has_title and has_url and has_category and has_summary:
                filtered.append(article)
            else:
                missing = []
                if not has_id: missing.append('id')
                if not has_title: missing.append('title')
                if not has_url: missing.append('url')
                if not has_category: missing.append('category')
                if not has_summary: missing.append('summary')
                print(f"  删除: {article.get('title', 'N/A')[:40]}... (缺少: {', '.join(missing)})")
                total_removed += 1
        
        removed = original_count - len(filtered)
        
        if removed > 0:
            # 保存过滤后的数据
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(filtered, f, ensure_ascii=False, indent=2)
            
            print(f"{cat}: 删除 {removed} 篇，剩余 {len(filtered)} 篇")
        else:
            print(f"{cat}: 无需清理，共 {original_count} 篇")
    
    print(f"\n总计删除: {total_removed} 篇文章")
    
    # Git提交
    import subprocess
    try:
        subprocess.run(['git', 'add', 'data/articles/research/'], 
                     check=True, cwd='/Users/jarvis/.openclaw/workspace/dataloop-website')
        subprocess.run(['git', 'commit', '-m', f'清理空URL文章: 删除{total_removed}篇'], 
                     check=True, cwd='/Users/jarvis/.openclaw/workspace/dataloop-website')
        subprocess.run(['git', 'push', 'user-pages', 'master'], 
                     check=True, cwd='/Users/jarvis/.openclaw/workspace/dataloop-website')
        print("✅ Git推送完成")
    except Exception as e:
        print(f"⚠️ Git操作失败: {e}")

if __name__ == '__main__':
    clean_empty_articles()
