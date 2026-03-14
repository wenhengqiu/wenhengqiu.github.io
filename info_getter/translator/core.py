# -*- coding: utf-8 -*-
"""
Info-Getter 翻译模块 (Translator)
使用 OpenClaw 大模型 API 进行智能翻译

功能：
1. 翻译标题（20字内）和摘要（100字内）
2. 保护专有名词（GPT、Tesla等不翻译）
3. 实现降级策略（翻译失败保留原文）
"""

import os
import re
import json
import subprocess
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from functools import lru_cache

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class TranslationResult:
    """翻译结果数据结构"""
    title: str
    summary: str
    success: bool
    error_message: Optional[str] = None
    original_title: Optional[str] = None
    original_summary: Optional[str] = None


class TranslatorConfig:
    """翻译器配置"""
    
    # 默认模型配置
    DEFAULT_MODEL = "moonshot/kimi-k2.5"
    
    # 长度限制
    MAX_TITLE_LENGTH = 20
    MAX_SUMMARY_LENGTH = 100
    
    # 专有名词保护列表（这些词不会被翻译）
    PROTECTED_TERMS = {
        # AI/大模型
        "GPT", "GPT-3", "GPT-4", "GPT-4o", "GPT-o1", "GPT-o3",
        "LLM", "LLMs", "AI", "AGI", "OpenAI", "Anthropic", "Claude",
        "Gemini", "DeepMind", "Llama", "Mistral", "BERT", "Transformer",
        "PyTorch", "TensorFlow", "HuggingFace", "LangChain", "OpenClaw",
        
        # 自动驾驶
        "Tesla", "FSD", "Autopilot", "Waymo", "Cruise", "Apollo",
        "NOA", "ADAS", "Lidar", "Radar", "BEV", "OCC",
        
        # 机器人/具身智能
        "Figure AI", "Optimus", "Boston Dynamics", "Atlas", "Spot",
        "Embodied AI", "Humanoid", "Unitree", 
        
        # 科技公司
        "Apple", "Google", "Microsoft", "Amazon", "Meta", "NVIDIA",
        "Intel", "AMD", "Qualcomm", "ARM", "TSMC", "ASML",
        
        # 编程/技术
        "API", "SDK", "JSON", "YAML", "XML", "HTML", "CSS", "SQL",
        "HTTP", "HTTPS", "REST", "GraphQL", "gRPC", "WebSocket",
        "Docker", "Kubernetes", "K8s", "Linux", "Ubuntu", "Git",
        "Python", "JavaScript", "TypeScript", "Rust", "Go", "Java",
        "React", "Vue", "Angular", "Node.js", "Next.js",
        
        # 人名
        "Elon Musk", "Sam Altman", "Demis Hassabis", "Yann LeCun",
        "Geoffrey Hinton", "Andrew Ng", "Fei-Fei Li",
        
        # 其他
        "CEO", "CTO", "CFO", "COO", "VP", "PM",
        "SaaS", "PaaS", "IaaS", "B2B", "B2C", "DTC",
        "IPO", "VC", "PE", "ROI", "KPI", "OKR",
        "USA", "UK", "EU", "UN", "NASA", "MIT", "Stanford",
    }
    
    # 中文专有名词保护
    PROTECTED_CN_TERMS = {
        "卓驭科技", "成行平台", "大疆车载", "沈劭劼",
        "小鹏", "蔚来", "理想", "小米", "华为", "比亚迪",
        "宇树科技", "智元机器人", "傅利叶智能",
    }


class OpenClawTranslator:
    """
    OpenClaw 大模型翻译器
    
    使用 OpenClaw CLI 调用本地 Gateway 进行翻译
    """
    
    def __init__(
        self,
        model: str = TranslatorConfig.DEFAULT_MODEL,
        max_title_length: int = TranslatorConfig.MAX_TITLE_LENGTH,
        max_summary_length: int = TranslatorConfig.MAX_SUMMARY_LENGTH,
        protected_terms: Optional[set] = None
    ):
        self.model = model
        self.max_title_length = max_title_length
        self.max_summary_length = max_summary_length
        self.protected_terms = protected_terms or TranslatorConfig.PROTECTED_TERMS
        self.protected_cn_terms = TranslatorConfig.PROTECTED_CN_TERMS
        
        # 编译专有名词匹配正则
        self._compile_protected_patterns()
    
    def _compile_protected_patterns(self):
        """编译专有名词保护模式"""
        # 按长度降序排列，优先匹配更长的词
        sorted_terms = sorted(self.protected_terms, key=len, reverse=True)
        pattern = r'\b(' + '|'.join(re.escape(term) for term in sorted_terms) + r')\b'
        self.protected_pattern = re.compile(pattern, re.IGNORECASE)
        
        # 中文专有名词
        if self.protected_cn_terms:
            cn_pattern = '(' + '|'.join(re.escape(term) for term in self.protected_cn_terms) + ')'
            self.protected_cn_pattern = re.compile(cn_pattern)
        else:
            self.protected_cn_pattern = None
    
    def _protect_terms(self, text: str) -> tuple[str, Dict[str, str]]:
        """
        将专有名词替换为占位符，防止被翻译
        
        Returns:
            (处理后的文本, 占位符映射表)
        """
        placeholders = {}
        counter = 0
        
        def replace_match(match):
            nonlocal counter
            original = match.group(0)
            placeholder = f"<<PROTECTED_{counter}>>"
            placeholders[placeholder] = original
            counter += 1
            return placeholder
        
        # 保护英文专有名词
        protected_text = self.protected_pattern.sub(replace_match, text)
        
        # 保护中文专有名词
        if self.protected_cn_pattern:
            protected_text = self.protected_cn_pattern.sub(replace_match, protected_text)
        
        return protected_text, placeholders
    
    def _restore_terms(self, text: str, placeholders: Dict[str, str]) -> str:
        """恢复被保护的专有名词"""
        for placeholder, original in placeholders.items():
            text = text.replace(placeholder, original)
        return text
    
    def _call_openclaw_agent(self, prompt: str) -> Optional[str]:
        """
        调用 OpenClaw Agent 进行翻译
        
        使用 openclaw agent 命令调用本地 Gateway
        """
        try:
            # 构建系统提示词
            system_prompt = """你是一个专业的翻译助手。请准确翻译用户提供的文本到中文。
要求：
1. 保持原文意思准确
2. 语言流畅自然
3. 不要添加额外解释
4. 直接返回翻译结果"""
            
            # 构建完整消息
            full_prompt = f"{system_prompt}\n\n需要翻译的文本：\n{prompt}\n\n翻译结果："
            
            # 调用 openclaw agent
            cmd = [
                "openclaw", "agent",
                "--model", self.model,
                "--message", full_prompt
            ]
            
            logger.debug(f"Calling OpenClaw with command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8'
            )
            
            if result.returncode != 0:
                logger.error(f"OpenClaw error: {result.stderr}")
                return None
            
            # 解析输出
            output = result.stdout.strip()
            
            # 尝试从 JSON 输出中提取内容
            try:
                json_data = json.loads(output)
                if isinstance(json_data, dict):
                    # 尝试不同的字段
                    for key in ['response', 'content', 'text', 'message', 'result']:
                        if key in json_data:
                            return json_data[key]
                    # 如果没有找到，返回整个 JSON 的字符串形式
                    return str(json_data)
            except json.JSONDecodeError:
                # 不是 JSON，直接返回文本
                pass
            
            return output if output else None
            
        except subprocess.TimeoutExpired:
            logger.error("OpenClaw agent timeout")
            return None
        except Exception as e:
            logger.error(f"Error calling OpenClaw: {e}")
            return None
    
    def _translate_text(self, text: str, max_length: Optional[int] = None) -> Optional[str]:
        """
        翻译单段文本
        
        Args:
            text: 要翻译的文本
            max_length: 最大长度限制
        
        Returns:
            翻译后的文本，失败返回 None
        """
        if not text or not text.strip():
            return text
        
        # 保护专有名词
        protected_text, placeholders = self._protect_terms(text)
        
        # 构建翻译提示
        length_hint = f"（控制在{max_length}字以内）" if max_length else ""
        prompt = f"请将以下文本翻译成中文{length_hint}：\n\n{protected_text}"
        
        # 调用翻译
        translated = self._call_openclaw_agent(prompt)
        
        if translated is None:
            return None
        
        # 恢复专有名词
        translated = self._restore_terms(translated, placeholders)
        
        # 清理翻译结果
        translated = self._clean_translation(translated)
        
        # 截断到最大长度
        if max_length and len(translated) > max_length:
            translated = translated[:max_length-1] + "…"
        
        return translated
    
    def _clean_translation(self, text: str) -> str:
        """清理翻译结果"""
        # 移除常见的多余前缀
        prefixes_to_remove = [
            "翻译结果：", "翻译：", "译文：", "中文翻译：",
            "Translation:", "Translated:", "中文：",
        ]
        
        for prefix in prefixes_to_remove:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
        
        # 移除引号
        text = text.strip('"\'')
        
        return text.strip()
    
    def translate(
        self,
        title: str,
        summary: Optional[str] = None,
        fallback_to_original: bool = True
    ) -> TranslationResult:
        """
        翻译标题和摘要
        
        Args:
            title: 标题（英文）
            summary: 摘要（英文），可选
            fallback_to_original: 翻译失败时是否回退到原文
        
        Returns:
            TranslationResult 对象
        """
        original_title = title
        original_summary = summary
        
        # 翻译标题
        translated_title = self._translate_text(title, self.max_title_length)
        
        if translated_title is None:
            if fallback_to_original:
                logger.warning(f"Title translation failed, using original: {title}")
                translated_title = title
            else:
                return TranslationResult(
                    title=title,
                    summary=summary or "",
                    success=False,
                    error_message="Title translation failed",
                    original_title=original_title,
                    original_summary=original_summary
                )
        
        # 翻译摘要
        translated_summary = None
        if summary:
            translated_summary = self._translate_text(summary, self.max_summary_length)
            
            if translated_summary is None:
                if fallback_to_original:
                    logger.warning(f"Summary translation failed, using original")
                    translated_summary = summary
                else:
                    return TranslationResult(
                        title=translated_title,
                        summary=summary,
                        success=False,
                        error_message="Summary translation failed",
                        original_title=original_title,
                        original_summary=original_summary
                    )
        
        return TranslationResult(
            title=translated_title,
            summary=translated_summary or "",
            success=True,
            original_title=original_title,
            original_summary=original_summary
        )
    
    def translate_batch(
        self,
        items: List[Dict[str, str]],
        fallback_to_original: bool = True
    ) -> List[TranslationResult]:
        """
        批量翻译
        
        Args:
            items: 包含 title 和 summary 的字典列表
            fallback_to_original: 翻译失败时是否回退到原文
        
        Returns:
            TranslationResult 列表
        """
        results = []
        for item in items:
            result = self.translate(
                title=item.get('title', ''),
                summary=item.get('summary'),
                fallback_to_original=fallback_to_original
            )
            results.append(result)
        return results


class MockTranslator(OpenClawTranslator):
    """
    模拟翻译器（用于测试）
    不调用真实 API，返回模拟翻译结果
    """
    
    def _call_openclaw_agent(self, prompt: str) -> Optional[str]:
        """模拟翻译调用"""
        # 提取要翻译的文本（在 "：" 之后）
        if "：" in prompt:
            text = prompt.split("：", 1)[1].strip()
        else:
            text = prompt
        
        # 简单的模拟翻译（实际使用时应替换为真实翻译）
        return f"[模拟翻译] {text[:20]}..."


def create_translator(
    model: Optional[str] = None,
    use_mock: bool = False,
    **kwargs
) -> OpenClawTranslator:
    """
    工厂函数：创建翻译器实例
    
    Args:
        model: 模型名称，默认使用配置中的模型
        use_mock: 是否使用模拟翻译器（用于测试）
        **kwargs: 其他配置参数
    
    Returns:
        翻译器实例
    """
    if use_mock:
        return MockTranslator(model=model, **kwargs)
    
    return OpenClawTranslator(model=model or TranslatorConfig.DEFAULT_MODEL, **kwargs)


# 便捷函数
def translate_article(
    title: str,
    summary: Optional[str] = None,
    **kwargs
) -> TranslationResult:
    """
    便捷函数：翻译单篇文章
    
    示例：
        result = translate_article(
            title="OpenAI Releases GPT-4o",
            summary="OpenAI has announced the release of GPT-4o..."
        )
        print(result.title)  # 中文标题
        print(result.summary)  # 中文摘要
    """
    translator = create_translator(**kwargs)
    return translator.translate(title, summary)


def translate_articles(
    articles: List[Dict[str, str]],
    **kwargs
) -> List[TranslationResult]:
    """
    便捷函数：批量翻译文章
    
    示例：
        articles = [
            {"title": "Title 1", "summary": "Summary 1"},
            {"title": "Title 2", "summary": "Summary 2"},
        ]
        results = translate_articles(articles)
        for r in results:
            print(r.title, r.summary)
    """
    translator = create_translator(**kwargs)
    return translator.translate_batch(articles)


if __name__ == "__main__":
    # 测试代码
    print("Testing Translator Module...")
    
    # 使用模拟翻译器测试
    translator = create_translator(use_mock=True)
    
    result = translator.translate(
        title="OpenAI Releases GPT-4o: A New Multimodal Model",
        summary="OpenAI has announced the release of GPT-4o, a new multimodal model that can process text, audio, and images. The model is available to all ChatGPT users."
    )
    
    print(f"Original Title: {result.original_title}")
    print(f"Translated Title: {result.title}")
    print(f"Original Summary: {result.original_summary}")
    print(f"Translated Summary: {result.summary}")
    print(f"Success: {result.success}")
