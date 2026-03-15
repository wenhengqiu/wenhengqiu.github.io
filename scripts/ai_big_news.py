#!/usr/bin/env python3
"""
AI Big News - 每日AI圈大事总结
每天早上9点自动推送前一天AI行业重要资讯
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, field

# 添加项目路径
sys.path.insert(0, '/Users/jarvis/.openclaw/workspace/dataloop-website')


@dataclass
class Article:
    """文章数据类"""
    id: str
    title: str
    title_zh: str
    summary: str
    summary_zh: str
    url: str
    source: Dict[str, str]
    category: str
    quality_score: float
    published_at: str
    

@dataclass
class DailyReport:
    """每日报告"""
    date: str
    stats: Dict[str, int] = field(default_factory=dict)
    hot_topics: List[Dict] = field(default_factory=list)
    top_articles: Dict[str, List[Article]] = field(default_factory=dict)
    trends: str = ""


class DataCollector:
    """数据采集器"""
    
    def __init__(self, data_dir: str = "data/articles/research"):
        self.data_dir = Path(data_dir)
    
    def collect_articles(self, date_offset: int = 0) -> List[Article]:
        """采集指定日期的文章 (0=今天, 1=昨天)"""
        target_date = datetime.now() - timedelta(days=date_offset)
        target_str = target_date.strftime('%Y-%m-%d')
        
        print(f"📊 采集 {target_str} 的文章...")
        
        articles = []
        categories = ['llm', 'autonomous', 'robotics', 'zhuoyu']
        
        for category in categories:
            file_path = self.data_dir / f"{category}.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for item in data:
                    # 检查是否是目标日期的文章
                    pub_date = item.get('published_at', '')[:10]
                    if pub_date == target_str:
                        articles.append(Article(
                            id=item.get('id', ''),
                            title=item.get('title', ''),
                            title_zh=item.get('title_zh', item.get('title', '')),
                            summary=item.get('summary', ''),
                            summary_zh=item.get('summary_zh', item.get('summary', '')),
                            url=item.get('url', ''),
                            source=item.get('source', {'name': '未知', 'type': 'unknown'}),
                            category=item.get('category', 'llm'),
                            quality_score=item.get('quality_score', 0.5),
                            published_at=item.get('published_at', '')
                        ))
        
        print(f"  ✅ 找到 {len(articles)} 篇昨日文章")
        return articles


class ArticleFilter:
    """文章过滤器"""
    
    def filter(self, articles: List[Article], min_quality: float = 0.7) -> List[Article]:
        """筛选高质量文章"""
        print(f"\n🔍 筛选质量分≥{min_quality}的文章...")
        
        # 质量分过滤
        filtered = [a for a in articles if a.quality_score >= min_quality]
        print(f"  ✅ 筛选后: {len(filtered)} 篇")
        
        # 去重（基于标题相似度）
        filtered = self._deduplicate(filtered)
        print(f"  ✅ 去重后: {len(filtered)} 篇")
        
        # 排序（按质量分降序）
        filtered.sort(key=lambda x: x.quality_score, reverse=True)
        
        return filtered
    
    def _deduplicate(self, articles: List[Article]) -> List[Article]:
        """简单去重（基于标题前30字符）"""
        seen = set()
        unique = []
        for a in articles:
            key = a.title[:30]
            if key not in seen:
                seen.add(key)
                unique.append(a)
        return unique


class ReportGenerator:
    """报告生成器"""
    
    def generate(self, articles: List[Article], target_date: datetime = None) -> str:
        """生成Markdown报告"""
        if target_date is None:
            target_date = datetime.now() - timedelta(days=1)
        date_str = target_date.strftime('%Y年%m月%d日')
        
        # 统计
        stats = self._calculate_stats(articles)
        
        # TOP5文章
        top_articles = self._select_top5(articles)
        
        # 生成报告
        report = f"""# 🌅 AI Big News - {date_str}

## 📊 昨日概览
━━━━━━━━━━━━━━━━
| 领域 | 文章数 | 占比 |
|------|--------|------|
| 🤖 人工智能 | {stats.get('llm', 0)} | {stats.get('llm', 0)/max(stats['total'], 1)*100:.0f}% |
| 🚗 自动驾驶 | {stats.get('autonomous', 0)} | {stats.get('autonomous', 0)/max(stats['total'], 1)*100:.0f}% |
| 🤖 具身智能 | {stats.get('robotics', 0)} | {stats.get('robotics', 0)/max(stats['total'], 1)*100:.0f}% |
| 🚙 卓驭科技 | {stats.get('zhuoyu', 0)} | {stats.get('zhuoyu', 0)/max(stats['total'], 1)*100:.0f}% |
| **总计** | **{stats['total']}** | 100% |

## 🔥 今日热点
{self._generate_hot_topics(articles)}

## 🤖 人工智能 TOP5
{self._generate_top5_section(top_articles.get('llm', []))}

## 🚗 自动驾驶 TOP5
{self._generate_top5_section(top_articles.get('autonomous', []))}

## 🤖 具身智能 TOP5
{self._generate_top5_section(top_articles.get('robotics', []))}

## 📈 趋势洞察
{self._generate_trends(articles)}

---
🤖 由 **Info-Getter + AI Big News** 自动生成  
📅 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}  
🔗 [查看完整数据](https://wenhengqiu.github.io/research.html)
"""
        
        return report
    
    def _calculate_stats(self, articles: List[Article]) -> Dict[str, int]:
        """计算统计信息"""
        stats = {'total': len(articles), 'llm': 0, 'autonomous': 0, 'robotics': 0, 'zhuoyu': 0}
        for a in articles:
            if a.category in stats:
                stats[a.category] += 1
        return stats
    
    def _select_top5(self, articles: List[Article]) -> Dict[str, List[Article]]:
        """选择各领域TOP5"""
        top = {'llm': [], 'autonomous': [], 'robotics': [], 'zhuoyu': []}
        
        for category in top.keys():
            category_articles = [a for a in articles if a.category == category]
            top[category] = category_articles[:5]
        
        return top
    
    def _generate_hot_topics(self, articles: List[Article]) -> str:
        """生成热点话题"""
        # 简单实现：统计关键词出现频率
        keywords = {}
        for a in articles:
            text = f"{a.title} {a.summary}".lower()
            for kw in ['gpt', 'fsd', 'robot', '端到端', '大模型', '人形']:
                if kw in text:
                    keywords[kw] = keywords.get(kw, 0) + 1
        
        # 排序取前3
        hot = sorted(keywords.items(), key=lambda x: -x[1])[:3]
        
        if not hot:
            return "暂无热点数据"
        
        result = []
        for i, (kw, count) in enumerate(hot, 1):
            result.append(f"{i}. **{kw.upper()}** - 相关文章{count}篇")
        
        return '\n'.join(result)
    
    def _generate_top5_section(self, articles: List[Article]) -> str:
        """生成TOP5章节"""
        if not articles:
            return "暂无数据"
        
        lines = []
        for i, a in enumerate(articles, 1):
            source_name = a.source.get('name', '未知') if isinstance(a.source, dict) else '未知'
            title = a.title_zh if a.title_zh else a.title
            summary = a.summary_zh[:80] + '...' if a.summary_zh and len(a.summary_zh) > 80 else (a.summary_zh or '')
            
            lines.append(f"{i}. **{title}** - *{source_name}* (质量:{a.quality_score:.1f})")
            if summary:
                lines.append(f"   > {summary}")
            if a.url:
                lines.append(f"   → [阅读原文]({a.url})")
            lines.append("")
        
        return '\n'.join(lines)
    
    def _generate_trends(self, articles: List[Article]) -> str:
        """生成趋势洞察"""
        categories = {}
        for a in articles:
            cat = a.category
            categories[cat] = categories.get(cat, 0) + 1
        
        if not categories:
            return "暂无趋势数据"
        
        # 找出最活跃的领域
        top_cat = max(categories, key=categories.get)
        cat_names = {'llm': '人工智能', 'autonomous': '自动驾驶', 'robotics': '具身智能', 'zhuoyu': '卓驭科技'}
        
        return f"昨日**{cat_names.get(top_cat, top_cat)}**领域最为活跃，共有{categories[top_cat]}篇高质量文章。建议重点关注该领域的技术进展和产品动态。"


class AIBigNews:
    """AI Big News 主程序"""
    
    def __init__(self):
        self.collector = DataCollector()
        self.filter = ArticleFilter()
        self.generator = ReportGenerator()
    
    def run(self) -> str:
        """运行每日总结"""
        print("=" * 70)
        print("🌅 AI Big News - 每日AI圈大事总结")
        print("=" * 70)
        
        # 1. 采集文章 (0=今天, 1=昨天)
        articles = self.collector.collect_articles(date_offset=0)
        
        if not articles:
            print("\n⚠️ 昨日没有新文章")
            return ""
        
        # 2. 筛选文章
        filtered = self.filter.filter(articles)
        
        if not filtered:
            print("\n⚠️ 没有通过筛选的文章")
            return ""
        
        # 3. 生成报告
        report = self.generator.generate(filtered)
        
        # 4. 保存报告
        self._save_report(report, target_date=datetime.now())
        
        # 5. 显示报告
        print("\n" + "=" * 70)
        print("📰 生成的报告")
        print("=" * 70)
        print(report[:1000] + "...")
        
        return report
    
    def _save_report(self, report: str, target_date: datetime = None):
        """保存报告"""
        if target_date is None:
            target_date = datetime.now()
        date_str = target_date.strftime('%Y-%m-%d')
        
        # 保存到daily目录
        daily_dir = Path('/Users/jarvis/.openclaw/workspace/dataloop-website/data/articles/daily')
        daily_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = daily_dir / f"{date_str}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n💾 报告已保存: {report_file}")


def main():
    """主函数"""
    ai_big_news = AIBigNews()
    report = ai_big_news.run()
    
    if report:
        print("\n✅ AI Big News 生成成功!")
    else:
        print("\n⚠️ 未能生成报告")


if __name__ == '__main__':
    main()
