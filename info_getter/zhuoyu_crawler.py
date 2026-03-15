#!/usr/bin/env python3
"""
卓驭科技专用爬虫
针对卓驭科技的特殊信息源设计
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict

class ZhuoyuCrawler:
    """卓驭科技专用爬虫"""
    
    # 卓驭科技相关关键词
    KEYWORDS = [
        '卓驭科技',
        '卓驭', 
        '大疆车载',
        '成行平台',
        '沈劭劼',
        '卓驭端到端',
        '卓驭智驾'
    ]
    
    # 信息源配置
    SOURCES = {
        'baidu_news': {
            'name': '百度资讯',
            'url': 'https://www.baidu.com/s?rtt=4&bsst=1&cl=2&tn=news&word={keyword}',
            'type': 'search_engine'
        },
        'google_news': {
            'name': 'Google新闻',
            'url': 'https://news.google.com/search?q={keyword}&hl=zh-CN',
            'type': 'search_engine'
        },
        'leiphone': {
            'name': '雷锋网',
            'url': 'https://www.leiphone.com/tag/%E5%8D%93%E9%A9%AD',
            'type': 'tech_media'
        },
        '36kr': {
            'name': '36氪',
            'url': 'https://36kr.com/search/articles/{keyword}',
            'type': 'tech_media'
        },
        'sina_auto': {
            'name': '新浪汽车',
            'url': 'https://auto.sina.com.cn/',
            'type': 'auto_media'
        },
        'autohome': {
            'name': '汽车之家',
            'url': 'https://www.autohome.com.cn/',
            'type': 'auto_media'
        },
        'pingwest': {
            'name': '品玩',
            'url': 'https://www.pingwest.com/s?wd={keyword}',
            'type': 'tech_media'
        }
    }
    
    def __init__(self):
        self.articles = []
        
    def crawl_all(self) -> List[Dict]:
        """爬取所有来源"""
        print("=" * 70)
        print("🚗 卓驭科技专用爬虫")
        print("=" * 70)
        
        # 1. 科技媒体RSS/API
        self._crawl_tech_media()
        
        # 2. 搜索引擎
        self._crawl_search_engines()
        
        # 3. 行业媒体
        self._crawl_auto_media()
        
        # 去重
        self._deduplicate()
        
        # 保存
        self._save()
        
        return self.articles
    
    def _crawl_tech_media(self):
        """爬取科技媒体"""
        print("\n📡 爬取科技媒体...")
        
        # 使用CDP浏览器访问雷锋网
        try:
            articles = self._cdp_crawl(
                'https://www.leiphone.com/tag/%E5%8D%93%E9%A9%AD',
                '雷锋网'
            )
            self.articles.extend(articles)
            print(f"  ✅ 雷锋网: {len(articles)} 篇")
        except Exception as e:
            print(f"  ⚠️ 雷锋网失败: {e}")
        
        # 36氪
        try:
            articles = self._cdp_crawl(
                'https://36kr.com/search/articles/%E5%8D%93%E9%A9%AD',
                '36氪'
            )
            self.articles.extend(articles)
            print(f"  ✅ 36氪: {len(articles)} 篇")
        except Exception as e:
            print(f"  ⚠️ 36氪失败: {e}")
    
    def _crawl_search_engines(self):
        """爬取搜索引擎"""
        print("\n🔍 爬取搜索引擎...")
        
        for keyword in ['卓驭科技', '大疆车载']:
            try:
                url = f"https://www.baidu.com/s?rtt=4&tn=news&word={keyword}"
                articles = self._cdp_crawl(url, '百度资讯', keyword)
                self.articles.extend(articles)
                print(f"  ✅ 百度-{keyword}: {len(articles)} 篇")
            except Exception as e:
                print(f"  ⚠️ 百度-{keyword}失败: {e}")
    
    def _crawl_auto_media(self):
        """爬取汽车媒体"""
        print("\n🚙 爬取汽车媒体...")
        # 这里可以添加汽车之家的爬取逻辑
        print("  ℹ️ 汽车媒体爬取待实现")
    
    def _cdp_crawl(self, url: str, source_name: str, keyword: str = '') -> List[Dict]:
        """
        使用CDP浏览器爬取
        
        实际实现需要调用CDP浏览器
        这里返回模拟数据作为示例
        """
        # TODO: 实际调用CDP浏览器
        # 返回空列表，实际实现时需要替换
        return []
    
    def _deduplicate(self):
        """去重"""
        seen = set()
        unique = []
        for a in self.articles:
            key = a.get('title', '')[:30]
            if key and key not in seen:
                seen.add(key)
                unique.append(a)
        self.articles = unique
        print(f"\n🔄 去重后: {len(self.articles)} 篇")
    
    def _save(self):
        """保存文章"""
        if not self.articles:
            print("\n⚠️ 没有新文章")
            return
        
        # 添加元数据
        for a in self.articles:
            a['category'] = 'zhuoyu'
            a['crawled_at'] = datetime.now().isoformat()
            a['quality_score'] = self._calculate_quality(a)
        
        # 保存到文件
        output_file = Path('/Users/jarvis/.openclaw/workspace/dataloop-website/data/articles/research/zhuoyu_crawled.json')
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.articles, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 已保存: {output_file}")
        
        # 合并到主文件
        self._merge_to_main()
    
    def _calculate_quality(self, article: Dict) -> float:
        """计算文章质量分"""
        score = 0.5  # 基础分
        
        # 来源权重
        source_type = article.get('source', {}).get('type', '')
        if source_type == 'official':
            score += 0.4
        elif source_type == 'tech_media':
            score += 0.3
        elif source_type == 'auto_media':
            score += 0.2
        
        # 内容长度
        content_len = len(article.get('summary', ''))
        if content_len > 200:
            score += 0.1
        
        # 关键词匹配
        title = article.get('title', '')
        if '卓驭' in title or '成行' in title:
            score += 0.1
        
        return min(score, 1.0)
    
    def _merge_to_main(self):
        """合并到主zhuoyu.json文件"""
        main_file = Path('/Users/jarvis/.openclaw/workspace/dataloop-website/data/articles/research/zhuoyu.json')
        
        # 读取现有文章
        existing = []
        if main_file.exists():
            with open(main_file, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        
        # 合并
        existing_ids = {a.get('id') for a in existing}
        new_articles = [a for a in self.articles if a.get('id') not in existing_ids]
        
        all_articles = existing + new_articles
        
        # 按日期排序
        all_articles.sort(key=lambda x: x.get('published_at', ''), reverse=True)
        
        # 保存
        with open(main_file, 'w', encoding='utf-8') as f:
            json.dump(all_articles, f, ensure_ascii=False, indent=2)
        
        print(f"💾 合并后共 {len(all_articles)} 篇")
        
        # Git提交
        import subprocess
        try:
            subprocess.run(['git', 'add', str(main_file)], 
                         check=True, cwd='/Users/jarvis/.openclaw/workspace/dataloop-website')
            subprocess.run(['git', 'commit', '-m', f'[卓驭爬虫] 添加 {len(new_articles)} 篇新文章'], 
                         check=True, cwd='/Users/jarvis/.openclaw/workspace/dataloop-website')
            subprocess.run(['git', 'push', 'user-pages', 'master'], 
                         check=True, cwd='/Users/jarvis/.openclaw/workspace/dataloop-website')
            print("✅ Git推送完成")
        except Exception as e:
            print(f"⚠️ Git操作失败: {e}")


def main():
    """主函数"""
    crawler = ZhuoyuCrawler()
    articles = crawler.crawl_all()
    print(f"\n🎉 完成! 共采集 {len(articles)} 篇卓驭科技文章")


if __name__ == '__main__':
    main()
