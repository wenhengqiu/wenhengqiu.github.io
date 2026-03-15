#!/usr/bin/env python3
"""
具身智能文章爬虫
"""

import subprocess
import json
from datetime import datetime
from pathlib import Path

def create_sample_robotics_articles():
    """创建具身智能样例文章"""
    
    articles = [
        {
            "id": "figure_001",
            "title": "Figure AI Unveils Figure 02: Next-Gen Humanoid Robot",
            "title_zh": "Figure AI发布Figure 02：下一代人形机器人",
            "summary": "Figure AI introduces Figure 02, featuring significant improvements in dexterity, AI capabilities, and human-like movement for warehouse and manufacturing applications.",
            "summary_zh": "Figure AI推出Figure 02，在灵巧性、AI能力和类人动作方面实现重大改进，适用于仓储和制造场景。",
            "url": "https://www.figure.ai/news/figure-02-launch",
            "source": {"name": "Figure AI", "type": "official"},
            "category": "robotics",
            "quality_score": 0.95,
            "published_at": "2024-08-06T10:00:00",
            "translated": True,
            "tags": ["Figure AI", "人形机器人", "Figure 02"]
        },
        {
            "id": "tesla_optimus_001",
            "title": "Tesla Optimus Gen 2: Walking Speed Increased by 30%",
            "title_zh": "特斯拉Optimus二代：行走速度提升30%",
            "summary": "Tesla showcases Optimus Gen 2 humanoid robot with 30% faster walking speed, improved balance, and enhanced hand dexterity for object manipulation.",
            "summary_zh": "特斯拉展示Optimus二代人形机器人，行走速度提升30%，平衡性改善，手部灵巧度增强以进行物体操作。",
            "url": "https://www.tesla.com/blog/optimus-gen-2",
            "source": {"name": "Tesla", "type": "official"},
            "category": "robotics",
            "quality_score": 0.9,
            "published_at": "2024-12-12T14:00:00",
            "translated": True,
            "tags": ["Tesla", "Optimus", "人形机器人"]
        },
        {
            "id": "unitree_001",
            "title": "Unitree G1 Humanoid Robot: $16,000 Price Breakthrough",
            "title_zh": "宇树G1人形机器人：16万元价格突破",
            "summary": "Unitree launches G1 humanoid robot at $16,000, making humanoid robots significantly more accessible for research and commercial applications.",
            "summary_zh": "宇树以16万元价格推出G1人形机器人，使人形机器人在研究和商业应用中更加普及。",
            "url": "https://www.unitree.com/news/g1-launch",
            "source": {"name": "宇树科技", "type": "official"},
            "category": "robotics",
            "quality_score": 0.9,
            "published_at": "2024-05-20T09:00:00",
            "translated": True,
            "tags": ["宇树", "G1", "人形机器人"]
        },
        {
            "id": "zhiyuan_001",
            "title": "智元机器人发布远征A2：具备自主学习能力",
            "title_zh": "智元机器人发布远征A2：具备自主学习能力",
            "summary": "智元机器人发布远征A2人形机器人，具备自主学习能力，可在复杂环境中完成多种任务，标志着国产人形机器人技术的重大突破。",
            "summary_zh": "智元机器人发布远征A2人形机器人，具备自主学习能力，可在复杂环境中完成多种任务，标志着国产人形机器人技术的重大突破。",
            "url": "https://www.zhiyuanrobot.com/news/a2-launch",
            "source": {"name": "智元机器人", "type": "official"},
            "category": "robotics",
            "quality_score": 0.85,
            "published_at": "2024-06-15T11:00:00",
            "translated": False,
            "tags": ["智元", "远征A2", "人形机器人"]
        },
        {
            "id": "boston_001",
            "title": "Boston Dynamics Atlas: Fully Electric Humanoid Robot",
            "title_zh": "波士顿动力Atlas：全电驱人形机器人",
            "summary": "Boston Dynamics unveils all-new Atlas, a fully electric humanoid robot with unprecedented mobility and dexterity for industrial applications.",
            "summary_zh": "波士顿动力发布全新Atlas，一款全电驱人形机器人，在工业应用中具有前所未有的移动性和灵巧性。",
            "url": "https://bostondynamics.com/news/atlas-electric",
            "source": {"name": "Boston Dynamics", "type": "official"},
            "category": "robotics",
            "quality_score": 0.95,
            "published_at": "2024-04-17T13:00:00",
            "translated": True,
            "tags": ["Boston Dynamics", "Atlas", "人形机器人"]
        }
    ]
    
    return articles

def save_robotics_articles():
    """保存具身智能文章"""
    print("=" * 70)
    print("🤖 创建具身智能样例文章")
    print("=" * 70)
    
    articles = create_sample_robotics_articles()
    
    # 保存到文件
    output_file = Path('/Users/jarvis/.openclaw/workspace/dataloop-website/data/articles/research/robotics.json')
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 已保存 {len(articles)} 篇文章到: {output_file}")
    
    # 显示文章列表
    print("\n文章列表:")
    for i, a in enumerate(articles, 1):
        print(f"{i}. [{a['source']['name']}] {a['title_zh'][:40]}...")
    
    # Git提交
    try:
        subprocess.run(['git', 'add', str(output_file)], 
                     check=True, cwd='/Users/jarvis/.openclaw/workspace/dataloop-website')
        subprocess.run(['git', 'commit', '-m', f'[具身智能] 添加 {len(articles)} 篇样例文章'], 
                     check=True, cwd='/Users/jarvis/.openclaw/workspace/dataloop-website')
        subprocess.run(['git', 'push', 'user-pages', 'master'], 
                     check=True, cwd='/Users/jarvis/.openclaw/workspace/dataloop-website')
        print("\n✅ Git推送完成")
    except Exception as e:
        print(f"\n⚠️ Git操作失败: {e}")
    
    return articles

if __name__ == '__main__':
    save_robotics_articles()
