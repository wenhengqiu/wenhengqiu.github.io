#!/usr/bin/env python3
"""
AI Big News - 行业大佬版
一段式总结 + 趋势判断，为决策者定制
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass

sys.path.insert(0, '/Users/jarvis/.openclaw/workspace/dataloop-website')


@dataclass
class Article:
    id: str
    title: str
    title_zh: str
    summary: str
    source: Dict
    category: str
    quality_score: float
    published_at: str


class ExecutiveBriefGenerator:
    """高管简报生成器"""
    
    def __init__(self):
        self.data_dir = Path('/Users/jarvis/.openclaw/workspace/dataloop-website/data/articles/research')
    
    def collect_articles(self, days: int = 1) -> List[Article]:
        """采集最近文章"""
        articles = []
        cutoff = datetime.now() - timedelta(days=days)
        
        for category in ['llm', 'autonomous', 'robotics', 'zhuoyu']:
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
                            # 去重检查
                            title_key = item.get('title_zh', item.get('title', ''))[:40]
                            if not any(a.title_zh[:40] == title_key for a in articles):
                                articles.append(Article(
                                    id=item.get('id', ''),
                                    title=item.get('title', ''),
                                    title_zh=item.get('title_zh', item.get('title', '')),
                                    summary=item.get('summary_zh', item.get('summary', '')),
                                    source=item.get('source', {'name': '未知'}),
                                    category=item.get('category', 'llm'),
                                    quality_score=item.get('quality_score', 0.5),
                                    published_at=pub_date
                                ))
                    except:
                        pass
        
        # 按质量分排序
        articles.sort(key=lambda x: x.quality_score, reverse=True)
        return articles[:15]  # 只取TOP15
    
    def analyze_themes(self, articles: List[Article]) -> Dict:
        """分析主题和趋势"""
        # 关键词映射
        theme_keywords = {
            '大模型迭代': ['GPT', 'Claude', 'Gemini', '大模型', 'LLM', '多模态', '推理'],
            '端到端智驾': ['端到端', 'end-to-end', 'FSD', '城市NOA', '无图'],
            '具身智能落地': ['人形机器人', 'Figure', 'Optimus', '量产', '工厂'],
            '智驾平权': ['卓驭', '成行', '10万', '中算力', '下沉'],
            'AI应用爆发': ['Agent', '应用', '落地', '商业化', '营收']
        }
        
        themes = {k: [] for k in theme_keywords.keys()}
        
        for article in articles:
            text = f"{article.title_zh} {article.summary}".lower()
            for theme, keywords in theme_keywords.items():
                if any(kw.lower() in text for kw in keywords):
                    themes[theme].append(article)
        
        # 找出最热的3个主题
        hot_themes = sorted(themes.items(), key=lambda x: -len(x[1]))[:3]
        
        return {
            'hot_themes': hot_themes,
            'total_articles': len(articles),
            'company_mentions': self._extract_companies(articles)
        }
    
    def _extract_companies(self, articles: List[Article]) -> Dict[str, int]:
        """提取公司提及次数"""
        companies = [
            'OpenAI', 'Google', 'DeepMind', 'Anthropic', 'Meta', 'Microsoft',
            'Tesla', 'Waymo', '百度', '小鹏', '华为', '蔚来', '理想',
            'Figure AI', '宇树', '智元', '波士顿动力',
            '卓驭', '大疆', 'Mobileye'
        ]
        
        mentions = {}
        for article in articles:
            text = f"{article.title_zh} {article.summary}"
            for company in companies:
                if company in text:
                    mentions[company] = mentions.get(company, 0) + 1
        
        return dict(sorted(mentions.items(), key=lambda x: -x[1])[:5])
    
    def generate_brief(self, articles: List[Article], analysis: Dict) -> str:
        """生成高管简报"""
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%m月%d日')
        
        # 构建主题段落
        theme_paragraphs = []
        for theme_name, theme_articles in analysis['hot_themes']:
            if theme_articles:
                titles = [a.title_zh[:30] + '...' for a in theme_articles[:2]]
                theme_paragraphs.append(f"{theme_name}（{len(theme_articles)}篇）：{'；'.join(titles)}")
        
        # 核心公司
        companies = list(analysis['company_mentions'].keys())[:3]
        company_str = '、'.join(companies) if companies else '头部企业'
        
        # 生成趋势判断
        trend_judgment = self._generate_trend_judgment(analysis)
        
        brief = f"""# 🌅 AI Big News · 高管简报

**{yesterday} | 精选{analysis['total_articles']}篇高质量资讯**

---

## 📋 核心动态

昨日AI行业呈现**{len(theme_paragraphs)}大主线**密集发酵态势。{'；'.join(theme_paragraphs)}。{company_str}等头部玩家加速布局，技术迭代与商业化落地进入共振期。

## 🔮 趋势判断

{trend_judgment}

## 📌 重点关注

"""
        
        # 添加TOP5文章
        for i, article in enumerate(articles[:5], 1):
            source = article.source.get('name', '未知') if isinstance(article.source, dict) else '未知'
            brief += f"{i}. **{article.title_zh}**（{source}）\n"
        
        brief += f"""
---
*Info-Getter 智能生成 · 为决策者节省时间*
"""
        
        return brief
    
    def _generate_trend_judgment(self, analysis: Dict) -> str:
        """生成趋势判断"""
        hot_themes = analysis['hot_themes']
        
        if not hot_themes or not hot_themes[0][1]:
            return "市场处于蓄力期，建议关注头部企业技术发布动态。"
        
        # 根据最热主题生成判断
        top_theme = hot_themes[0][0]
        
        judgments = {
            '大模型迭代': '基础模型能力竞争进入白热化，推理效率与多模态融合成为新战场，应用层创业窗口正在收窄。',
            '端到端智驾': '自动驾驶技术路线收敛至端到端，数据闭环能力成为核心竞争力，2024-2025将是城市NOA规模化关键期。',
            '具身智能落地': '人形机器人从实验室走向工厂，成本下降与场景验证并行，制造业自动化升级迎来拐点。',
            '智驾平权': '高阶智驾下探至10-20万车型，供应链成本压力倒逼算法优化，中算力方案迎来爆发窗口。',
            'AI应用爆发': '大模型应用从概念验证进入商业化阶段，Agent形态产品开始产生实际营收，B端落地速度快于C端。'
        }
        
        return judgments.get(top_theme, f"{top_theme}成为昨日焦点，技术演进与产业落地同步加速，建议密切关注头部玩家动向。")
    
    def run(self) -> str:
        """运行生成"""
        print("=" * 70)
        print("🌅 AI Big News · 高管简报")
        print("=" * 70)
        
        # 采集文章
        articles = self.collect_articles()
        print(f"\n📊 采集到 {len(articles)} 篇高质量文章")
        
        if not articles:
            return "暂无新资讯"
        
        # 分析主题
        analysis = self.analyze_themes(articles)
        print(f"🔥 识别 {len(analysis['hot_themes'])} 个热点主题")
        
        # 生成简报
        brief = self.generate_brief(articles, analysis)
        
        # 保存
        self._save(brief)
        
        # 显示
        print("\n" + "=" * 70)
        print(brief)
        print("=" * 70)
        
        return brief
    
    def _save(self, brief: str):
        """保存简报"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 保存到daily目录
        daily_dir = Path('/Users/jarvis/.openclaw/workspace/dataloop-website/data/articles/daily')
        daily_dir.mkdir(parents=True, exist_ok=True)
        
        # 高管版
        brief_file = daily_dir / f"{today}_executive.md"
        with open(brief_file, 'w', encoding='utf-8') as f:
            f.write(brief)
        
        print(f"\n💾 已保存: {brief_file}")


def main():
    generator = ExecutiveBriefGenerator()
    brief = generator.run()
    print("\n✅ 高管简报生成完成!")


if __name__ == '__main__':
    main()
