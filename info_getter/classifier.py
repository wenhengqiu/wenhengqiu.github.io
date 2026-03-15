#!/usr/bin/env python3
"""
文章智能分类器
基于内容关键词自动分类到：人工智能、具身智能、自动驾驶、卓驭科技
"""

import re
from typing import Dict, List, Tuple

class ArticleClassifier:
    """文章智能分类器"""
    
    # 分类关键词库（按优先级排序）
    CATEGORY_KEYWORDS = {
        'zhuoyu': {
            'priority': 2,  # 降低优先级，只有明确提到卓驭才分类
            'keywords': [
                '卓驭', '成行平台', '大疆车载', '沈劭劼',
                'ZhuoYu', 'DJI Automotive', '卓驭科技', '卓驭智驾'
            ],
            'name': '卓驭科技'
        },
        'robotics': {
            'priority': 1,
            'keywords': [
                '人形机器人', '具身智能', 'Embodied AI', 'Figure AI', 'Figure 02',
                'Optimus', '特斯拉机器人', '宇树', 'Unitree', '智元', '远征',
                '波士顿动力', 'Boston Dynamics', 'Atlas', '灵巧手', '运动控制',
                '双足', '人形', 'humanoid', '机器人', 'robotics',
                '机械臂', '抓取', '操作', 'locomotion', 'manipulation'
            ],
            'name': '具身智能'
        },
        'autonomous': {
            'priority': 1,
            'keywords': [
                '自动驾驶', 'FSD', 'ADAS', 'NOA', '城市NOA', '高速NOA',
                '智驾', '特斯拉自动驾驶', 'Tesla FSD', 'Waymo', 'Cruise',
                '百度Apollo', 'Apollo', '华为ADS', '小鹏NGP', 'XNGP',
                '蔚来NOP', '理想NOA', '端到端', '端到端自动驾驶',
                '感知', '决策', '规控', '规划控制', '激光雷达', 'LiDAR',
                '纯视觉', '视觉方案', 'BEV', 'Occupancy', '无图',
                '高精地图', 'HD Map', '自动泊车', '代客泊车',
                'Robotaxi', '无人驾驶', 'self-driving', 'autonomous driving'
            ],
            'name': '自动驾驶'
        },
        'llm': {
            'priority': 3,
            'keywords': [
                'GPT', 'LLM', '大模型', '大语言模型', 'Claude', 'Gemini',
                'Transformer', 'OpenAI', 'DeepMind', 'Anthropic', 'AGI',
                '多模态', '推理', 'RAG', 'Agent', 'AI模型',
                'ChatGPT', 'GPT-4', 'GPT-5', 'Llama', 'Mistral',
                '神经网络', '深度学习', '机器学习', '强化学习',
                'NLP', '自然语言处理', '计算机视觉', 'CV',
                '生成式AI', 'Generative AI', 'AIGC', '文生图', '文生视频'
            ],
            'name': '人工智能'
        }
    }
    
    def classify(self, title: str, summary: str = '') -> Tuple[str, float, Dict]:
        """
        对文章进行分类
        
        Returns:
            (category, confidence, details)
        """
        text = f"{title} {summary}".lower()
        
        # 计算每个分类的匹配分数
        scores = {}
        match_details = {}
        
        for category, config in self.CATEGORY_KEYWORDS.items():
            score = 0
            matched_keywords = []
            
            for keyword in config['keywords']:
                keyword_lower = keyword.lower()
                # 标题匹配权重更高
                if keyword_lower in title.lower():
                    score += 3
                    matched_keywords.append(f"{keyword}(标题)")
                # 摘要匹配
                elif keyword_lower in text:
                    score += 1
                    matched_keywords.append(keyword)
            
            # 考虑优先级（优先级数字越小，权重越高）
            priority_boost = (5 - config['priority']) * 0.5
            final_score = score + priority_boost
            
            scores[category] = final_score
            match_details[category] = {
                'score': score,
                'priority_boost': priority_boost,
                'final_score': final_score,
                'matched_keywords': matched_keywords[:5]  # 只显示前5个
            }
        
        # 选择得分最高的分类
        if scores:
            best_category = max(scores, key=scores.get)
            best_score = scores[best_category]
            
            # 计算置信度
            total_score = sum(scores.values())
            confidence = best_score / total_score if total_score > 0 else 0
            
            return best_category, confidence, match_details[best_category]
        
        return 'llm', 0.0, {'reason': 'no match'}
    
    def classify_batch(self, articles: List[Dict]) -> List[Dict]:
        """批量分类文章"""
        results = []
        
        for article in articles:
            title = article.get('title', '')
            summary = article.get('summary', '')
            
            category, confidence, details = self.classify(title, summary)
            
            article['category'] = category
            article['classification_confidence'] = confidence
            article['classification_details'] = details
            
            results.append(article)
        
        return results
    
    def get_category_stats(self, articles: List[Dict]) -> Dict:
        """获取分类统计"""
        stats = {cat: 0 for cat in self.CATEGORY_KEYWORDS.keys()}
        
        for article in articles:
            cat = article.get('category', 'unknown')
            if cat in stats:
                stats[cat] += 1
        
        return stats


# 测试
if __name__ == '__main__':
    classifier = ArticleClassifier()
    
    test_articles = [
        {
            'title': 'Waymo Expands Autonomous Ride-Hailing Service to Austin',
            'summary': 'Waymo announced the expansion of its autonomous ride-hailing service'
        },
        {
            'title': 'Figure AI Unveils Figure 02: Next-Gen Humanoid Robot',
            'summary': 'Figure AI introduces Figure 02 humanoid robot'
        },
        {
            'title': 'OpenAI Releases GPT-5 with Multimodal Capabilities',
            'summary': 'OpenAI announced GPT-5 with advanced reasoning'
        },
        {
            'title': '卓驭科技发布成行平台3.0',
            'summary': '卓驭科技正式发布成行平台3.0，支持城市NOA'
        },
        {
            'title': 'Tesla FSD V12: End-to-End Neural Networks',
            'summary': 'Tesla releases FSD V12 with end-to-end neural networks'
        }
    ]
    
    print("文章分类测试:")
    print("=" * 70)
    
    for article in test_articles:
        category, confidence, details = classifier.classify(
            article['title'], article['summary']
        )
        
        cat_name = classifier.CATEGORY_KEYWORDS[category]['name']
        
        print(f"\n标题: {article['title'][:50]}...")
        print(f"分类: {cat_name} ({category})")
        print(f"置信度: {confidence:.2f}")
        print(f"匹配关键词: {', '.join(details.get('matched_keywords', [])[:3])}")
