"""
Info-Getter Publisher Module
自动发布文章到 GitHub，支持 SimHash 去重和质量评分过滤
"""

import json
import os
import re
import subprocess
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class Article:
    """文章数据模型 - 符合 PRD v6.1 规范"""
    id: str
    title: str
    title_zh: str  # 中文标题（翻译）
    summary: str
    summary_zh: str  # 中文摘要（翻译）
    content: str
    category: str
    publish_date: str
    display_date: str
    source: Dict[str, str]  # 对象格式: {name, type}
    url: str
    tags: List[str] = field(default_factory=list)
    is_featured: bool = False
    quality_score: float = 0.0
    simhash: str = ""
    translated: bool = True  # 是否已翻译
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Article':
        """从字典创建 Article 对象"""
        # 处理不同字段命名风格
        publish_date = data.get('publish_date') or data.get('publishDate', '')
        display_date = data.get('display_date') or data.get('displayDate', '')
        is_featured = data.get('is_featured') or data.get('isFeatured', False)
        
        # 处理 source 字段（兼容字符串和对象格式）
        source = data.get('source', '')
        if isinstance(source, str):
            source = {'name': source, 'type': 'tech_media'}
        
        return cls(
            id=data.get('id', ''),
            title=data.get('title', ''),
            title_zh=data.get('title_zh', data.get('title', '')),  # 降级处理
            summary=data.get('summary', ''),
            summary_zh=data.get('summary_zh', data.get('summary', '')),  # 降级处理
            content=data.get('content', ''),
            category=data.get('category', ''),
            publish_date=publish_date,
            display_date=display_date,
            source=source,
            url=data.get('url', data.get('original_url', '')),
            tags=data.get('tags', []),
            is_featured=is_featured,
            quality_score=data.get('quality_score', 0.0),
            simhash=data.get('simhash', ''),
            translated=data.get('translated', True)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典 - PRD v6.1 格式"""
        return {
            'id': self.id,
            'title': self.title,
            'title_zh': self.title_zh,
            'summary': self.summary,
            'summary_zh': self.summary_zh,
            'url': self.url,
            'source': self.source,
            'category': self.category,
            'quality_score': round(self.quality_score, 2),
            'published_at': self.publish_date,
            'translated': self.translated,
            'tags': self.tags
        }


class SimHash:
    """SimHash 实现用于文本去重"""
    
    def __init__(self, hashbits: int = 64):
        self.hashbits = hashbits
    
    def _string_hash(self, s: str) -> int:
        """计算字符串哈希值"""
        if s == "":
            return 0
        x = ord(s[0]) << 7
        m = 1000003
        mask = 2 ** self.hashbits - 1
        for c in s:
            x = ((x * m) ^ ord(c)) & mask
        x ^= len(s)
        if x == -1:
            x = -2
        return x
    
    def _tokenize(self, text: str) -> List[str]:
        """分词 - 使用简单的字符级 n-gram"""
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', text.lower())
        # 使用 3-gram
        return [text[i:i+3] for i in range(len(text) - 2)] if len(text) >= 3 else [text]
    
    def compute(self, text: str) -> str:
        """计算 SimHash 值"""
        tokens = self._tokenize(text)
        if not tokens:
            return "0" * self.hashbits
        
        # 加权哈希
        v = [0] * self.hashbits
        for token in tokens:
            # 使用词频作为权重
            weight = tokens.count(token)
            hash_val = self._string_hash(token)
            
            for i in range(self.hashbits):
                bit = (hash_val >> i) & 1
                if bit == 1:
                    v[i] += weight
                else:
                    v[i] -= weight
        
        # 生成指纹
        fingerprint = 0
        for i in range(self.hashbits):
            if v[i] > 0:
                fingerprint |= 1 << i
        
        return format(fingerprint, f'0{self.hashbits // 4}x')
    
    def hamming_distance(self, hash1: str, hash2: str) -> int:
        """计算两个 SimHash 的汉明距离"""
        if not hash1 or not hash2:
            return self.hashbits
        
        x = int(hash1, 16) ^ int(hash2, 16)
        distance = 0
        while x:
            distance += 1
            x &= x - 1
        return distance
    
    def similarity(self, hash1: str, hash2: str) -> float:
        """计算相似度 (0-1)"""
        distance = self.hamming_distance(hash1, hash2)
        return 1 - (distance / self.hashbits)


class QualityScorer:
    """文章质量评分器"""
    
    def __init__(self):
        self.min_content_length = 100  # 最小内容长度
        self.min_summary_length = 20   # 最小摘要长度
    
    def score(self, article: Article) -> float:
        """
        计算文章质量分数 (0-1)
        
        评分维度：
        1. 内容完整性 (30%)
        2. 摘要质量 (20%)
        3. 标题质量 (20%)
        4. 元数据完整性 (20%)
        5. 标签丰富度 (10%)
        """
        scores = []
        
        # 1. 内容完整性 (30%)
        content_score = self._score_content(article.content)
        scores.append((content_score, 0.3))
        
        # 2. 摘要质量 (20%)
        summary_score = self._score_summary(article.summary)
        scores.append((summary_score, 0.2))
        
        # 3. 标题质量 (20%)
        title_score = self._score_title(article.title)
        scores.append((title_score, 0.2))
        
        # 4. 元数据完整性 (20%)
        metadata_score = self._score_metadata(article)
        scores.append((metadata_score, 0.2))
        
        # 5. 标签丰富度 (10%)
        tags_score = self._score_tags(article.tags)
        scores.append((tags_score, 0.1))
        
        # 加权平均
        total_weight = sum(w for _, w in scores)
        weighted_score = sum(s * w for s, w in scores) / total_weight if total_weight > 0 else 0
        
        return round(weighted_score, 3)
    
    def _score_content(self, content: str) -> float:
        """评分内容质量"""
        if not content:
            return 0.0
        
        # 去除 HTML 标签
        text = re.sub(r'<[^>]+>', '', content)
        text_length = len(text.strip())
        
        if text_length < self.min_content_length:
            return 0.3
        elif text_length < 500:
            return 0.6
        elif text_length < 1000:
            return 0.8
        else:
            return 1.0
    
    def _score_summary(self, summary: str) -> float:
        """评分摘要质量"""
        if not summary:
            return 0.0
        
        length = len(summary.strip())
        if length < self.min_summary_length:
            return 0.3
        elif length < 50:
            return 0.6
        elif length < 100:
            return 0.8
        else:
            return 1.0
    
    def _score_title(self, title: str) -> float:
        """评分标题质量"""
        if not title:
            return 0.0
        
        title = title.strip()
        length = len(title)
        
        # 标题长度适中
        if length < 5 or length > 100:
            return 0.5
        
        # 包含关键词加分
        score = 0.7
        if any(kw in title for kw in ['发布', '推出', '宣布', '获得', '完成']):
            score += 0.1
        if re.search(r'[\d\.]+', title):  # 包含数字/版本号
            score += 0.1
        
        return min(score, 1.0)
    
    def _score_metadata(self, article: Article) -> float:
        """评分元数据完整性"""
        required_fields = [
            article.id, article.title, article.category,
            article.publish_date, article.source, article.url
        ]
        
        filled = sum(1 for f in required_fields if f)
        return filled / len(required_fields)
    
    def _score_tags(self, tags: List[str]) -> float:
        """评分标签丰富度"""
        if not tags:
            return 0.0
        
        count = len(tags)
        if count < 2:
            return 0.4
        elif count < 4:
            return 0.7
        else:
            return 1.0


class Publisher:
    """
    文章发布器
    
    功能：
    1. 读取现有 JSON 文件
    2. SimHash 去重检查
    3. 质量评分过滤（<0.7 不发布）
    4. Git 自动提交和推送
    """
    
    def __init__(
        self,
        data_dir: str,
        quality_threshold: float = 0.7,
        similarity_threshold: float = 0.85,
        auto_git: bool = True
    ):
        self.data_dir = Path(data_dir)
        self.quality_threshold = quality_threshold
        self.similarity_threshold = similarity_threshold
        self.auto_git = auto_git
        
        self.simhash = SimHash()
        self.scorer = QualityScorer()
        
        # 确保数据目录存在
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def load_existing_articles(self, category: Optional[str] = None) -> List[Article]:
        """加载现有文章"""
        articles = []
        
        # 确定搜索路径
        if category:
            search_paths = [self.data_dir / category]
        else:
            search_paths = [self.data_dir / "daily", self.data_dir / "research"]
        
        for base_path in search_paths:
            if not base_path.exists():
                continue
            
            # 递归查找所有 JSON 文件
            for json_file in base_path.rglob("*.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            for item in data:
                                articles.append(Article.from_dict(item))
                        else:
                            articles.append(Article.from_dict(data))
                except Exception as e:
                    print(f"Warning: Failed to load {json_file}: {e}")
        
        return articles
    
    def check_duplicate(self, article: Article, existing_articles: List[Article]) -> Tuple[bool, Optional[Article], float]:
        """
        检查文章是否重复
        
        Returns:
            (是否重复, 最相似的文章, 相似度)
        """
        if not article.simhash:
            article.simhash = self.simhash.compute(article.title + article.summary)
        
        max_similarity = 0.0
        most_similar = None
        
        for existing in existing_articles:
            if not existing.simhash:
                existing.simhash = self.simhash.compute(existing.title + existing.summary)
            
            similarity = self.simhash.similarity(article.simhash, existing.simhash)
            if similarity > max_similarity:
                max_similarity = similarity
                most_similar = existing
        
        is_duplicate = max_similarity >= self.similarity_threshold
        return is_duplicate, most_similar, max_similarity
    
    def evaluate_quality(self, article: Article) -> float:
        """评估文章质量"""
        score = self.scorer.score(article)
        article.quality_score = score
        return score
    
    def should_publish(self, article: Article, existing_articles: List[Article]) -> Tuple[bool, Dict[str, Any]]:
        """
        判断是否应该发布文章
        
        Returns:
            (是否发布, 详细信息)
        """
        result = {
            'passed': True,
            'quality_score': 0.0,
            'is_duplicate': False,
            'similarity': 0.0,
            'duplicate_with': None,
            'reasons': []
        }
        
        # 1. 质量评分
        quality_score = self.evaluate_quality(article)
        result['quality_score'] = quality_score
        
        if quality_score < self.quality_threshold:
            result['passed'] = False
            result['reasons'].append(
                f"Quality score {quality_score} below threshold {self.quality_threshold}"
            )
        
        # 2. 去重检查
        is_duplicate, duplicate_with, similarity = self.check_duplicate(article, existing_articles)
        result['is_duplicate'] = is_duplicate
        result['similarity'] = similarity
        result['duplicate_with'] = duplicate_with.id if duplicate_with else None
        
        if is_duplicate:
            result['passed'] = False
            result['reasons'].append(
                f"Duplicate detected with similarity {similarity:.3f} (article: {duplicate_with.id})"
            )
        
        return result['passed'], result
    
    def get_target_file(self, article: Article) -> Path:
        """确定文章应该保存到的文件路径"""
        date = datetime.strptime(article.publish_date, "%Y-%m-%d")
        
        if article.category in ['daily', 'company', 'product']:
            # 日常新闻按日期存储
            target_dir = self.data_dir / "daily" / str(date.year) / f"{date.month:02d}"
            target_file = target_dir / f"{article.publish_date}.json"
        else:
            # 研究类按类别存储
            target_file = self.data_dir / "research" / f"{article.category}.json"
        
        return target_file
    
    def add_article(self, article: Article, existing_articles: List[Article]) -> Dict[str, Any]:
        """
        添加单篇文章
        
        Returns:
            操作结果信息
        """
        # 检查是否应该发布
        should_pub, check_result = self.should_publish(article, existing_articles)
        
        if not should_pub:
            return {
                'success': False,
                'article_id': article.id,
                'reason': '; '.join(check_result['reasons']),
                'details': check_result
            }
        
        # 确定目标文件
        target_file = self.get_target_file(article)
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 加载现有数据
        existing_data = []
        if target_file.exists():
            try:
                with open(target_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    if not isinstance(existing_data, list):
                        existing_data = [existing_data]
            except Exception as e:
                print(f"Warning: Failed to read {target_file}: {e}")
        
        # 检查 ID 是否已存在
        for item in existing_data:
            if item.get('id') == article.id:
                return {
                    'success': False,
                    'article_id': article.id,
                    'reason': f"Article with ID {article.id} already exists",
                    'details': check_result
                }
        
        # 添加新文章
        existing_data.append(article.to_dict())
        
        # 保存文件
        with open(target_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        
        return {
            'success': True,
            'article_id': article.id,
            'file': str(target_file),
            'quality_score': check_result['quality_score'],
            'similarity': check_result['similarity'],
            'details': check_result
        }
    
    def publish(self, articles: List[Article]) -> Dict[str, Any]:
        """
        发布文章列表
        
        Returns:
            发布结果统计
        """
        # 加载所有现有文章用于去重
        existing_articles = self.load_existing_articles()
        
        results = {
            'total': len(articles),
            'published': 0,
            'rejected': 0,
            'duplicates': 0,
            'low_quality': 0,
            'details': []
        }
        
        published_files = set()
        
        for article in articles:
            result = self.add_article(article, existing_articles)
            results['details'].append(result)
            
            if result['success']:
                results['published'] += 1
                published_files.add(result['file'])
                # 添加到现有文章列表，防止同一批次内重复
                existing_articles.append(article)
            else:
                results['rejected'] += 1
                if 'Duplicate' in result['reason']:
                    results['duplicates'] += 1
                elif 'Quality' in result['reason']:
                    results['low_quality'] += 1
        
        # Git 操作
        if self.auto_git and published_files:
            git_result = self._git_commit_and_push(published_files)
            results['git'] = git_result
        
        return results
    
    def _git_commit_and_push(self, files: set) -> Dict[str, Any]:
        """执行 Git 提交和推送"""
        result = {
            'success': False,
            'commits': [],
            'errors': []
        }
        
        try:
            # 获取仓库根目录
            repo_root = self._get_git_root()
            if not repo_root:
                result['errors'].append("Not a git repository")
                return result
            
            # 添加文件
            for file_path in files:
                rel_path = os.path.relpath(file_path, repo_root)
                cmd = ['git', 'add', rel_path]
                proc = subprocess.run(
                    cmd, cwd=repo_root,
                    capture_output=True, text=True
                )
                if proc.returncode != 0:
                    result['errors'].append(f"git add failed: {proc.stderr}")
            
            # 检查是否有变更
            status_proc = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=repo_root, capture_output=True, text=True
            )
            
            if not status_proc.stdout.strip():
                result['success'] = True
                result['commits'].append("No changes to commit")
                return result
            
            # 提交
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_msg = f"feat: publish articles at {timestamp}\n\n- Published {len(files)} article(s)\n- Auto-generated by Info-Getter Publisher"
            
            commit_proc = subprocess.run(
                ['git', 'commit', '-m', commit_msg],
                cwd=repo_root, capture_output=True, text=True
            )
            
            if commit_proc.returncode != 0:
                result['errors'].append(f"git commit failed: {commit_proc.stderr}")
                return result
            
            result['commits'].append(commit_msg)
            
            # 推送到 user-pages remote
            push_proc = subprocess.run(
                ['git', 'push', 'user-pages', 'master'],
                cwd=repo_root, capture_output=True, text=True
            )
            
            if push_proc.returncode != 0:
                result['errors'].append(f"git push failed: {push_proc.stderr}")
            else:
                result['success'] = True
                result['commits'].append("Pushed to remote")
        
        except Exception as e:
            result['errors'].append(str(e))
        
        return result
    
    def _get_git_root(self) -> Optional[str]:
        """获取 Git 仓库根目录"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--show-toplevel'],
                cwd=self.data_dir, capture_output=True, text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None


# 便捷函数
def publish_articles(
    articles_data: List[Dict[str, Any]],
    data_dir: str = None,
    quality_threshold: float = 0.7,
    auto_git: bool = True
) -> Dict[str, Any]:
    """
    便捷函数：发布文章列表
    
    Args:
        articles_data: 文章数据列表
        data_dir: 数据目录，默认使用环境变量或默认路径
        quality_threshold: 质量阈值
        auto_git: 是否自动 Git 提交
    
    Returns:
        发布结果
    """
    if data_dir is None:
        data_dir = os.environ.get(
            'INFOGETTER_DATA_DIR',
            '/Users/jarvis/.openclaw/workspace/dataloop-website/data/articles'
        )
    
    publisher = Publisher(
        data_dir=data_dir,
        quality_threshold=quality_threshold,
        auto_git=auto_git
    )
    
    articles = [Article.from_dict(data) for data in articles_data]
    return publisher.publish(articles)


def publish_single_article(
    article_data: Dict[str, Any],
    data_dir: str = None,
    quality_threshold: float = 0.7,
    auto_git: bool = True
) -> Dict[str, Any]:
    """便捷函数：发布单篇文章"""
    return publish_articles(
        [article_data],
        data_dir=data_dir,
        quality_threshold=quality_threshold,
        auto_git=auto_git
    )


if __name__ == "__main__":
    # 测试示例
    test_article = {
        "id": "2026-03-14-test001",
        "title": "测试文章：AI 技术新突破",
        "summary": "这是一篇测试文章，用于验证发布模块的功能。",
        "content": "<p>测试内容</p>",
        "category": "llm",
        "publishDate": "2026-03-14",
        "displayDate": "3月14日",
        "source": "测试源",
        "url": "https://example.com/test",
        "tags": ["测试", "AI"],
        "isFeatured": False
    }
    
    result = publish_single_article(test_article, auto_git=False)
    print(json.dumps(result, ensure_ascii=False, indent=2))
