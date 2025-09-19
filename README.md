# grbtools

一、首先处理光学数据，需要用户提供以下信息，
1.GRB的T0时间（UTC）；
2.准备包含以下信息的光学数据，数据文件为.csv，time（UTC）,曝光时间，mag，mag_err，望远镜名，滤波片，中心波长或等效波长。
读取数据后，做以下处理，
1.将观测时间转化为mid time，单位为s，即光学观测的时间-T0+曝光时间/2，
2.视星等和其误差转化为流量密度，
3.按时间从小到大排序，
4.另存到新的文件，文件名称为望远镜名+滤波片.csv，可指定保存路径。

二、对X射线光变曲线处理，准备包含以下信息的X射线数据，数据文件为.fits，1. time（s），time err, count rate, count rate err, 我要将其转化为相对于T0的时间，读取header关键词['OBS-MJD']+time（s）-T0(需要转化为MJD格式)，通过转化因子将count rate转化为流量，然后保存为csv，保存的信息为time（s）（相对于T0的时间），，time err（相对于T0的时间）,flux,flux err。文件名称为望远镜名_flux.csv，可指定保存路径。下一步读取望远镜名.csv，将流量转化为流量密度，保存为文件名称为望远镜名_flux_density.csv。

第二步时变性质分析

主要需要实现两个功能，一是任意个brokenpowrlaw函数拟合；二是余晖模型的拟合。
