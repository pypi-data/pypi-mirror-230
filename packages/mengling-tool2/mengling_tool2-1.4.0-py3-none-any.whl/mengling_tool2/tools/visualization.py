import json
from math import inf
import matplotlib.pyplot as plt
import numpy as np
import pyecharts.options as opts
from pyecharts.charts import Line


# 获取回归方程系数
def _huigui(arr):
    numerator = 0.0
    denominator = 0.0
    arr_mean = np.mean(arr, axis=0)
    for point in arr:
        dx = point[0] - arr_mean[0]
        numerator += dx * (point[1] - arr_mean[1])
        denominator += np.square(dx)
    a = numerator / denominator
    b = arr_mean[1] - a * arr_mean[0]
    return a, b


def _getzh(ifcolor=True):
    if ifcolor:
        datas = ['red', 'blue', 'green', 'gold', 'brown',
                 'peru', 'grey', 'pink', 'slategray']
    else:
        datas = ['-', '--', '-.', ':', 'None', 'solid', 'dashed', 'dashdot', 'dotted']
    i = 0
    while True:
        yield datas[i]
        if i >= len(datas) - 1:
            i = 0
        else:
            i += 1


# 用于生成颜色及线段
_zh_color = _getzh(True)
_zh_li = _getzh(False)


class Loader:
    def __init__(self, datas, xs: list = None, md=1, p_color=None, p_size=15, ifhuigui=False, texts: list = None):
        if type(datas) in {tuple, list}:
            if xs is None:
                self.arr = np.array([[x, datas[x]] for x in range(len(datas))])
            else:
                assert len(xs) == len(datas), 'xs和ys长度不一致!'
                self.arr = np.array([[x, y] for x, y in zip(xs, datas)])
        else:
            self.arr = datas
        self.md = md
        self.p_color = p_color if p_color else next(_zh_color)
        self.p_size = p_size
        self.ifhuigui = ifhuigui
        assert texts is None or len(texts) == len(datas)
        self.texts = texts
        # 线参数
        self.linename = None
        self.line_color = None
        self.linestyle = None

    # 设置线参数
    def setLine(self, linename, line_color=None, linestyle=None):
        self.linename = linename
        self.line_color = line_color if line_color else next(_zh_color)
        self.linestyle = linestyle if linestyle else next(_zh_li)

    # 设置点参数
    def setPoint(self, p_size=15):
        self.p_size = p_size


# 图像化
def _graphical(ax, loader: Loader):
    # 绘制线
    if loader.linename:
        ax.plot(loader.arr[:, 0], loader.arr[:, 1], linestyle=loader.linestyle,
                c=loader.line_color)  # 显示点参数设置 marker='o'

    plt.grid(linestyle='-.')
    if loader.ifhuigui:
        a, b = _huigui(loader.arr)
        ax.plot([loader.arr[0, 0], loader.arr[-1, 0]], [a * loader.arr[0, 0] + b, a * loader.arr[-1, 0] + b],
                color='black')
    # 根据密度对点进行稀疏处理
    n = int(1 / loader.md)
    xs, ys, texts = [], [], []
    for i in range(0, loader.arr.shape[0], n):
        if loader.texts:
            texts.append(loader.texts[i])
        else:
            texts.append('')
        xs.append(loader.arr[i, 0])
        ys.append(loader.arr[i, 1])
    # 绘制值
    if loader.texts:
        for x, y, text in zip(xs, ys, texts):
            plt.text(x, y * 1.005, text, ha='center', va='bottom', fontsize=8, fontproperties='SimHei')
    # 绘制点,颜色可默认
    ax.scatter(xs, ys, c=loader.p_color, s=loader.p_size)


# 获取交点组方法
def _intersection(loadt1: Loader, loadt2: Loader):
    arr1 = np.array(sorted(loadt1.arr, key=lambda x: x[0]))
    arr2 = np.array(sorted(loadt2.arr, key=lambda x: x[0]))
    # 合成并集坐标组
    minx, maxx = max(arr1[0, 0], min(arr2[:, 1])), min(arr1[-1:, 0], max(arr2[:, 1]))
    xls = [x for x in set(arr1[:, 0] + arr2[:, 0]) if minx <= x <= maxx]
    xls.sort()

    # 合成坐标数组
    def getSupplys(arr: np.array) -> list:
        i = 0
        xys = list()
        while arr[i, 0] < minx:
            i += 1
        for x in xls:
            if i >= len(arr): break
            p = arr[i]
            if x == p[0]:
                xys.append(p)
            else:
                # 计算补位点
                p1 = arr[i + 1]
                dpy = (p1[1] - p[1]) / p[0] * p1[0]
                xys.append((x, dpy))
            i += 1
        return xys

    arr1 = getSupplys(arr1)
    arr2 = getSupplys(arr2)
    # 交点组
    dps = list()
    index, length = 0, len(xls)
    for index in range(length - 1):
        if arr1[index] == arr2[index]:
            dps.append(arr1[index])
        else:
            x10, y10 = arr1[index]
            x11, y11 = arr1[index + 1]
            x20, y20 = arr2[index]
            x21, y21 = arr2[index + 1]
            # 判断线段是否有交点
            if (y10 - y20) * (y11 - y21) < 0:
                a1, a2 = (y11 - y10) / (x11 - x10), (y21 - y20) / (x21 - x20)
                b1, b2 = y10 - a1 * x10, y20 - a2 * x20
                dx = (b2 - b1) / (a1 - a2)
                dy = a1 * dx + b1
                dps.append((dx, dy))
    # 判断最后一个点
    if arr1[index] == arr2[index]: dps.append(arr1[index])
    return dps


# 二维绘制
def graphicalN(*loadts, title='', xname='', yname='', intersections: list = None,
               ifonlysave=False, savefullpath='test.png'):
    ax = plt.figure().add_subplot(111)
    plt.title(title, fontproperties='SimHei')
    plt.xlabel(xname, fontproperties='SimHei')
    plt.ylabel(yname, fontproperties='SimHei')

    lines = list()
    for loadt in loadts:
        _graphical(ax, loadt)
        if loadt.linename: lines.append(loadt.linename)

    # 绘制个线的交点
    if intersections:
        dps = list()
        for ins in intersections:
            dps.extend(_intersection(*ins))
        if len(dps) > 0:
            # 绘制点,颜色可默认
            pxs, pys = [p[0] for p in dps], [p[1] for p in dps]
            ax.scatter(pxs, pys, color='orange', s=30)
            for x, y in dps:
                plt.text(x, y * 1.01, '(%s,%s)' % (round(x, 2), round(y, 2)), ha='center', va='bottom', fontsize=10)

    plt.legend(lines)
    if ifonlysave:
        plt.savefig(savefullpath)
    else:
        plt.show()


# 柱状图
def barChat(xs, ys, xname='', yname='', title='', ifline=False):
    assert len(xs) == len(ys), 'xs与ys的总长度不一致'
    """对不同的区段标为不同的颜色"""
    colors = []
    y14 = sum(ys) / len(ys) / 4
    for y in ys:
        if y < y14:
            colors.append("green")
        elif y < y14 * 2:
            colors.append("lightseagreen")
        elif y < y14 * 3:
            colors.append("gold")
        else:
            colors.append("coral")

    plt.bar(xs, ys, color=colors, tick_label=xs)

    for a, b in zip(xs, ys):
        plt.text(a, b + 0.1, b, ha='center', va='bottom')
    # 绘制线和点
    if ifline:
        plt.plot(xs, ys, color='red')  # 绘制线
        plt.scatter(xs, ys, color='m', s=15)  # 绘制点,颜色可默认
    plt.legend(loc="upper left")
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.title(title, fontproperties='SimHei')
    plt.xlabel(xname, fontproperties='SimHei')
    plt.ylabel(yname, fontproperties='SimHei')
    # plt.rcParams['savefig.dpi'] = 300  # 图片像素
    # plt.rcParams['figure.dpi'] = 300  # 分辨率
    # plt.rcParams['figure.figsize'] = (15.0, 8.0)  # 尺寸
    # plt.savefig('D:\\result.png')
    plt.show()


# 多参数对比型柱状图
def barChatN(xs, yss, xname='', yname='', title=''):
    indexs = np.arange(len(xs))
    width = 1 / len(yss) * 2 / 3
    colors = ['darkorange', 'deepskyblue', 'green']
    for i in range(len(yss)):
        ys = yss[i]
        assert len(xs) == len(ys), 'ys%s长度与xs不一致' % i
        plt.bar(indexs + i * width, ys, width=width, label='lab%s' % i, color=colors[i % 3])
        # 显示在图形上的值
        for a, b in zip(indexs, ys):
            plt.text(a + i * width, b + 0.1, b, ha='center', va='bottom')
    # 绘制x轴
    plt.bar(indexs + (len(yss) - 1) * width / 2, [0] * len(xs), width=width, tick_label=xs)
    plt.xticks()
    plt.legend(loc="upper left")  # 防止label和图像重合显示不出来
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.title(title, fontproperties='SimHei')
    plt.xlabel(xname, fontproperties='SimHei')
    plt.ylabel(yname, fontproperties='SimHei')
    plt.show()


# 不好显示大数据量
def lookWeb_old(title, names: list, xs: list, yss: list):
    js = {'title': title, 'names': names, 'xs': xs, 'datas': yss}
    with open('D:\web临时数据', 'w+', encoding='utf-8') as file:
        file.write(json.dumps(js))


def lookWeb_lines(title, xs, *yss, linexs: list = None, lineys: list = None, names=None, filepath='d:/web_data.html'):
    if lineys is None: lineys = []
    if linexs is None: linexs = []
    miny, maxy = inf, -inf
    linexs = [{"xAxis": p} for p in linexs]
    lineys = [{"yAxis": p} for p in lineys]

    line = Line(init_opts=opts.InitOpts(width="1680px", height="800px")).add_xaxis(xaxis_data=xs)
    for i in range(len(yss)):
        ys = yss[i]
        miny = min(miny, *ys)
        maxy = max(maxy, *ys)
        name = f"线{i}" if names is None else names[i]
        line.add_yaxis(
            series_name=name,
            y_axis=ys,
            yaxis_index=0,
            is_smooth=True,
            is_symbol_show=False,
        )
    (
        line.set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            datazoom_opts=[
                opts.DataZoomOpts(xaxis_index=0),
                opts.DataZoomOpts(type_="inside", xaxis_index=0),
            ],
            # visualmap_opts=opts.VisualMapOpts(
            #     pos_top="10",
            #     pos_right="10",
            #     is_piecewise=True,
            #     pieces=[
            #         {"gt": 0, "lte": 50, "color": "#096"},
            #         {"gt": 50, "lte": 100, "color": "#ffde33"},
            #         {"gt": 100, "lte": 150, "color": "#ff9933"},
            #         {"gt": 150, "lte": 200, "color": "#cc0033"},
            #         {"gt": 200, "lte": 300, "color": "#660099"},
            #         {"gt": 300, "color": "#7e0023"},
            #     ],
            #     out_of_range={"color": "#999"},
            # ),
            xaxis_opts=opts.AxisOpts(type_="category"),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name_location="start",
                min_=miny,
                max_=maxy,
                is_scale=True,
                axistick_opts=opts.AxisTickOpts(is_inside=False),
            ),
        ).set_series_opts(
            markline_opts=opts.MarkLineOpts(
                data=linexs + lineys,
                # [
                #     {"xAxis": 100},
                #     {"yAxis": 100},
                #     {"yAxis": 150},
                #     {"yAxis": 200},
                #     {"yAxis": 300},
                # ],
                label_opts=opts.LabelOpts(position="end"),
            )
        ).render(filepath)
    )
    print('file:///' + filepath)
    return filepath


# 多项式拟合
def polyFitting(ys, n=3):
    x = np.arange(0, len(ys), 1)
    y = np.array(ys)
    z1 = np.polyfit(x, y, n)  # 用3次多项式拟合
    p1 = np.poly1d(z1)
    print(p1)  # 在屏幕上打印拟合多项式
    yvals = p1(x)  # 也可以使用yvals=np.polyval(z1,x)
    plot1 = plt.plot(x, y, '*', label='original values')
    plot2 = plt.plot(x, yvals, 'r', label='polyfit values')
    plt.xlabel('x axis')
    plt.ylabel('y axis')
    plt.legend(loc=4)  # 指定legend的位置,读者可以自己help它的用法
    plt.title('polyfitting')
    plt.show()
