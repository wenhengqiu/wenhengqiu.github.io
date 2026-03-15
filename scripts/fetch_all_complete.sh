#!/bin/bash
# Info-Getter 完整采集脚本
# 集成 RSS + Playwright + CDP浏览器爬虫

echo "🚀 Info-Getter 完整采集"
echo "========================"
echo ""

cd /Users/jarvis/.openclaw/workspace/dataloop-website

# 1. 检查Chrome是否运行
if ! curl -s http://localhost:9222/json/version > /dev/null; then
    echo "🌐 启动Chrome..."
    /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --headless=new &
    sleep 5
fi

# 2. RSS采集（现有守护进程）
echo "📡 RSS采集..."
echo "   守护进程自动运行中"

# 3. Playwright爬虫
echo ""
echo "🕷️ Playwright爬虫..."
/Library/Developer/CommandLineTools/usr/bin/python3 scripts/crawl_playwright.py

# 4. CDP浏览器爬虫
echo ""
echo "🌐 CDP浏览器爬虫..."
/Library/Developer/CommandLineTools/usr/bin/python3 /Users/jarvis/.openclaw/workspace/skills/cdp-web-crawler/crawl_zhuoyu.py

# 5. 统计结果
echo ""
echo "📊 采集统计"
echo "==========="

# 统计文章数
python3 << 'EOF'
import json
from pathlib import Path
from collections import defaultdict

total = 0
by_category = defaultdict(int)
by_source = defaultdict(int)

categories = ['llm', 'autonomous', 'robotics', 'zhuoyu', 'web_crawled', 'zhuoyu_cdp']

for cat in categories:
    file_path = Path(f'data/articles/research/{cat}.json')
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            total += len(data)
            by_category[cat] = len(data)
            
            for item in data:
                source = item.get('source', {})
                if isinstance(source, dict):
                    by_source[source.get('name', 'unknown')] += 1

print(f"总文章数: {total}")
print(f"\n按分类:")
for cat, count in sorted(by_category.items(), key=lambda x: -x[1]):
    print(f"  {cat}: {count}篇")

print(f"\nTop 10 来源:")
for source, count in sorted(by_source.items(), key=lambda x: -x[1])[:10]:
    print(f"  {source[:25]:25s}: {count}篇")
EOF

echo ""
echo "🎉 采集完成!"
