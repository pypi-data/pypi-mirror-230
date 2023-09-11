from random import uniform
from numpy import exp


# 模拟退火算法
class Annealing:
    def __init__(self, valuefunc, maxstep=1, w0=0, t=100, week_num=100):
        self.func = valuefunc
        self.maxstep = maxstep
        self.w0 = w0
        self.value0 = valuefunc(w0)
        # 温度
        self.t = t
        # 单次迭代次数
        self.week_num = week_num

    # 单次随机
    def _ceil(self):
        w = self.w0 + uniform(-self.maxstep, self.maxstep)
        value = self.func(w)
        d = value - self.value0
        if d > 0 or exp(d * 100 / self.t) > uniform(0, 1):
            self.w0 = w
            self.value0 = value

    # 温度循环
    def cycle(self):
        while self.t > 0:
            for i in range(self.week_num):
                self._ceil()
            self.t -= 1


if __name__ == '__main__':
    al = Annealing(lambda x: -x ** 2 - 3 * x + 1, t=100)
    al.cycle()
    print(al.w0, al.value0)
