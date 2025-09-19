import numpy as np
from typing import List, Tuple

def simple_power_law(x: np.ndarray, norm: float, alpha: float) -> np.ndarray:
    """
    一个简单的幂律函数模型：F(t) = norm * t^(-alpha)

    Args:
        x (np.ndarray): 自变量（通常是相对于T0的时间，单位：s）。
        norm (float): 归一化常数。
        alpha (float): 幂律衰减指数（通常为正值）。

    Returns:
        np.ndarray: 幂律模型在给定时间点x的函数值。
    """
    return norm * x**(-alpha)

def broken_power_law(
    x: np.ndarray, 
    norm: float, 
    t_break: float, 
    alpha1: float, 
    alpha2: float, 
    delta: float = 0.5
) -> np.ndarray:
    """
    一个平滑断裂幂律函数（Smoothly Broken Power Law, SBPL）。

    该模型用于描述具有一个断点的光变曲线。
    
    Args:
        x (np.ndarray): 自变量（通常是相对于T0的时间，单位：s）。
        norm (float): 归一化常数。
        t_break (float): 断点时间。
        alpha1 (float): 第一个衰减段的幂律指数（通常为正值）。
        alpha2 (float): 第二个衰减段的幂律指数（通常为正值）。
        delta (float, optional): 平滑参数。值越小，过渡越平滑。默认为0.5。

    Returns:
        np.ndarray: SBPL 模型在给定时间点x的函数值。
    """
    term = 1 + (x / t_break)**(1 / delta)
    result = norm * x**(-alpha1) * term**(-delta * (alpha2 - alpha1))
    return result

def multi_sbpl(
    x: np.ndarray, 
    norm: float, 
    breakpoints: List[float], 
    alphas: List[float], 
    deltas: List[float]
) -> np.ndarray:
    """
    多段平滑破幂律函数模型（Multi-segment Smoothly Broken Power Law）。

    该函数可以拟合具有任意数量断点的光变曲线。

    Args:
        x (np.ndarray): 自变量（通常是相对于T0的时间，单位：s）。
        norm (float): 归一化常数。
        breakpoints (List[float]): 断点时间列表，例如 [t_b1, t_b2, ...]。
        alphas (List[float]): 幂律指数列表，例如 [alpha1, alpha2, ...]。
                               列表长度应比 breakpoints 多 1。
        deltas (List[float]): 平滑参数列表，例如 [delta1, delta2, ...]。
                              列表长度应与 breakpoints 相同。

    Returns:
        np.ndarray: 多段 SBPL 模型在给定时间点x的函数值。
    """
    # 确保参数列表的长度匹配
    if len(alphas) != len(breakpoints) + 1:
        raise ValueError("alphas 列表的长度必须比 breakpoints 多 1。")
    if len(deltas) != len(breakpoints):
        raise ValueError("deltas 列表的长度必须与 breakpoints 相同。")
        
    # 初始幂律指数为 -alpha1
    result = norm * x**(-alphas[0])
    
    # 计算每个断点的平滑过渡
    for i in range(len(breakpoints)):
        term = 1 + (x / breakpoints[i])**(1 / deltas[i])
        # 指数差为 -(alpha_i+1) - (-alpha_i) = alpha_i - alpha_(i+1)
        result *= term**(-deltas[i] * (alphas[i+1] - alphas[i]))
        
    return result