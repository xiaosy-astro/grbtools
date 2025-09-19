import pandas as pd
from typing import Dict
from datetime import datetime
import os

from ..utils.flux_converter import magnitude_to_flux_density
from .base_processor import BaseProcessor

class OpticalProcessor(BaseProcessor):
    """
    一个用于处理光学观测数据的处理器。
    它继承自 BaseProcessor，并实现 process 方法。
    """
    def process(
        self,
        input_file: str,
        t0: datetime,
        output_dir: str,
        a_v: float
    ) -> Dict[str, pd.DataFrame]:
        """
        处理光学原始数据文件，包括时间转换、星等去消光和转换为流量密度。

        Args:
            input_file (str): 输入数据文件的路径。
            t0 (datetime.datetime): GRB 触发时间。
            output_dir (str): 处理后数据文件的保存目录。
            a_v (float): V 波段的总消光量，用于星际消光计算。

        Returns:
            Dict[str, pd.DataFrame]: 包含处理后数据的字典，键为 'optical_data'，
                                     值为包含去消光星等和流量密度的新 DataFrame。
        """
        print(f"正在处理光学数据文件: {input_file}...")

        try:
            df = pd.read_csv(input_file)
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到指定的光学数据文件: {input_file}")

        required_columns = ['time', 'exposure_s', 'mag_ab', 'mag_err', 'telescope', 'filter', 'lambda_eff_angstrom']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(
                f"输入文件缺少必需的列。必需列为: {required_columns}"
            )
        
        # 1. 确保时间列为 datetime 对象
        df['time'] = pd.to_datetime(df['time'])

        # 2. 计算相对于 t0 的时间差（秒），并加上曝光时间的一半
        df['t_minus_t0'] = (df['time'] - t0).dt.total_seconds() + df['exposure_s'] / 2

        # 3. 使用 flux_converter 将星等转换为流量密度 (mJy)
        df['flux_density_mjy'], df['flux_density_err_mjy'] = magnitude_to_flux_density(
            mag_ab=df['mag_ab'],
            mag_err=df['mag_err'],
            lambda_eff_angstrom=df['lambda_eff_angstrom'],
            a_v=a_v
        )
        
        # 4. 按时间对数据进行排序
        df_sorted = df.sort_values(by='t_minus_t0').reset_index(drop=True)

        # 5. 定义保存路径并保存处理后的数据
        output_filepath = os.path.join(output_dir, os.path.basename(input_file).replace('.csv', '_processed.csv'))
        df_sorted.to_csv(output_filepath, index=False)
        print(f"处理完成。文件已保存至: {output_filepath}")

        return {'optical_data': df_sorted}