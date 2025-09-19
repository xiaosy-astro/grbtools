import datetime
from typing import Union, Dict, Optional
import pandas as pd


# 从 data 模块导入
from ..data.optical_processor import OpticalProcessor
from ..data.xray_processor import XrayProcessor


class GRBEvent:
    """
    一个核心类，用于表示和管理单个伽马射线暴（GRB）事件的所有相关信息。

    这个类是用户与 grb-analyzer 包交互的主要入口点。它封装了GRB的基础物理
    属性，并提供方法来调用数据处理模块，将处理后的光变曲线数据存储在
    一个统一的容器中。
    """

    def __init__(self, 
                 name: str, 
                 t0: Union[str, datetime.datetime], 
                 z: Optional[float] = None, 
                 distance_cm: Optional[float] = None):
        """
        初始化一个 GRBEvent 对象。

        Args:
            name (str): GRB的名称，例如 'GRB250419A'。
            t0 (Union[str, datetime.datetime]): 暴发的触发时间 (T0)。
                可以是符合ISO 8601格式的字符串 (e.g., "2025-04-19T12:30:00")
                或是一个 Python 的 datetime 对象。
            z (Optional[float], optional): 红移 (redshift)。默认为 None。
            distance_cm (Optional[float], optional): 光度距离 (单位: cm)。默认为 None。
        """
        self.name = name
        self.z = z
        self.distance_cm = distance_cm

        # 内部统一将 t0 存储为 datetime 对象，方便后续计算
        if isinstance(t0, str):
            # 使用 fromisoformat 可以解析大部分标准时间字符串
            self.t0 = datetime.datetime.fromisoformat(t0)
        elif isinstance(t0, datetime.datetime):
            self.t0 = t0
        else:
            raise TypeError("t0 必须是时间字符串或 datetime 对象。")

        # --- 数据容器 ---
        # 使用一个嵌套字典来存储不同波段、不同仪器或处理阶段的光变曲线。
        # 结构示例:
        # self.lightcurves = {
        #     'optical': {
        #         'VT_B': pd.DataFrame(...),
        #         'LCO_V': pd.DataFrame(...)
        #     },
        #     'xray': {
        #         'XRT_flux': pd.DataFrame(...),
        #         'XRT_flux_density': pd.DataFrame(...)
        #     }
        # }
        self.lightcurves: Dict[str, Dict[str, pd.DataFrame]] = {}
        
        print(f"GRBEvent '{self.name}' (T0: {self.t0.isoformat()}) 已创建。")

    def __repr__(self) -> str:
        """为开发者提供清晰的对象表示。"""
        return f"GRBEvent(name='{self.name}', t0='{self.t0.isoformat()}', z={self.z})"

    def process_optical_data(self, input_file: str, output_dir: str):
        """
        调用光学数据处理器来处理原始光学数据文件。

        处理流程包括：时间转换、星等转流量密度、排序和保存。
        处理完成后的数据（以DataFrame格式）会自动加载到本对象的 `lightcurves` 容器中。

        Args:
            input_file (str): 包含光学观测数据的 .csv 文件路径。
            output_dir (str): 保存处理后文件的目录路径。
        """
        print(f"[{self.name}] 开始处理光学数据: {input_file}")
        
        # 1. 实例化一个光学处理器
        processor = OpticalProcessor()
        
        # 2. 调用其 process 方法，传入T0时间等必要信息
        #    我们设计 process 方法返回一个字典，键是 "望远镜_滤波片"，值是处理后的DataFrame
        processed_data_dict = processor.process(
            input_file=input_file,
            t0=self.t0,
            output_dir=output_dir
        )
        
        # 3. 将返回的数据存储到对象的容器中
        if 'optical' not in self.lightcurves:
            self.lightcurves['optical'] = {}
        
        self.lightcurves['optical'].update(processed_data_dict)
        
        loaded_keys = list(processed_data_dict.keys())
        print(f"[{self.name}] 光学数据处理完成。已加载 {len(loaded_keys)} 条光变曲线: {loaded_keys}")

    def process_xray_data(self, 
                          fits_file: str, 
                          output_dir: str,
                          flux_conversion_factor: float,
                          density_conversion_params: Optional[dict] = None):
        """
        调用X射线数据处理器来处理原始 .fits 文件。

        Args:
            fits_file (str): 包含X射线光变曲线的 .fits 文件路径。
            output_dir (str): 保存处理后文件的目录路径。
            flux_conversion_factor (float): 从 count rate 转换到 flux 的因子。
            density_conversion_params (Optional[dict], optional): 
                从 flux 转换到 flux density 所需的参数。默认为 None。
        """
        print(f"[{self.name}] 开始处理X射线数据: {fits_file}")
        
        # 1. 实例化一个X射线处理器
        processor = XrayProcessor()
        
        # 2. 调用其处理方法
        #    我们设计它返回一个包含 'flux' 和 'flux_density' 键的字典
        processed_data_dict = processor.process(
            fits_file=fits_file,
            t0=self.t0,
            output_dir=output_dir,
            flux_conversion_factor=flux_conversion_factor,
            density_conversion_params=density_conversion_params
        )
        
        # 3. 存储数据
        if 'xray' not in self.lightcurves:
            self.lightcurves['xray'] = {}
            
        self.lightcurves['xray'].update(processed_data_dict)
        
        loaded_keys = list(processed_data_dict.keys())
        print(f"[{self.name}] X射线数据处理完成。已加载光变曲线: {loaded_keys}")
        
    def get_lightcurve(self, band: str, name: str) -> Optional[pd.DataFrame]:
        """
        一个方便的辅助方法，用于从数据容器中按名称获取光变曲线。

        Args:
            band (str): 波段名称，如 'optical', 'xray'。
            name (str): 光变曲线的具体名称，如 'VT_B', 'XRT_flux_density'。

        Returns:
            Optional[pd.DataFrame]: 如果找到，则返回光变曲线的DataFrame；否则返回None。
        """
        return self.lightcurves.get(band, {}).get(name)
