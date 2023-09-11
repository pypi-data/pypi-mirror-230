from threading import Lock
import time
import traceback
from ..tools.progress import Progress
from ..tools.thread import threads_run


class SuperTaskClass:
    def __init__(self, datas_childFunc, datas: list, cellnum=1, **kwargs):
        """
        :param datas_childFunc: 单位执行方法，参数组：(datas)
        :param datas: 数据组
        """
        # 线程数
        self.threadnum = kwargs.get('threadnum', 5)
        self.childFunc = datas_childFunc
        # 参数组
        self.datas = datas
        self.cellnum = cellnum
        self.name = kwargs.get('name', '任务组')
        # 错误组
        self.iftz = kwargs.get('iftz', True)
        self.__lock0 = Lock()  # 互斥锁，获取锁定
        self.__lock1 = Lock()  # 互斥锁，进度显示锁定

    def run(self):
        self.datas = list(self.datas)
        length = len(self.datas)
        if length == 0: return None
        if length < self.threadnum: self.threadnum = length
        jd = Progress(len(self.datas), self.name)

        def temp():
            nonlocal self, jd
            while True:
                self.__lock0.acquire()  # 上锁 注意了此时锁的代码越少越好
                datas = list()
                while len(self.datas) > 0 and (self.cellnum == 0 or len(datas) < self.cellnum):
                    datas.append(self.datas.pop(0))
                self.__lock0.release()  # 解锁
                # 没有任务，结束子线程
                if len(datas) == 0: break
                try:
                    self.childFunc(datas)
                except:
                    if self.iftz: print(traceback.format_exc())
                    print('[严重错误]参数组 ' + str(datas) + ' 失败')
                # 进度显示
                self.__lock1.acquire()  # 上锁 注意了此时锁的代码越少越好
                jd.add(len(datas))
                jd.printProgress()
                self.__lock1.release()  # 解锁

        start = time.time()
        print('任务开始...线程数：%s' % self.threadnum)
        threads_run(temp, [[] for i in range(self.threadnum)], ifwait=True)
        end = time.time()
        print('%s 运行时间: %s 秒' % (self.name, round(end - start, 2)))
