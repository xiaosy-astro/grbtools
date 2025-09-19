import pytest
import pandas as pd
from datetime import datetime
import os
import shutil
from grb_analyzer.data import OpticalProcessor

@pytest.fixture(scope="module")
def setup_teardown():
    """在测试前创建测试目录和模拟数据，并在测试后清理。"""
    # 创建一个临时目录用于测试
    test_dir = "test_output_optical"
    os.makedirs(test_dir, exist_ok=True)
    
    # 创建一个模拟的光学数据文件
    data = {
        'time': [
            "2025-04-19T05:01:00",
            "2025-04-19T05:02:00",
            "2025-04-19T05:03:00"
        ],
        'exposure_s': [60, 60, 60],
        'mag_ab': [20.5, 21.0, 21.5],
        'mag_err': [0.1, 0.15, 0.2],
        'telescope': ['T1', 'T2', 'T1'],
        'filter': ['R', 'R', 'R'],
        'lambda_eff_angstrom': [6500, 6500, 6500]
    }
    df = pd.DataFrame(data)
    input_file = os.path.join(test_dir, "mock_optical.csv")
    df.to_csv(input_file, index=False)
    
    # 将所需的文件路径传递给测试
    yield input_file, test_dir
    
    # 清理：移除测试目录及其内容
    shutil.rmtree(test_dir)

def test_optical_processor_success(setup_teardown):
    """测试 OpticalProcessor 的成功处理流程。"""
    input_file, output_dir = setup_teardown
    t0 = datetime(2025, 4, 19, 5, 0, 0)
    a_v = 0.08
    
    processor = OpticalProcessor()
    result = processor.process(input_file, t0, output_dir, a_v)
    
    # 1. 验证返回值类型
    assert isinstance(result, dict)
    assert 'optical_data' in result
    
    # 2. 验证 DataFrame 的内容和列名
    df = result['optical_data']
    assert isinstance(df, pd.DataFrame)
    assert 't_minus_t0' in df.columns
    assert 'flux_density_mjy' in df.columns
    assert 'flux_density_err_mjy' in df.columns
    assert len(df) == 3 # 验证行数
    
    # 3. 验证时间转换是否正确
    assert df['t_minus_t0'].iloc[0] == 60 + 30 # 60s from t0, plus half exposure
    
    # 4. 验证输出文件是否存在
    output_file = os.path.join(output_dir, "mock_optical_processed.csv")
    assert os.path.exists(output_file)

def test_optical_processor_missing_column():
    """测试当输入文件缺少必需列时是否抛出 ValueError。"""
    data = {
        'time': ["2025-04-19T05:01:00"], 
        'exposure_s': [60],
        'mag_ab': [20.5] # 缺少 mag_err, lambda_eff_angstrom 等
    }
    df = pd.DataFrame(data)
    test_dir = "test_output_optical_missing_col"
    os.makedirs(test_dir, exist_ok=True)
    input_file = os.path.join(test_dir, "missing_col.csv")
    df.to_csv(input_file, index=False)
    
    processor = OpticalProcessor()
    t0 = datetime(2025, 4, 19, 5, 0, 0)
    with pytest.raises(ValueError, match="输入文件缺少必需的列"):
        processor.process(input_file, t0, test_dir, 0.08)
        
    shutil.rmtree(test_dir)

def test_optical_processor_file_not_found():
    """测试当输入文件不存在时是否抛出 FileNotFoundError。"""
    processor = OpticalProcessor()
    t0 = datetime(2025, 4, 19, 5, 0, 0)
    with pytest.raises(FileNotFoundError):
        processor.process("non_existent_file.csv", t0, "test_output", 0.08)