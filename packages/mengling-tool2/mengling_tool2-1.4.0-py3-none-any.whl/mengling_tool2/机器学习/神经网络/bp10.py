import numpy as np


# 需要装好cupy的环境才能用,调用gpu运算
# import cupy as np


# bp神经网络
# 参考:https://blog.csdn.net/buxiangspeaking/article/details/123795429
class BP:
    # 自定义中间层神经元数量及层次
    def __init__(self, input_dim, mid_dims: list, out_all_ls: list, train_XY: list = None, np_page=None):
        if np_page:
            self._np = np_page
        else:
            self._np = np
        assert len(mid_dims) > 0
        assert len(out_all_ls) == len(set(out_all_ls))
        if train_XY:
            X, Y = train_XY
            # 用于初始的预训练,选出误差最小的初始权值组
            args = list()
            for i in range(100):
                vs = self._ininArgs(input_dim, mid_dims, out_all_ls)
                E = self.getE(X, Y, ifmean=True)
                args.append((E, vs))
            vs = sorted(args, key=lambda x: x[0])[0][1]
            self.Wim, self.W_mids, self.Wmo, self.Bs = vs
        else:
            self._ininArgs(input_dim, mid_dims, out_all_ls)

    # 获取初始化参数组
    def _ininArgs(self, input_dim, mid_dims: list, out_all_ls):
        # 维度记录
        self.input_dim, self.mid_dims, self.out_all_ls = input_dim, mid_dims, out_all_ls
        # 输出层权值
        Wim = self._np.random.uniform(-1, 1, (input_dim, mid_dims[0]))
        self.Wim = Wim
        # 中间层权值组
        W_mids = [self._np.random.uniform(-1, 1, (mid_dims[i], mid_dims[i + 1])) for i in range(len(mid_dims) - 1)]
        self.W_mids = W_mids
        # 输出层权值
        Wmo = self._np.random.uniform(-1, 1, (mid_dims[-1], len(out_all_ls)))
        self.Wmo = Wmo
        # 偏置值组
        Bs = [self._np.ones(dim) for dim in mid_dims[1:] + [len(out_all_ls)]]
        self.Bs = Bs
        return Wim, W_mids, Wmo, Bs

    # 映射结果
    def _mapY(self, Y0):
        Y = self._np.zeros((len(Y0), len(self.out_all_ls)))
        for i, y in enumerate(Y0):
            index = self.out_all_ls.index(y)
            Y[i, index] = 1
        return Y

    # 获取映射结果
    def _getResultY(self, Y):
        result = list()
        for y in Y:
            index = list(y).index(max(y))
            result.append(self.out_all_ls[index])
        return self._np.array(result)

    # 概率分配激活函数
    def _softmaxY(self, Y):
        PY = self._np.zeros(Y.shape)
        for i, y in enumerate(Y):
            y1 = self._np.exp(y)
            PY[i] = y1 / sum(y1)
        return PY

    # 激活函数
    def _sigmoid(self, X):
        return 1 / (1 + self._np.exp(-X))

    # 激活函数的偏导,g(x)=x*(1-x)
    def _dsigmoid(self, X):
        return X * (1 - X)

    # 正向传播计算输出
    def _forward(self, X):
        C_out = self._sigmoid(X @ self.Wim)
        M_outs = list()
        F = C_out
        for W, B in zip(self.W_mids, self.Bs[:-1]):
            M_out = self._sigmoid(F @ W + B)
            M_outs.append(M_out)
            F = M_out
        O_out = self._sigmoid(F @ self.Wmo + self.Bs[-1])

        return C_out, M_outs, O_out

    # 反向传播更新权值
    def _back(self, C_out, M_outs, O_out, Y):
        assert len(Y) == O_out.shape[0]
        delta_Wmo = (Y - O_out) * self._dsigmoid(O_out)
        delta_W_mids = list()
        FW, delta_FW = self.Wmo, delta_Wmo
        # 需要反向
        for W, M_out in zip(self.W_mids[::-1], M_outs[::-1]):
            delta_W_mid = delta_FW @ FW.T * self._dsigmoid(M_out)
            delta_W_mids.append(delta_W_mid)
            FW, delta_FW = W, delta_W_mid
        delta_Wim = delta_FW @ FW.T * self._dsigmoid(C_out)

        return delta_Wmo, delta_W_mids, delta_Wim

    def train(self, X, Y0, week: int, step=1, print_num=10, step_revise_num=8, step_revise=2):
        Y = self._mapY(Y0)
        min_e_arg = None
        w = int(week / print_num)
        for i in range(week):
            # 正向传播计算输出值
            C_out, M_outs, O_out = self._forward(X)
            # 反向训练获取梯度系数
            delta_Wmo, delta_W_mids, delta_Wim = self._back(C_out, M_outs, O_out, Y)
            # 更新权重,由于一次计算了多个样本,所以需要求平均
            self.Wim += step / X.shape[0] * X.T @ delta_Wim
            F_out = C_out
            for W_mid, M_out, delta_W_mid in zip(self.W_mids, M_outs, delta_W_mids[::-1]):
                W_mid += step / X.shape[0] * F_out.T @ delta_W_mid
                F_out = M_out
            self.Wmo += step / X.shape[0] * F_out.T @ delta_Wmo
            # 更新偏置值
            for B, delta_W in zip(self.Bs, delta_W_mids[::-1] + [delta_Wmo]):
                B += step * self._np.mean(delta_W, axis=0)
            # 计算误差矩阵
            E = self._np.mean(self._np.square(Y - O_out) / 2)
            # 记录历史最小误差参数
            if min_e_arg is None or E < min_e_arg[0]:
                Wim, W_mids, Wmo, Bs = self.Wim, self.W_mids, self.Wmo, self.Bs
                min_e_arg = [E, [Wim, W_mids, Wmo, Bs]]
            elif step_revise_num > 0:
                # 当出现误差大于上次训练时将脚步减小,误差为开口向上的抛物线
                step /= step_revise
                step_revise_num -= 1
                print(f'出现误差增大情况,脚步缩小{step_revise}倍 剩余缩小次数:{step_revise_num}')
            else:
                print('模型收敛,提前结束', f'当前次数{i + 1}')
                break
            if i % w == 0: print('训练次数:', i + 1, '当前误差:', E)

        if min_e_arg:
            self.Wim, self.W_mids, self.Wmo, self.Bs = min_e_arg[1]
            print('最终误差:', min_e_arg[0])

    def predict(self, X, if_probability_Y=False):
        Y = self._forward(X)[-1]
        if if_probability_Y:
            return self._softmaxY(Y)
        else:
            return self._getResultY(Y)

    # 获取当前误差
    def getE(self, X, Y0, ifmean=True):
        Y = self._mapY(Y0)
        C_out, M_outs, O_out = self._forward(X)
        E = self._np.square(Y - O_out) / 2
        if ifmean:
            return self._np.mean(E)
        else:
            return E


def saveModel(bper: BP, name, path=None) -> str:
    datas = [bper.input_dim, bper.mid_dims, bper.out_all_ls]
    if np == bper._np:
        datas += [bper.Wim, bper.W_mids, bper.Wmo, bper.Bs]
    else:
        # cupy->numpy
        datas += [bper._np.asnumpy(bper.Wim),
                  [bper._np.asnumpy(x) for x in bper.W_mids],
                  bper._np.asnumpy(bper.Wmo),
                  [bper._np.asnumpy(x) for x in bper.Bs]]
    arr = np.array(datas, dtype=object)
    filepath = f'{(path + "/") if path else ""}{name}'
    np.save(filepath, arr=arr)
    print('保存模型成功', filepath + '.npy')
    return filepath + '.npy'


def loadModel(filename, np_page=None) -> BP:
    arr = np.load(filename, allow_pickle=True)
    bper = BP(1, [1], [0], np_page=np_page)
    bper.input_dim, bper.mid_dims, bper.out_all_ls, bper.Wim, bper.W_mids, bper.Wmo, bper.Bs = arr
    # numpy->cupy
    if bper._np != np:
        bper.Wim = np_page.asarray(bper.Wim)
        bper.W_mids = [np_page.asarray(x) for x in bper.W_mids]
        bper.Wmo = np_page.asarray(bper.Wmo)
        bper.Bs = [np_page.asarray(x) for x in bper.Bs]
    print(f'加载bp模型文件:{filename}\n输入维度:{bper.input_dim}\n中间层:{bper.mid_dims}\n输出结果集:{bper.out_all_ls}')
    return bper
