# Info-Getter - 全自动信息聚合系统

## 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 配置环境变量
```bash
export OPENCLAW_API_KEY="your_key"
export GITHUB_TOKEN="your_token"
```

### 运行一次
```bash
python -m info_getter --once
```

### 持续运行
```bash
python -m info_getter
```

## 项目结构

```
info_getter/
├── __init__.py
├── __main__.py
├── scheduler.py      # 调度器
├── fetcher/          # 采集模块
│   ├── __init__.py
│   └── core.py
├── translator/       # 翻译模块
│   ├── __init__.py
│   └── core.py
└── publisher/        # 发布模块
    ├── __init__.py
    └── core.py
```
