#!/usr/bin/env python3
"""
测试Web爬虫 - 禁用SSL验证
"""

import urllib.request
import ssl
import re

# 禁用SSL验证
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://deepmind.google/discover/blog/'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

try:
    with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
        html = response.read().decode('utf-8', errors='ignore')
        print(f'✅ 成功获取: {len(html)} 字符')
        
        # 简单解析标题
        titles = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]{20,100})</a>', html, re.IGNORECASE)
        print(f'📄 找到 {len(titles)} 个链接')
        
        for href, title in titles[:5]:
            print(f'  - {title.strip()[:60]}...')
            print(f'    {href[:60]}')
            
except Exception as e:
    print(f'❌ 失败: {e}')
