"""
pytest配置和公共fixtures
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 可以在这里添加公共的fixtures
# 例如：数据库连接、测试数据等

