import pytest
from astropy.io import fits
import numpy as np
from datetime import datetime
import os
import shutil
from grb_analyzer.data import XrayProcessor

@pytest.fixture(scope="module")
def setup_teardown_xray():
    """在测试前创建测试目录和模拟 FITS 文件，并在测试后清理。"""
    test_dir = "test_output_xray"
    os.makedirs(test_dir, exist_ok=True)
    
    # 创建一个模拟的 FITS 文件
    col_time = fits.Column(name='TIME', format='D', array=np.array([100, 200, 300]))
    col_time_err = fits.Column(name='TIME_ERR', format='D', array=np.array([10, 10, 10]))
    col_rate = fits.Column(name='RATE', format='D', array=np.array([0.5, 0.3, 0.1]))
    col_err = fits.Column(name='ERROR', format='D', array=np.array([0.05, 0.03, 0.01]))
    
    cols = fits.ColDefs([col_time, col_time_err, col_rate, col_err])
    hdu = fits.BinTableHDU.from_columns(cols)
    
    # 在头部中添加 MJD-OBS 关键词
    hdu.header['MJD-OBS'] = 60000.0  # 模拟观测开始的 MJD
    
    hdul = fits.HDUList([fits.PrimaryHDU(), hdu])
    input_file = os.path.join(test_dir, "mock_xray.fits")
    hdul.writeto(input_file, overwrite=True)
    
    yield input_file, test_dir
    
    shutil.rmtree(test_dir)

def test_xray_processor_success(setup_teardown_xray):
    """测试 XrayProcessor 的成功处理流程。"""
    input_file, output_dir = setup_teardown_xray
    t0 = datetime(2025, 4, 19, 5, 0, 0) # 假设对应的 MJD 为 60000.0
    
    processor = XrayProcessor()
    
    # 测试 count rate 到 flux 的转换
    result = processor.process(
        fits_file=input_file,
        t0=t0,
        output_dir=output_dir,
        flux_conversion_factor=1e-10,
        density_conversion_params={'photon_index': 2.0}
    )
    
    # 1. 验证返回值类型和内容
    assert isinstance(result, dict)
    assert 'XRT_flux' in result
    assert 'xray_flux_density' in result
    
    # 2. 验证输出文件是否存在
    assert os.path.exists(os.path.join(output_dir, "XRT_flux.csv"))
    assert os.path.exists(os.path.join(output_dir, "XRT_flux_density.csv"))

def test_xray_processor_missing_header(setup_teardown_xray):
    """测试当 FITS 头部缺少 MJD-OBS 时是否抛出 ValueError。"""
    input_file, output_dir = setup_teardown_xray
    t0 = datetime(2025, 4, 19, 5, 0, 0)
    
    # 移除关键的 MJD-OBS 头部
    with fits.open(input_file, mode='update') as hdul:
        del hdul[1].header['MJD-OBS']
        hdul.flush()

    processor = XrayProcessor()
    with pytest.raises(ValueError, match="FITS header 中缺少 'MJD-OBS' 关键字"):
        processor.process(
            fits_file=input_file,
            t0=t0,
            output_dir=output_dir,
            flux_conversion_factor=1e-10
        )

def test_xray_processor_file_not_found():
    """测试当 FITS 文件不存在时是否抛出 FileNotFoundError。"""
    processor = XrayProcessor()
    t0 = datetime(2025, 4, 19, 5, 0, 0)
    with pytest.raises(FileNotFoundError):
        processor.process(
            fits_file="non_existent_file.fits",
            t0=t0,
            output_dir="test_output",
            flux_conversion_factor=1e-10
        )