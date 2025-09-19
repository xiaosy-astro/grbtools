# grbtools

## 项目架构

```
grb-analyzer/
│
├── grb_analyzer/               # 核心源代码包
│   │
│   ├── __init__.py             # 包初始化文件
│   │
│   ├── core/                   # 核心对象定义
│   │   ├── __init__.py
│   │   └── grb_event.py        # 定义一个GRBEvent类，作为所有数据的容器
│   │
│   ├── data/                   # 数据处理模块（对应您的第一步）
│   │   ├── __init__.py
│   │   ├── base_processor.py   # 定义数据处理器的基类（抽象类）
│   │   ├── optical_processor.py# 处理光学数据
│   │   └── xray_processor.py     # 处理X射线数据
│   │
│   ├── analysis/               # 时变性质分析模块（对应您的第二步）
│   │   ├── __init__.py
│   │   ├── models.py           # 存放所有拟合函数（BPL, 物理模型等）
│   │   └── fitting.py          # 负责执行拟合操作的类或函数
│   │
│   └── utils/                  # 通用工具模块
│       ├── __init__.py
│       ├── time_converter.py   # 时间格式转换（UTC, MJD等）
│       └── flux_converter.py   # 流量/星等转换工具
│
├── tests/                      # 单元测试目录
│   ├── test_optical.py
│   └── test_xray.py
│
├── examples/                   # 使用示例
│   └── process_grb_250419A.ipynb # Jupyter Notebook 教程
│
├── pyproject.toml              # (推荐) 项目打包和依赖管理文件
└── README.md                   # 项目说明文件
```

### 一、首先处理光学数据，需要用户提供以下信息，
1.GRB的T0时间（UTC）；

2.准备包含以下信息的光学数据，数据文件为.csv，time（UTC）,曝光时间，mag，mag_err，望远镜名，滤波片，中心波长或等效波长。
读取数据后，做以下处理，

1.将观测时间转化为mid time，单位为s，即光学观测的时间-T0+曝光时间/2，

2.视星等和其误差转化为流量密度，

3.按时间从小到大排序，

4.另存到新的文件，文件名称为望远镜名+滤波片.csv，可指定保存路径。

### 二、对X射线光变曲线处理，准备包含以下信息的X射线数据，数据文件为.fits，

1. time（s），time err, count rate, count rate err, 我要将其转化为相对于T0的时间，读取header关键词['OBS-MJD']+time（s）-T0(需要转化为MJD格式)，通过转化因子将count rate转化为流量，然后保存为csv，保存的信息为time（s）（相对于T0的时间），time err（相对于T0的时间）,flux,flux err。文件名称为望远镜名_flux.csv，可指定保存路径。下一步读取望远镜名.csv，将流量转化为流量密度，保存为文件名称为望远镜名_flux_density.csv。

## 第二步时变性质分析

主要需要实现两个功能，一是任意个brokenpowrlaw函数拟合；二是余晖模型的拟合。
