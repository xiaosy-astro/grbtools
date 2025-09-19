"""
grb_analyzer.analysis 包初始化文件。

该文件用于将模型函数和拟合工具类暴露到包的顶层，
方便用户直接导入和使用。
"""

from .models import simple_power_law, broken_power_law, multi_sbpl
from .fitting import Fitter

# 定义 __all__ 列表以明确包的公共 API
__all__ = [
    "simple_power_law",
    "broken_power_law",
    "multi_sbpl",
    "Fitter"
]