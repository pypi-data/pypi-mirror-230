import math
import random

'''
遗传算法的节点及流程:
    制作参数基因
    淘汰算法
    基因突变算法
    基因重组算法
    迭代流程
'''


class Heredity:
    def __init__(self, rna_num: int, ls_fitness_value, min_result, mutation_p,
                 initial_rnas_num=10, savenum=100, minv=0, maxv=100,
                 *initial_rnas):
        # RNA长度
        self.rna_num = rna_num
        # 基因取值范围
        self.minv = minv
        self.maxv = maxv
        # 计算适应度方法
        self.fitnessfunc = ls_fitness_value
        # 最低输出适应值,到达该值时迭代结束
        self.min_result = min_result
        # 突变率
        self.mutation_p = mutation_p
        # 当前存活的种群,初始时不够数据则随机生成初始rna
        self.save_rnas = list(initial_rnas)
        for i in range(initial_rnas_num - len(initial_rnas)):
            self.save_rnas.append(tuple([random.uniform(minv, maxv) for k in range(rna_num)]))
        # 生存空间
        self.savenum = savenum

    # 种群选择
    def select(self, rnas):
        rna_values = list()
        for rna in rnas:
            value = self.fitnessfunc(rna)
            rna_values.append([rna, value])
        # 根据适应度排序
        rna_values.sort(key=lambda x: x[1], reverse=True)
        # 最低的适应度
        pass
        # 生存空间竞争
        rna_values = rna_values[:self.savenum]
        return rna_values

    # 基因突变
    def mutation(self, rna):
        index_rnadt = dict()
        for i in range(len(rna)):
            if random.uniform(0, 1) <= self.mutation_p:
                index_rnadt[i] = random.uniform(self.minv, self.maxv)
        if len(index_rnadt) > 0:
            rna_re = list(rna)
            for i, v in index_rnadt.items():
                rna_re[i] = v
            rna = tuple(rna_re)
        return rna

    # 基因重组
    def recombination(self, rna1, rna2):
        # 随机取交换点
        i = math.ceil(random.uniform(1, self.rna_num - 1))
        rna_ch = rna1[:i] + rna2[i:]
        return rna_ch

    # 开始迭代
    def run(self):
        period = 1
        while True:
            print('第', period, '代')
            # 全排列基因重组
            rnas = self.save_rnas
            rna_chs = list()
            # (n^2+n)/2排列数
            for i in range(len(rnas)):
                for k in range(i + 1, len(rnas)):
                    # 基因重组
                    rna_ch = self.recombination(rnas[i], rnas[k])
                    # 基因突变
                    rna_ch = self.mutation(rna_ch)
                    rna_chs.append(rna_ch)
            rnas.extend(rna_chs)
            # 开始选择
            rna_values = self.select(rnas)
            self.save_rnas = [rna for rna, value in rna_values]
            # 判断是否满足最低要求
            max_prna = rna_values[0][0]
            max_value = rna_values[0][1]
            print('当代最大rna序列:', max_prna)
            print('当代最大值:', max_value)
            if max_value >= self.min_result:
                return max_prna, max_value, period
            else:
                period += 1


if __name__ == '__main__':
    # -x^2-2x-1=0
    h = Heredity(10, lambda ls: -sum([((v + 1) ** 2) for v in ls]), -0.001, 0.05,
                 initial_rnas_num=10, savenum=100, minv=-100, maxv=100)
    print(h.run())
