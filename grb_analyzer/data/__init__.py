"""
grb_analyzer.data 包初始化文件。

该文件用于将数据处理相关的核心类暴露到包的顶层，
方便用户直接导入和使用。
"""

from .base_processor import BaseProcessor
from .optical_processor import OpticalProcessor
from .xray_processor import XrayProcessor

# 定义 __all__ 列表以明确包的公共 API
__all__ = [
    "BaseProcessor",
    "OpticalProcessor",
    "XrayProcessor"
]