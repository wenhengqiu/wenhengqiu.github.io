# Info-Getter Translator Module

Info-Getter 翻译模块 - 使用 OpenClaw 大模型 API 进行智能翻译

## 功能特性

- ✅ **集成 OpenClaw API** - 调用本地 Gateway 进行翻译
- ✅ **智能长度控制** - 标题限制20字内，摘要限制100字内
- ✅ **专有名词保护** - GPT、Tesla 等品牌名和术语不翻译
- ✅ **降级策略** - 翻译失败时自动保留原文
- ✅ **批量翻译** - 支持多篇文章同时翻译

## 快速开始

### 基本用法

```python
from translator import translate_article

# 翻译单篇文章
result = translate_article(
    title="OpenAI Releases GPT-4o: A New Multimodal Model",
    summary="OpenAI has announced the release of GPT-4o..."
)

print(result.title)    # 中文标题（20字内）
print(result.summary)  # 中文摘要（100字内）
```

### 批量翻译

```python
from translator import translate_articles

articles = [
    {"title": "Title 1", "summary": "Summary 1"},
    {"title": "Title 2", "summary": "Summary 2"},
]

results = translate_articles(articles)
for r in results:
    print(r.title, r.summary)
```

### 自定义配置

```python
from translator import create_translator

translator = create_translator(
    model="moonshot/kimi-k2.5",  # 指定模型
    max_title_length=15,          # 自定义标题长度
    max_summary_length=80,        # 自定义摘要长度
    protected_terms={"API", "SDK"}  # 添加自定义保护词
)

result = translator.translate(title="...", summary="...")
```

## 目录结构

```
translator/
├── __init__.py          # 包入口
├── core.py              # 核心翻译逻辑
├── test_translator.py   # 测试文件
├── examples.py          # 使用示例
└── README.md            # 本文档
```

## 专有名词保护

以下类型的专有名词会被自动保护（不翻译）：

- **AI/大模型**: GPT, LLM, OpenAI, Anthropic, Claude, Gemini, DeepMind, PyTorch, TensorFlow
- **自动驾驶**: Tesla, FSD, Waymo, NOA, ADAS, BEV
- **机器人**: Figure AI, Optimus, Boston Dynamics, Unitree
- **科技公司**: Apple, Google, Microsoft, Meta, NVIDIA
- **编程/技术**: API, SDK, Docker, Kubernetes, Python, React
- **人名**: Elon Musk, Sam Altman, Demis Hassabis
- **中文专有**: 卓驭科技, 成行平台, 大疆车载, 小鹏, 华为

## API 参考

### TranslationResult

翻译结果数据类：

```python
@dataclass
class TranslationResult:
    title: str           # 翻译后的标题
    summary: str         # 翻译后的摘要
    success: bool        # 是否成功
    error_message: str   # 错误信息（失败时）
    original_title: str  # 原标题
    original_summary: str  # 原摘要
```

### OpenClawTranslator

主要翻译类：

```python
translator = OpenClawTranslator(
    model="moonshot/kimi-k2.5",  # 模型名称
    max_title_length=20,          # 标题最大长度
    max_summary_length=100,       # 摘要最大长度
    protected_terms=set()         # 自定义保护词集合
)

# 翻译
result = translator.translate(title="...", summary="...")

# 批量翻译
results = translator.translate_batch([{"title": "..."}, ...])
```

## 环境要求

- Python 3.8+
- OpenClaw CLI 已安装并配置
- OpenClaw Gateway 正在运行

## 测试

```bash
# 运行测试
python translator/test_translator.py

# 运行示例
python translator/examples.py
```

## 与 Fetcher 集成

```python
from fetcher import fetch_articles
from translator import translate_articles

# 获取文章
articles = fetch_articles()

# 提取需要翻译的内容
to_translate = [
    {"title": a["title"], "summary": a["summary"]}
    for a in articles
]

# 翻译
results = translate_articles(to_translate)

# 合并结果
for article, result in zip(articles, results):
    article["title_cn"] = result.title
    article["summary_cn"] = result.summary
```

## 降级策略

当翻译失败时，模块会自动降级：

1. **网络错误** - 保留原文，标记失败
2. **API 超时** - 保留原文，标记失败
3. **模型错误** - 保留原文，标记失败

可通过 `fallback_to_original` 参数控制：

```python
# 失败时保留原文（默认）
result = translator.translate(title="...", fallback_to_original=True)

# 失败时返回错误
result = translator.translate(title="...", fallback_to_original=False)
```

## License

MIT License
