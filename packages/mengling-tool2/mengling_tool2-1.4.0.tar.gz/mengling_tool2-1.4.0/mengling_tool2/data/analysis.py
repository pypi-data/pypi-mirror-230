import numpy as np
import pandas as pd
import math


# 数据格式处理
def __datasHandle(*lss) -> list:
    rs = list()
    for ls in lss:
        assert len(ls) > 0, 'ls中没有数据!'
        rs.append(list(map(float, ls)))
    return rs


# 获取回归方程系数
def getHuiGui_ab(datays, dataxs: list = None):
    if dataxs is None:
        dataxs = list(range(len(datays)))
        datays = __datasHandle(datays)[0]
    else:
        datays, dataxs = __datasHandle(datays, dataxs)
    numerator = 0.0
    denominator = 0.0
    x_mean = np.mean(dataxs)
    y_mean = np.mean(datays)
    n = len(dataxs)
    for i in range(n):
        numerator += (dataxs[i] - x_mean) * (datays[i] - y_mean)
        denominator += np.square(dataxs[i] - x_mean)
    a = (numerator / denominator) if denominator != 0 else 0
    b = y_mean - a * x_mean

    return a, b


# 描述点与回归线的离散情况
# 回归偏差
def getLineVar(list0):
    if len(list0) <= 2: return 0
    list0 = __datasHandle(list0)[0]
    xlist = list(range(len(list0)))
    a, b = getHuiGui_ab(xlist, list0)
    sumv = 0
    A, B, C = a, -1, b
    for x in xlist:
        v = abs(A * x + B * list0[x] + C) / (A ** 2 + B ** 2) ** (1 / 2)
        sumv += v
    return sumv / len(list0)


# 获取标准差
def getVar(ls):
    ls = __datasHandle(ls)[0]
    mv = np.mean(ls)
    # 计算方差
    sumv = sum([((v - mv) ** 2) for v in ls]) / len(ls)
    return sumv ** 0.5


# 关联度(Sperman秩相关系数)
# 正负为相关性
# /value/<=0.3->不存在线性相关
# 0.3</value/<=0.5->低度线性相关
# 0.5</value/<=0.8->显著线性相关
# /value/>0.8->高度线性相关
# 如果数据中没有重复值， 并且当两个变量完全单调相关时，斯皮尔曼相关系数则为+1或−1
def getRelation_Sperman(xs, ys, ifgetvalue=True):
    assert len(xs) == len(ys), 'xs与ys长度需一致'
    xs, ys = __datasHandle(xs, ys)
    data = pd.DataFrame({'xs': list(xs), 'ys': list(ys)})
    # 按两项进行各自排序
    data.sort_values('xs', inplace=True)
    data['xs_rank'] = np.arange(1, len(data) + 1)
    data.sort_values('ys', inplace=True)
    data['ys_rank'] = np.arange(1, len(data) + 1)
    # 计算项排名差的平方
    data['d2'] = (data['xs_rank'] - data['ys_rank']) ** 2
    n = len(data)
    # 按公式计算Sperman秩相关系数
    r = 1 - 6 * (data['d2'].sum()) / (n * (n ** 2 - 1))
    if ifgetvalue:
        return round(r, 4)
    else:
        ar = abs(r)
        b = '正' if r > 0 else '负'
        if ar <= 0.3:
            return '不存在线性相关'
        elif ar <= 0.5:
            return '低度%s线性相关' % b
        elif ar <= 0.8:
            return '中度%s线性相关' % b
        else:
            return '高度%s线性相关' % b


# 获取协方差
# 可以通过具体数字来度量两组或两组以上数据间的相关关系
# 如果两个变量的变化趋势一致，协方差就是正值，说明两个变量正相关。如果两个变量的变化趋势相反，协方差就是负值，说明两个变量负相关。如果两个变量相互独立，那么协方差就是0，说明两个变量不相关
def getCov(xs, ys):
    assert len(xs) == len(ys), 'xs与ys长度需一致'
    xs, ys = __datasHandle(xs, ys)
    x_mean = np.mean(xs)
    y_mean = np.mean(ys)
    result = sum([((x - x_mean) * (y - y_mean)) for x, y in zip(xs, ys)]) / (len(xs) - 1)
    return result


# 获取信息熵
def getEntropy(*ps):
    sumv = 0
    # H=sum(-plog2p)
    for p in ps:
        sumv += -p * math.log2(p)
    return sumv
