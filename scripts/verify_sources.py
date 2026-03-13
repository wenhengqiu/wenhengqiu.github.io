#!/usr/bin/env python3
"""
Info-Getter 信息源可用性验证工具
由于网络限制，提供模拟验证和配置检查
"""

import yaml
import json
from datetime import datetime

# 信息源清单
SOURCES = {
    "official_blogs": [
        {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml", "type": "rss", "status": "待验证"},
        {"name": "DeepMind Blog", "url": "https://deepmind.google/discover/blog/", "type": "rss", "status": "待验证"},
        {"name": "Anthropic", "url": "https://www.anthropic.com/news", "type": "rss", "status": "待验证"},
        {"name": "Tesla Blog", "url": "https://www.tesla.com/blog/rss.xml", "type": "rss", "status": "待验证"},
        {"name": "Waymo Blog", "url": "https://waymo.com/blog/rss/", "type": "rss", "status": "待验证"},
        {"name": "华为智能汽车", "url": "https://auto.huawei.com/news/rss", "type": "rss", "status": "待验证"},
        {"name": "小鹏汽车", "url": "https://www.xiaopeng.com/news/rss", "type": "rss", "status": "待验证"},
        {"name": "百度 Apollo", "url": "https://apollo.auto/news/rss", "type": "rss", "status": "待验证"},
        {"name": "Figure AI", "url": "https://www.figure.ai/news/rss", "type": "rss", "status": "待验证"},
        {"name": "宇树科技", "url": "https://www.unitree.com/news/rss", "type": "rss", "status": "待验证"},
        {"name": "智元机器人", "url": "https://www.zhiyuan-robot.com/news/rss", "type": "rss", "status": "待验证"},
        {"name": "卓驭科技", "url": "https://www.zhuoyutech.com/news/rss", "type": "rss", "status": "待验证"},
    ],
    "tech_media": [
        {"name": "机器之心", "url": "https://www.jiqizhixin.com/rss", "type": "rss", "status": "待验证"},
        {"name": "量子位", "url": "https://www.qbitai.com/rss", "type": "rss", "status": "待验证"},
        {"name": "品玩", "url": "https://www.pingwest.com/rss", "type": "rss", "status": "待验证"},
        {"name": "36氪", "url": "https://36kr.com/feed", "type": "rss", "status": "待验证"},
        {"name": "雷锋网", "url": "https://www.leiphone.com/rss", "type": "rss", "status": "待验证"},
        {"name": "极客公园", "url": "https://www.geekpark.net/rss", "type": "rss", "status": "待验证"},
        {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "type": "rss", "status": "待验证"},
        {"name": "The Verge AI", "url": "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml", "type": "rss", "status": "待验证"},
        {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/", "type": "rss", "status": "待验证"},
        {"name": "IEEE Spectrum", "url": "https://spectrum.ieee.org/rss/", "type": "rss", "status": "待验证"},
    ],
    "community": [
        {"name": "Hacker News", "url": "https://hacker-news.firebaseio.com/v0/", "type": "api", "status": "待验证"},
        {"name": "Reddit r/MachineLearning", "url": "https://www.reddit.com/r/MachineLearning/.rss", "type": "rss", "status": "待验证"},
        {"name": "Reddit r/SelfDrivingCars", "url": "https://www.reddit.com/r/SelfDrivingCars/.rss", "type": "rss", "status": "待验证"},
        {"name": "Lobsters AI", "url": "https://lobste.rs/t/ai.rss", "type": "rss", "status": "待验证"},
    ],
    "papers": [
        {"name": "arXiv cs.AI", "url": "http://arxiv.org/rss/cs.AI", "type": "rss", "status": "待验证"},
        {"name": "arXiv cs.CV", "url": "http://arxiv.org/rss/cs.CV", "type": "rss", "status": "待验证"},
        {"name": "arXiv cs.RO", "url": "http://arxiv.org/rss/cs.RO", "type": "rss", "status": "待验证"},
        {"name": "Papers With Code", "url": "https://paperswithcode.com/rss", "type": "rss", "status": "待验证"},
        {"name": "HuggingFace Blog", "url": "https://huggingface.co/blog/feed.xml", "type": "rss", "status": "待验证"},
    ]
}

def generate_config():
    """生成YAML配置文件"""
    config = {
        "version": "1.0",
        "updated_at": datetime.now().isoformat(),
        "sources": []
    }
    
    category_map = {
        "official_blogs": "general",
        "tech_media": "general", 
        "community": "general",
        "papers": "general"
    }
    
    priority_map = {
        "official_blogs": "p0",
        "tech_media": "p0",
        "community": "p1",
        "papers": "p1"
    }
    
    for category, sources in SOURCES.items():
        for source in sources:
            config["sources"].append({
                "id": source["name"].lower().replace(" ", "_").replace("/", "_"),
                "name": source["name"],
                "category": category_map.get(category, "general"),
                "type": source["type"],
                "language": "zh" if any(x in source["name"] for x in ["机器", "量子", "品玩", "氪", "雷锋", "极客", "华为", "小鹏", "百度", "宇树", "智元", "卓驭"]) else "en",
                "url": source["url"],
                "priority": priority_map.get(category, "p2"),
                "enabled": True,
                "status": "待验证",
                "fetch_interval": 3600,
                "timeout": 30,
                "retry_times": 3
            })
    
    return config

def main():
    print("=== Info-Getter 信息源清单 ===\n")
    
    total = 0
    for category, sources in SOURCES.items():
        print(f"【{category}】({len(sources)}个)")
        for s in sources:
            print(f"  - {s['name']}: {s['url']}")
        total += len(sources)
        print()
    
    print(f"总计: {total}个信息源\n")
    
    # 生成配置文件
    config = generate_config()
    with open('/tmp/sources.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, sort_keys=False)
    
    print("✅ 配置文件已生成: /tmp/sources.yaml")
    
    # 生成JSON版本
    with open('/tmp/sources.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print("✅ JSON配置已生成: /tmp/sources.json")

if __name__ == "__main__":
    main()
