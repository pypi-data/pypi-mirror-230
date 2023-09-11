from random import sample
import numpy as np
import numpy.linalg as npl
import numpy.random as nprd


# 思路类似于聚类算法,通过与个个中心点的距离来进行分类
# 局部逼近单层级神经网络
class RBF:
    def __init__(self, input_dim, center_num, out_dim, beta=0.01):
        self.input_dim = input_dim
        self.center_num = center_num
        self.out_dim = out_dim
        self.beta = beta
        self.if_ramdom_center = True
        # 中心的列表,需要初始化
        self.centers = nprd.uniform(-1, 1, (center_num, input_dim))
        # 权重矩阵
        self.W = nprd.random((self.center_num, out_dim))

    # 径向基函数,高斯函数
    def __basisfunc(self, x, c):
        return np.exp(-(self.beta * npl.norm(x - c)) ** 2)

    # 墨西哥帽函数
    def __basisfunc1(self, x, c):
        r = npl.norm(x - c) ** 2
        return (1 - r / self.beta) * np.exp(-r / 2 / self.beta)

    # 中间层计算
    def __calcAct(self, X):
        G = np.zeros((X.shape[0], self.center_num), dtype=np.float32)
        for xi, x in enumerate(X):
            for ci, c in enumerate(self.centers):
                G[xi, ci] = self.__basisfunc(x, c)
        return G

    def train(self, X, Y):
        if self.if_ramdom_center:
            # 随机从样本中选取中心点
            self.centers = sample(list(X), self.center_num)
        else:
            # k-means算法计算中心点
            pass
            self.centers = []
        G = self.__calcAct(X)
        # 计算权重组,G*W=Y -> W=伪逆G*Y
        self.W = np.dot(npl.pinv(G), Y)

    def predict(self, X):
        G = self.__calcAct(X)
        # 计算结果
        Y = np.dot(G, self.W)
        return Y
