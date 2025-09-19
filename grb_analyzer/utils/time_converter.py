from astropy.time import Time
from datetime import datetime
from typing import Union

def utc_to_mjd(utc_time: datetime) -> float:
    """
    将 UTC 时间 (datetime 对象) 转换为修正儒略日 (MJD)。

    Args:
        utc_time (datetime): 待转换的 UTC 时间。

    Returns:
        float: 转换后的 MJD 值。
    """
    # 使用 astropy.time.Time 实例化一个时间对象，并指定格式为 'datetime'
    t = Time(utc_time, format='datetime', scale='utc')
    return t.mjd

def mjd_to_utc(mjd: Union[float, str]) -> datetime:
    """
    将修正儒略日 (MJD) 转换为 UTC 时间 (datetime 对象)。

    Args:
        mjd (Union[float, str]): 待转换的 MJD 值。

    Returns:
        datetime: 转换后的 UTC 时间。
    """
    # 使用 astropy.time.Time 实例化一个时间对象，并指定格式为 'mjd'
    t = Time(mjd, format='mjd', scale='utc')
    # 使用 to_datetime 方法转换为 Python datetime 对象
    return t.to_datetime()

def utc_to_tjd(utc_time: datetime) -> float:
    """
    将 UTC 时间 (datetime 对象) 转换为截断儒略日 (TJD)。

    TJD = JD - 2440000.5
    TJD = MJD - 40000.0

    Args:
        utc_time (datetime): 待转换的 UTC 时间。

    Returns:
        float: 转换后的 TJD 值。
    """
    mjd_time = utc_to_mjd(utc_time)
    return mjd_time - 40000.0

def tjd_to_utc(tjd: Union[float, str]) -> datetime:
    """
    将截断儒略日 (TJD) 转换为 UTC 时间 (datetime 对象)。

    Args:
        tjd (Union[float, str]): 待转换的 TJD 值。

    Returns:
        datetime: 转换后的 UTC 时间。
    """
    mjd_time = float(tjd) + 40000.0
    return mjd_to_utc(mjd_time)