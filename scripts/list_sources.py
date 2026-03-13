#!/usr/bin/env python3
"""
Info-Getter 信息源清单
"""

SOURCES = {
    "官方博客 (12个)": [
        ("OpenAI Blog", "https://openai.com/blog/rss.xml", "rss", "en"),
        ("DeepMind Blog", "https://deepmind.google/discover/blog/", "rss", "en"),
        ("Anthropic", "https://www.anthropic.com/news", "rss", "en"),
        ("Meta AI", "https://ai.meta.com/blog/rss/", "rss", "en"),
        ("Tesla Blog", "https://www.tesla.com/blog/rss.xml", "rss", "en"),
        ("Waymo Blog", "https://waymo.com/blog/rss/", "rss", "en"),
        ("华为智能汽车", "https://auto.huawei.com/news/rss", "rss", "zh"),
        ("小鹏汽车", "https://www.xiaopeng.com/news/rss", "rss", "zh"),
        ("百度 Apollo", "https://apollo.auto/news/rss", "rss", "zh"),
        ("Figure AI", "https://www.figure.ai/news/rss", "rss", "en"),
        ("宇树科技", "https://www.unitree.com/news/rss", "rss", "zh"),
        ("卓驭科技", "https://www.zhuoyutech.com/news/rss", "rss", "zh"),
    ],
    "科技媒体 (10个)": [
        ("机器之心", "https://www.jiqizhixin.com/rss", "rss", "zh"),
        ("量子位", "https://www.qbitai.com/rss", "rss", "zh"),
        ("品玩", "https://www.pingwest.com/rss", "rss", "zh"),
        ("36氪", "https://36kr.com/feed", "rss", "zh"),
        ("雷锋网", "https://www.leiphone.com/rss", "rss", "zh"),
        ("极客公园", "https://www.geekpark.net/rss", "rss", "zh"),
        ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/", "rss", "en"),
        ("The Verge AI", "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml", "rss", "en"),
        ("MIT Technology Review", "https://www.technologyreview.com/feed/", "rss", "en"),
        ("IEEE Spectrum", "https://spectrum.ieee.org/rss/", "rss", "en"),
    ],
    "社区论坛 (4个)": [
        ("Hacker News", "https://hacker-news.firebaseio.com/v0/", "api", "en"),
        ("Reddit r/MachineLearning", "https://www.reddit.com/r/MachineLearning/.rss", "rss", "en"),
        ("Reddit r/SelfDrivingCars", "https://www.reddit.com/r/SelfDrivingCars/.rss", "rss", "en"),
        ("Lobsters AI", "https://lobste.rs/t/ai.rss", "rss", "en"),
    ],
    "论文平台 (5个)": [
        ("arXiv cs.AI", "http://arxiv.org/rss/cs.AI", "rss", "en"),
        ("arXiv cs.CV", "http://arxiv.org/rss/cs.CV", "rss", "en"),
        ("arXiv cs.RO", "http://arxiv.org/rss/cs.RO", "rss", "en"),
        ("Papers With Code", "https://paperswithcode.com/rss", "rss", "en"),
        ("HuggingFace Blog", "https://huggingface.co/blog/feed.xml", "rss", "en"),
    ]
}

def main():
    print("=" * 60)
    print("Info-Getter 信息源清单")
    print("=" * 60)
    print()
    
    total = 0
    for category, sources in SOURCES.items():
        print(f"【{category}】")
        for name, url, type_, lang in sources:
            flag = "🇨🇳" if lang == "zh" else "🇺🇸"
            print(f"  {flag} {name}")
            print(f"     {url}")
        print()
        total += len(sources)
    
    print("=" * 60)
    print(f"总计: {total}个信息源")
    print("=" * 60)

if __name__ == "__main__":
    main()
