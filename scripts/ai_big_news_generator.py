#!/usr/bin/env python3
"""
AI Big News 独立生成器
分别总结人工智能、自动驾驶、具身智能的关键信息
不依赖Info-Getter，直接读取文章数据
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter

class AIBigNewsGenerator:
    """AI Big News 生成器"""
    
    def __init__(self):
        self.data_dir = Path('/Users/jarvis/.openclaw/workspace/dataloop-website/data/articles/research')
        self.output_dir = Path('/Users/jarvis/.openclaw/workspace/dataloop-website/data/articles/daily')
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def load_articles(self, days=1):
        """加载最近几天的文章"""
        cutoff = datetime.now() - timedelta(days=days)
        articles = []
        
        for category in ['llm', 'autonomous', 'robotics']:
            file_path = self.data_dir / f"{category}.json"
            if not file_path.exists():
                continue
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for item in data:
                pub_date = item.get('published_at', '')
                if pub_date:
                    try:
                        article_date = datetime.fromisoformat(pub_date.replace('Z', '+00:00').replace('+00:00', ''))
                        if article_date >= cutoff:
                            item['category'] = category
                            articles.append(item)
                    except:
                        pass
        
        return articles
    
    def analyze_by_category(self, articles):
        """按分类分析文章"""
        result = {
            'llm': [],
            'autonomous': [],
            'robotics': []
        }
        
        for article in articles:
            cat = article.get('category', 'llm')
            if cat in result:
                result[cat].append(article)
        
        return result
    
    def extract_keywords(self, articles, top_n=5):
        """提取关键词"""
        all_text = ' '.join([a.get('title', '') + ' ' + a.get('summary', '') for a in articles])
        
        # 预定义关键词
        keywords_map = {
            'llm': ['GPT', '大模型', 'OpenAI', 'Claude', 'Gemini', 'LLM', 'AI', '智能', '模型', '算法'],
            'autonomous': ['自动驾驶', 'FSD', 'NOA', '智驾', '激光雷达', '纯视觉', '端到端', '特斯拉', '小鹏', '蔚来'],
            'robotics': ['人形机器人', '具身智能', 'Figure', 'Optimus', '宇树', '智元', '机器人', '灵巧手', '运动控制']
        }
        
        found_keywords = []
        for word_list in keywords_map.values():
            for word in word_list:
                if word in all_text:
                    found_keywords.append(word)
        
        # 统计频率
        counter = Counter(found_keywords)
        return counter.most_common(top_n)
    
    def generate_summary(self, articles_by_cat):
        """生成各领域总结"""
        summaries = {}
        
        for cat, articles in articles_by_cat.items():
            if not articles:
                summaries[cat] = "今日暂无重要动态"
                continue
            
            # 取前3篇高分文章
            top_articles = sorted(articles, key=lambda x: x.get('quality_score', 0), reverse=True)[:3]
            
            # 生成总结
            titles = [a.get('title', '')[:30] for a in top_articles]
            summaries[cat] = '；'.join(titles) + '...'
        
        return summaries
    
    def generate_big_news(self):
        """生成AI Big News"""
        print("=" * 70)
        print("🌅 生成 AI Big News")
        print("=" * 70)
        
        # 加载文章
        articles = self.load_articles(days=1)
        print(f"\n📊 加载到 {len(articles)} 篇文章")
        
        # 按分类分析
        by_category = self.analyze_by_category(articles)
        print(f"  人工智能: {len(by_category['llm'])} 篇")
        print(f"  自动驾驶: {len(by_category['autonomous'])} 篇")
        print(f"  具身智能: {len(by_category['robotics'])} 篇")
        
        # 生成各领域总结
        summaries = self.generate_summary(by_category)
        
        # 提取热点关键词
        hot_keywords = self.extract_keywords(articles)
        
        # 生成报告
        today = datetime.now().strftime('%Y年%m月%d日')
        report = f"""# 🌅 AI Big News · {today}

## 📊 昨日概览
━━━━━━━━━━━━━━━━
| 领域 | 文章数 | 关键动态 |
|------|--------|----------|
| 🤖 人工智能 | {len(by_category['llm'])} | {summaries['llm']} |
| 🚗 自动驾驶 | {len(by_category['autonomous'])} | {summaries['autonomous']} |
| 🤖 具身智能 | {len(by_category['robotics'])} | {summaries['robotics']} |

## 🔥 热点关键词
{chr(10).join([f"{i+1}. **{kw}** - 出现{count}次" for i, (kw, count) in enumerate(hot_keywords)])}

## 📰 各领域 TOP3

### 🤖 人工智能
{self._format_top3(by_category['llm'])}

### 🚗 自动驾驶
{self._format_top3(by_category['autonomous'])}

### 🤖 具身智能
{self._format_top3(by_category['robotics'])}

---
🤖 由 AI Big News Generator 自动生成
📅 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
        
        # 保存报告
        today_str = datetime.now().strftime('%Y-%m-%d')
        output_file = self.output_dir / f"{today_str}_big_news.md"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n💾 已保存: {output_file}")
        print("\n" + "=" * 70)
        print(report[:500] + "...")
        print("=" * 70)
        
        return report
    
    def _format_top3(self, articles):
        """格式化TOP3文章"""
        if not articles:
            return "暂无文章"
        
        top3 = sorted(articles, key=lambda x: x.get('quality_score', 0), reverse=True)[:3]
        
        lines = []
        for i, article in enumerate(top3, 1):
            title = article.get('title', '无标题')[:50]
            source = article.get('source', '未知')
            if isinstance(source, dict):
                source = source.get('name', '未知')
            lines.append(f"{i}. **{title}** - *{source}*")
        
        return '\n'.join(lines)


def main():
    """主函数"""
    generator = AIBigNewsGenerator()
    generator.generate_big_news()
    print("\n✅ AI Big News 生成完成!")


if __name__ == '__main__':
    main()
