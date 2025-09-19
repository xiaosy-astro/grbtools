import pandas as pd
from datetime import datetime
from typing import Optional, Dict, List
import os

# 从我们创建的包中导入所有必要的类
from ..data import OpticalProcessor, XrayProcessor
from ..analysis import Fitter
from ..analysis.models import multi_sbpl, broken_power_law, simple_power_law
from bilby.core.prior import Prior, Uniform
import bilby

class GRBEvent:
    """
    代表一个 GRB 爆发事件的类。
    
    这个类管理与特定 GRB 事件相关的所有数据处理、光变曲线存储和拟合分析。
    """
    def __init__(self, event_id: str, t0: datetime):
        """
        初始化一个 GRBEvent 实例。

        Args:
            event_id (str): GRB 爆发的唯一标识符（例如，GRB250419A）。
            t0 (datetime): GRB 爆发的精确时间（T0）。
        """
        self.event_id = event_id
        self.t0 = t0
        # 存储所有处理后的光变曲线
        self.lightcurves: Dict[str, pd.DataFrame] = {}
        # 存储所有拟合结果
        self.fit_results: Dict[str, bilby.core.result.Result] = {}
        self.output_dir = f"output/{self.event_id}"
        
        # 确保输出目录存在
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
    def process_data(self, data_file: str, processor_type: str, **kwargs):
        """
        处理 GRB 观测数据。
        
        Args:
            data_file (str): 原始数据文件的路径。
            processor_type (str): 'optical' 或 'xray'。
            **kwargs: 传递给特定处理器（如 A_V 或 flux_conversion_factor）的参数。
        """
        print(f"开始处理 {self.event_id} 的 {processor_type} 数据...")
        
        processor = None
        if processor_type.lower() == 'optical':
            processor = OpticalProcessor()
        elif processor_type.lower() == 'xray':
            processor = XrayProcessor()
        else:
            raise ValueError("processor_type 必须是 'optical' 或 'xray'。")

        # 调用处理器的 process 方法并将结果存储
        processed_data = processor.process(
            input_file=data_file,
            t0=self.t0,
            output_dir=self.output_dir,
            **kwargs
        )
        self.lightcurves.update(processed_data)
        print(f"{processor_type} 数据处理完成。")
        
    def fit_lightcurve(
        self,
        lc_key: str,
        model_function: callable,
        priors: Dict[str, Prior],
        label: str,
        **sampler_kwargs
    ):
        """
        使用指定的模型拟合存储的光变曲线。
        
        Args:
            lc_key (str): 要拟合的光变曲线的键名（例如 'optical_data' 或 'XRT_flux_density'）。
            model_function (callable): 要使用的模型函数（来自 analysis.models）。
            priors (Dict[str, Prior]): Bilby 的先验分布字典。
            label (str): 拟合结果的标签。
            **sampler_kwargs: 传递给 bilby.run_sampler 的其他参数。
        """
        if lc_key not in self.lightcurves:
            raise ValueError(f"'{lc_key}' 键未在 lightcurves 字典中找到。请先处理数据。")
        
        print(f"开始拟合 {self.event_id} 的 '{lc_key}' 光变曲线...")
        
        data_to_fit = self.lightcurves[lc_key]
        fitter = Fitter(data=data_to_fit, model_function=model_function)
        
        result = fitter.run_fit(
            priors=priors,
            label=f"{self.event_id}_{label}",
            outdir=self.output_dir,
            **sampler_kwargs
        )
        
        self.fit_results[label] = result
        print(f"拟合完成。结果已存储在 fit_results['{label}'] 中。")

