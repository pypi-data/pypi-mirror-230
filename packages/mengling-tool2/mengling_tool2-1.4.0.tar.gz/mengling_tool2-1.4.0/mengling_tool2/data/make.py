import copy
import string
from secrets import choice
import numpy as np
import emoji
import random
import hashlib
import base64
import math
from pandas import DataFrame


# 获取列表中较大或较小区间的子列表
def getPartials(values: list, ifmax=True, var_p: float = 0.5):
    datas = np.array(values)
    # 方差目标降低至该值
    markvar = datas.var() * var_p
    assert var_p > 0, 'var_p应该大于0！'
    for i in range(100):
        # 取高于平均数的值
        arev = datas.mean()
        if ifmax:
            values = [v for v in datas if v >= arev]
        else:
            values = [v for v in datas if v <= arev]
        datas = np.array(values)
        # 计算当前列表方差是否低于设定方差
        var = datas.var()
        if var <= markvar or np.isnan(var): break
    if i == 99: raise ValueError('超出迭代次数限制')
    return values


# 获取纯净的编码字符串
def getPureStr(string: str, encoding="utf-8"):
    result = string.strip().encode(encoding, "ignore").decode(encoding)
    # 清除表情字符
    result = emoji.demojize(result)
    return result


# 获取指定长度的随机密码,默认为大写及数字
def getRandomPassword(n, ls=string.ascii_letters + string.digits):
    return ''.join([choice(ls) for i in range(n)])


# 按照区间段随机取出指定个数的数据
def getSectionRandoms(ls, num, ifeven=True):
    n = len(ls)
    if n <= num:
        results = copy.deepcopy(ls)
    else:
        if ifeven:
            results = list()
            d = n // num
            for i in range(0, (num - 1) * d, d):
                results += random.sample(ls[i:i + d], 1)
            # 最后一个区间直到最后一位元素
            results += random.sample(ls[(num - 1) * d:], 1)
        else:
            results = random.sample(ls, num)
    return results


# 获取回归方程系数
def __huigui(datays, dataxs: list = None):
    if dataxs is None: dataxs = list(range(len(datays)))
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
def __lineVar(list0, ifallnum=False):
    if len(list0) <= 2: return 0
    xlist = list(range(len(list0)))
    a, b = __huigui(xlist, list0)
    sumv = 0
    A, B, C = a, -1, b
    for x in xlist:
        v = abs(A * x + B * list0[x] + C) / (A ** 2 + B ** 2) ** (1 / 2)
        sumv += v
    if ifallnum:
        return sumv
    else:
        return sumv / len(list0)


# def ddall(ls0):
#     if len(ls0) <= 3: return ls0, []
#     indexdt=dict()
#     for i in range(len(ls0)):
#
#     #对点进行系数记录

# 将数据分成2部分，以回归偏差情况为判断标准,以点为切割,输出的数据会比输入是多
def dd2(list0):
    # 区间最少数据量为4
    if len(list0) <= 3: return list0, []
    varlist = [np.inf]
    # 从第二个点开始进行切割记录
    for i in range(1, len(list0) - 1):
        y1, y2 = list0[0:i], list0[i:]
        xi1, xi2 = len(y1) / len(list0), len(y2) / len(list0)
        varlist.append(__lineVar(y1) * xi1 + __lineVar(y2) * xi2)
    minv = min(varlist)
    for i in range(1, len(varlist)):
        if varlist[i] == minv:
            return list0[0:i], list0[i:]


# 二分区域迭代
def ddn(list0, n):
    if n < 2: return [list0]
    sumlist = []
    ys1, ys2 = dd2(list0)
    # 根据区间偏差与区间值数量的乘积最小进行最划分
    # if __lineVar(ys1) * len(ys1) >= __lineVar(ys2) * len(ys2):
    if __lineVar(ys1) >= __lineVar(ys2):
        sumlist.extend(ddn(ys1, n - 1))
        sumlist.append(ys2)
    else:
        sumlist.append(ys1)
        sumlist.extend(ddn(ys2, n - 1))
    return sumlist


# 无监督二分区域划区,以单个值为分割点,第一区间的末尾为第二区间的首位
def ddAuto(list0, k0, minn=5):
    # 数据少于4个则不划分
    if len(list0) <= minn: return [list0]
    # 根据区间偏差与区间值数量占比的乘积最小进行最划分
    # 小于k系数将不再细分子区域
    linev = __lineVar(list0)
    k = k0 * np.mean(list0) / 100
    if linev <= k: return [list0]

    ys1, ys2 = dd2(list0)
    sumlist = []
    templist1 = ddAuto(ys1, k0)
    templist2 = ddAuto(ys2, k0)

    # print(linev2,len(ys2))
    sumlist.extend(templist1)
    sumlist.extend(templist2)

    resultls = list()
    # 合并小区间,保证单个区间数量满足最低限制
    sumlist = [s for s in sumlist if len(s) > 0]
    i, length = 0, len(sumlist)
    while i < length:
        result = sumlist[i]
        while i < length - 1 and len(result) < minn:
            i += 1
            # 仅头区间不用剔除相同数值
            result += sumlist[i][1:]
        resultls.append(result)
        i += 1
    # 检测尾部数量是否满足条件
    if len(resultls[-1]) < minn:
        temp = resultls.pop(-1)
        resultls[-1].extend(temp[1:])
    return resultls


# 无监督二分区域划区,以单个值为分割点,第一区间的末尾为第二区间的首位,基于区间数量进行划分
def ddAuto_num(list0, num, minn=5):
    # 数据少于最低个数则不划分
    if len(list0) <= minn: return [list0]

    ys1, ys2 = dd2(list0)
    if num <= 2: return [ys1, ys2]

    sumlist = []
    templist1 = ddAuto_num(ys1, math.floor(num / 2))
    templist2 = ddAuto_num(ys2, math.floor(num / 2))

    # print(linev2,len(ys2))
    sumlist.extend(templist1)
    sumlist.extend(templist2)

    return sumlist


# 生成对象的md5
def encryption_md5(txt: str, encoding='utf-8'):
    str_md5 = hashlib.md5(bytes(txt, encoding=encoding)).hexdigest()
    return str_md5


# 加密
def encryption(key, value):
    data = base64.b64encode(key.encode('utf-8')) + \
           base64.b64encode(value.encode('utf-8'))
    return base64.b64encode(data).decode('utf-8')


# 解密
def decrypt(key, data_enc):
    value = base64.b64decode(data_enc).decode('utf-8') \
        .replace(base64.b64encode(key.encode('utf-8')).decode('utf-8'), '')
    return base64.b64decode(value).decode('utf-8')


# 无密匙加密
def encode(data, encoding='utf-8'):
    k = base64.b64encode(data.encode(encoding)).decode(encoding)
    return k.replace('/', '%')


# 无密匙解密
def decode(key, encoding='utf-8'):
    return base64.b64decode(key.replace('%', '/')).decode(encoding)


def toFloat(x, n=2):
    return round(float(x), n)


def joinStr(str0, ls: list, index: int = None):
    if index is not None: ls = [v[index] for v in ls]
    return str(str0).join(list(map(str, ls)))


# 科学平均数
def s_Average(dataslist: list):
    if len(dataslist) == 0:
        return -np.inf
    else:
        sums = []
        for x in dataslist:
            sums.append(x ** (1 / len(dataslist)))
        sum_ave = 1
        for sum in sums:
            sum_ave *= sum
        return sum_ave


# 获取方差
def getVar(ls):
    return np.array(ls).var()


# 排列组合
def combination(*lss):
    if len(lss) < 2: return lss

    def temp(ls1, ls2):
        templs = list()
        for v1 in ls1:
            for v2 in ls2:
                v1c = copy.copy(v1)
                v1c.append(v2)
                templs.append(v1c)
        return templs

    ls0 = [[v] for v in lss[0]]
    for ls in lss[1:]:
        ls0 = temp(ls0, ls)
    return ls0


# 清洗字典
def dictClean(dt, oldv_func_newv):
    for k in dt.keys():
        dt[k] = oldv_func_newv(dt[k])


# 去突变影响,根据涨跌幅计算基准数据集
def regular(zdfls, v0: float = 100):
    v = v0
    valuels = list()
    # 去首位
    for zdf in zdfls:
        v *= 1 + zdf / 100
        valuels.append(v)
    return valuels


# 多项式拟合
def polynomial(ys, n=3, ifgetgs=False):
    xs = np.arange(0, len(ys), 1)
    ys = np.array(ys)
    z1 = np.polyfit(xs, ys, n)  # 多项式拟合
    pl = np.poly1d(z1)
    if ifgetgs:
        return pl
    else:
        print(pl)  # 在屏幕上打印拟合多项式
        yvals = pl(xs)  #
        return np.append([xs], [yvals], axis=0).T


# 列去重
def columnMerge(datas: list, *indexs, ifreturndt=True) -> dict or DataFrame:
    df = DataFrame(data=datas)
    df.drop_duplicates(subset=indexs, keep='first', inplace=True)
    if ifreturndt:
        # 返回格式:[{列1:值1},{列1:值2}...]
        return df.to_dict(orient="records")
    else:
        return df


if __name__ == '__main__':
    years = list(range(2010, 2021))
    n0s = [9, 21, 30, 60, 90, 120, 150, 180]
    n1s = [9, 15, 21, 30, 42, 60, 90]
    n2s = [9, 15, 21, 30, 42, 60, 90, 120, 150]
    a = combination(years, n0s, n1s, n2s)
    print()
