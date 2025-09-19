from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict
import datetime

class BaseProcessor(ABC):
    """
    数据处理器的抽象基类。

    所有具体的数据处理器（如光学、X射线处理器）都必须继承此基类，
    并实现其抽象方法。这确保了处理器的接口统一。
    """
    
    @abstractmethod
    def process(
        self,
        input_file: str,
        t0: datetime.datetime,
        output_dir: str,
        **kwargs
    ) -> Dict[str, pd.DataFrame]:
        """
        处理原始数据文件的抽象方法。

        Args:
            input_file (str): 输入数据文件的路径。
            t0 (datetime.datetime): GRB 触发时间。
            output_dir (str): 处理后数据文件的保存目录。
            **kwargs: 可选参数，用于不同处理器的特定需求。

        Returns:
            Dict[str, pd.DataFrame]: 包含处理后数据的字典，
                                     键通常为处理类型或波段，值为 DataFrame。
        """
        pass