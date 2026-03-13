#!/usr/bin/env python3
"""
Info-Getter 入口脚本
"""

import sys
import asyncio
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from scheduler import main

if __name__ == "__main__":
    asyncio.run(main())
