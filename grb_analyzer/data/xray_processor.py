import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from astropy.io import fits
from astropy.time import Time
from datetime import datetime
import os

from .base_processor import BaseProcessor
from ..utils.time_converter import utc_to_mjd
from ..utils.flux_converter import magnitude_to_flux_density

class XrayProcessor(BaseProcessor):
    """
    一个用于处理 X 射线观测数据的处理器。
    它继承自 BaseProcessor，并实现将 FITS 数据转换为格式化光变曲线。
    """

    def _compute_integral_energy(self, beta: float, e1: float, e2: float) -> float:
        """计算幂律能谱在给定能量范围内的积分。"""
        if beta == 1:
            return np.log(e2 / e1)
        else:
            return (e2**(1 - beta) - e1**(1 - beta)) / (1 - beta)

    def _compute_energy_flux_density_and_error(
        self, 
        flux: float, 
        sigma_flux: float, 
        beta: float, 
        sigma_beta: float, 
        e1: float, 
        e2: float, 
        e_obs: float
    ) -> Tuple[float, float]:
        """
        计算给定能量处的流量密度及其误差。
        
        Args:
            flux (float): 积分流量 (erg/cm²/s)。
            sigma_flux (float): 积分流量误差。
            beta (float): 能量谱指数。
            sigma_beta (float): 能量谱指数误差。
            e1 (float): 积分下限能量 (keV)。
            e2 (float): 积分上限能量 (keV)。
            e_obs (float): 观测能量 (keV)。

        Returns:
            Tuple[float, float]: 流量密度 (erg/cm²/s/keV) 及其误差。
        """
        integral = self._compute_integral_energy(beta, e1, e2)
        e_term = e_obs ** (-beta)
        f_e = flux / integral * e_term
        df_dF = e_term / integral
        df_dbeta = -np.log(e_obs) * flux / integral * e_term
        sigma_f_e = np.sqrt((df_dF * sigma_flux)**2 + (df_dbeta * sigma_beta)**2)
        return f_e, sigma_f_e

    def process(
        self,
        fits_file: str,
        t0: datetime,
        output_dir: str,
        flux_conversion_factor: Optional[float] = None,
        is_count_rate_data: bool = True,
        density_conversion_params: Optional[dict] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        处理 X 射线 FITS 文件，并生成流量和/或流量密度光变曲线。

        Args:
            fits_file (str): 包含 X 射线数据的 .fits 文件路径。
            t0 (datetime): GRB 爆发时间 (T0)。
            output_dir (str): 保存处理后文件的目录路径。
            flux_conversion_factor (Optional[float]): 从 count rate 转换到 flux 的因子。
            is_count_rate_data (bool): 输入数据是否为计数率。如果为 False，则假定为 flux。
            density_conversion_params (Optional[dict]): 
                从 flux 转换到 flux density 所需的参数。
                必须包含 'photon_index' 和可选的 'sigma_photon_index'。
                也可兼容旧的 'beta_X' 和 'sigma_beta_X'。

        Returns:
            Dict[str, pd.DataFrame]: 包含处理后数据的字典，键为 'xray_flux' 和/或 'xray_flux_density'。
        """
        print(f"[{self.__class__.__name__}] 开始处理X射线数据: {fits_file}")

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Step 1: 读取 FITS 数据和头部
        try:
            with fits.open(fits_file) as hdul:
                data = hdul[1].data
                header = hdul[1].header
                time = data['TIME']
                time_err = data['TIME_ERR']
                rate = data['RATE']
                rate_err = data['ERROR']
                mjd_obs = header.get('MJD-OBS')
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到指定的 FITS 文件: {fits_file}")

        if mjd_obs is None:
            raise ValueError("FITS header 中缺少 'MJD-OBS' 关键字")

        # Step 2: 时间转换 (相对于 T0)
        t0_mjd = utc_to_mjd(t0)
        delta_seconds = (mjd_obs - t0_mjd) * 86400.0
        time_from_t0 = delta_seconds + time

        # Step 3: 计算流量（Flux）
        if is_count_rate_data:
            if flux_conversion_factor is None:
                raise ValueError("若输入为计数率，必须提供 flux_conversion_factor。")
            flux = rate * flux_conversion_factor
            flux_err = rate_err * flux_conversion_factor
            flux_name = "XRT_flux"
        else:
            flux = rate
            flux_err = rate_err
            flux_name = "XRT_flux_user"
        
        # Step 4: 保存流量光变曲线
        df_flux = pd.DataFrame({
            'time_from_t0_s': time_from_t0,
            'time_err_s': time_err,
            'flux_erg_cm2_s': flux,
            'flux_err_erg_cm2_s': flux_err,
        })
        output_flux_path = os.path.join(output_dir, f"{flux_name}.csv")
        df_flux.to_csv(output_flux_path, index=False)
        print(f"[{self.__class__.__name__}] 已保存流量光变曲线至: {output_flux_path}")
        
        processed_data = {flux_name: df_flux}

        # Step 5: 计算流量密度（Flux Density）
        if density_conversion_params:
            # 新增逻辑：优先使用 photon_index，如果不存在则退回 beta_X
            if 'photon_index' in density_conversion_params:
                photon_index = density_conversion_params['photon_index']
                sigma_photon_index = density_conversion_params.get('sigma_photon_index', 0.0)
                beta = photon_index - 1.0
                sigma_beta = sigma_photon_index
            elif 'beta_X' in density_conversion_params:
                print("警告: 正在使用已弃用的参数 'beta_X'。请考虑改用 'photon_index'。")
                beta = density_conversion_params['beta_X']
                sigma_beta = density_conversion_params.get('sigma_beta_X', 0.0)
            else:
                raise ValueError("未提供有效的谱指数参数。请在 density_conversion_params 中提供 'photon_index' 或 'beta_X'。")
            
            e1 = density_conversion_params.get('E1', 0.3)
            e2 = density_conversion_params.get('E2', 10.0)
            e_obs = density_conversion_params.get('E_obs', 1.0)
            
            # 使用列表推导式进行高效计算
            flux_density_list = []
            flux_density_err_list = []
            for i in range(len(flux)):
                f_e, f_e_err = self._compute_energy_flux_density_and_error(
                    flux[i], flux_err[i], beta, sigma_beta, e1, e2, e_obs
                )
                flux_density_list.append(f_e)
                flux_density_err_list.append(f_e_err)
            
            flux_density_erg_cm2_s_keV = np.array(flux_density_list)
            flux_density_err_erg_cm2_s_keV = np.array(flux_density_err_list)

            # 转换为 mJy
            conversion_factor = 1e26 / 241797944177033445
            flux_density_mjy = flux_density_erg_cm2_s_keV * conversion_factor
            flux_density_err_mjy = flux_density_err_erg_cm2_s_keV * conversion_factor
            
            df_density = pd.DataFrame({
                'time_from_t0_s': time_from_t0,
                'time_err_s': time_err,
                'flux_density_mJy': flux_density_mjy,
                'flux_density_err_mJy': flux_density_err_mjy,
            })
            
            output_density_path = os.path.join(output_dir, f"{flux_name.replace('flux', 'flux_density')}.csv")
            df_density.to_csv(output_density_path, index=False)
            print(f"[{self.__class__.__name__}] 已保存流量密度光变曲线至: {output_density_path}")
            processed_data["xray_flux_density"] = df_density

        print(f"[{self.__class__.__name__}] X射线数据处理完成。")
        return processed_data