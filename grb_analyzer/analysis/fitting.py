import numpy as np
import pandas as pd
import bilby
from bilby.core.utils.random import rng, seed
from typing import Callable, Dict, List, Tuple
import os

class GenericGaussianLikelihood(bilby.Likelihood):
    """
    一个通用的高斯似然函数，用于拟合任何模型。

    该类动态地从参数字典中获取模型所需的参数，而不是硬编码。
    """
    def __init__(self, x: np.ndarray, y: np.ndarray, yerr: np.ndarray, model_function: Callable):
        """
        初始化似然函数。

        Args:
            x (np.ndarray): 自变量数据。
            y (np.ndarray): 观测数据。
            yerr (np.ndarray): 观测数据误差。
            model_function (Callable): 要拟合的数学模型函数。
        """
        super().__init__(parameters=dict())
        self.x = x
        self.y = y
        self.yerr = yerr
        self.model_function = model_function

    def log_likelihood(self) -> float:
        """
        计算模型的对数似然值。
        """
        # 从参数字典中提取模型参数和系统误差参数
        model_params = {k: v for k, v in self.parameters.items() if k not in ['log_f']}
        log_f = self.parameters.get("log_f", -10.0) # 如果没有提供，默认一个极小值

        # 使用解包操作将参数传递给模型函数
        model = self.model_function(self.x, **model_params)

        res = self.y - model
        sigma2 = self.yerr**2 + model**2 * np.exp(2 * log_f)
        
        loglike = -0.5 * np.sum(res**2 / sigma2 + np.log(2 * np.pi * sigma2))
        return loglike


class Fitter:
    """
    GRB 光变曲线的拟合工具类。

    该类封装了使用 bilby 库进行贝叶斯参数估计的整个工作流程。
    """
    def __init__(self, data: pd.DataFrame, model_function: Callable):
        """
        初始化拟合工具。

        Args:
            data (pd.DataFrame): 包含时间、流量和误差的 DataFrame。
            model_function (Callable): 要拟合的模型函数。
        """
        self.x = data['time_from_t0_s'].values
        self.y = data['flux_density_mjy'].values
        self.yerr = data['flux_density_err_mjy'].values
        self.model_function = model_function
        
    def run_fit(
        self,
        priors: Dict[str, bilby.core.prior.Prior],
        label: str,
        outdir: str = 'outdir',
        sampler: str = 'pymultinest',
        **sampler_kwargs
    ) -> bilby.core.result.Result:
        """
        执行贝叶斯拟合。

        Args:
            priors (Dict[str, bilby.core.prior.Prior]): 包含所有模型参数先验分布的字典。
            label (str): 拟合结果的标签，用于文件名和图表标题。
            outdir (str, optional): 保存结果的目录。默认为 'outdir'。
            sampler (str, optional): 要使用的采样器。默认为 'pymultinest'。
            **sampler_kwargs: 传递给 bilby.run_sampler 的其他参数。

        Returns:
            bilby.core.result.Result: 拟合结果对象。
        """
        # 设置 bilby 随机数种子以确保可重现性
        seed(1234)

        # 确保输出目录存在
        if not os.path.exists(outdir):
            os.makedirs(outdir)

        # 实例化似然函数
        likelihood = GenericGaussianLikelihood(
            self.x, self.y, self.yerr, self.model_function
        )

        # 运行 bilby 采样器
        print(f"[{self.__class__.__name__}] 开始运行 {sampler} 采样器...")
        result = bilby.run_sampler(
            likelihood=likelihood,
            priors=priors,
            outdir=outdir,
            label=label,
            sampler=sampler,
            **sampler_kwargs
        )
        print(f"[{self.__class__.__name__}] 采样完成。结果已保存到 {result.outdir}。")
        
        # 保存结果图表
        result.plot_corner(
            save=True, 
            filename=os.path.join(outdir, f'{label}_corner.pdf'),
            show_titles=True,
            quantiles=[0.16, 0.5, 0.84],
            labels=[priors[key].latex_label for key in result.parameter_labels]
        )
        
        return result