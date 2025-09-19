import pandas as pd
import numpy as np
from typing import Union, Tuple
from extinction import fm07 # 确保已安装 python-extinction 包

def magnitude_to_flux_density(
    mag_ab: Union[float, pd.Series],
    mag_err: Union[float, pd.Series],
    lambda_eff_angstrom: Union[float, pd.Series],
    a_v: float
) -> Tuple[Union[float, pd.Series], Union[float, pd.Series]]:
    """
    将 AB 星等及其误差转换为流量密度（mJy），并考虑星际消光。

    该函数使用 Fitzpatrick (2007) 的模型计算星际消光，然后将去消光后的
    星等转换为流量密度。支持单个数值或 Pandas Series 的批量转换。

    Args:
        mag_ab (Union[float, pd.Series]): AB 星等或包含 AB 星等的 Series。
        mag_err (Union[float, pd.Series]): 星等误差或包含误差的 Series。
        lambda_eff_angstrom (Union[float, pd.Series]): 滤光片的有效波长（单位：埃）。
                                                        可以是一个数值或一个 Series。
        a_v (float): V 波段的总消光量，用于计算星际消光。

    Returns:
        Tuple[Union[float, pd.Series], Union[float, pd.Series]]: 
            转换后的流量密度和其误差（单位：mJy）。
    """
    
    # 流量密度与 AB 星等转换的零点常量 (AB = 0 对应 3631 Jy)
    CONSTANT_JY = 3631.0
    
    # 1. 计算给定有效波长下的星际消光 A_lambda
    # fm07 函数的输入波长单位为埃 (Angstrom)
    a_lambda = fm07(np.array(lambda_eff_angstrom), a_v)
    
    # 将 AB 星等去消光：m_lambda_corrected = m_lambda - A_lambda
    mag_corrected = mag_ab - a_lambda
    
    # 2. 将去消光后的星等转换为流量密度 (单位: Jy)
    # 公式：F_nu = F_nu,0 * 10^(-mag/2.5)
    flux_density_jy = CONSTANT_JY * 10 ** (-mag_corrected / 2.5)
    
    # 3. 将单位从 Jy 转换为 mJy (毫焦耳)
    flux_density_mjy = flux_density_jy * 1000
    
    # 4. 流量密度误差计算
    # 公式：delta_F_nu = F_nu * (ln(10)/2.5) * delta_mag
    # 这里的 F_nu 必须是 Jy 单位，因为误差是基于其物理量计算的
    ln10_div_2p5 = np.log(10) / 2.5
    flux_density_err_jy = flux_density_jy * ln10_div_2p5 * mag_err
    
    # 将误差也转换为 mJy
    flux_density_err_mjy = flux_density_err_jy * 1000
    
    return flux_density_mjy, flux_density_err_mjy