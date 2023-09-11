# -*- coding: UTF-8 -*-
from threading import Lock, Thread
import time
from tqdm import tqdm

__LOCK = Lock()
# 记录上次是否为进度显示标识
__CACHE_IFJD = False


# 休眠进度显示
def sleepJd(sleep_time):
    for i in tqdm(range(int(sleep_time))):
        time.sleep(1)
    time.sleep(sleep_time - int(sleep_time))


def jdprint(*txts, ifjd=False):
    global __CACHE_IFJD
    __LOCK.acquire()
    assert (ifjd and len(txts) == 1) or not ifjd, '进度显示则输入只能有一个!'
    if ifjd:
        print('\r' + txts[0], end='')
    else:
        if __CACHE_IFJD: print('\r')
        print(*txts)
    __CACHE_IFJD = ifjd
    __LOCK.release()


# 进度类
class Progress():
    __jdpool = list()

    def __init__(self, maxlen: int, name=None):
        self.__index = 0
        self.__maxlen = maxlen
        self.__name = str(name) if name is not None else "work_task%s" % len(Progress.__jdpool)
        jdprint('[任务开始]', self.__name, '\n', '[数据量]', maxlen)
        # 添加至总池中
        Progress.__jdpool.append(self)

    # 进度完成
    def __over(self):
        jdprint('work_task:', self.__name + "已完成...")
        try:
            # 从总池中移除
            Progress.__jdpool.remove(self)
        except:
            pass

    # 进度显示
    def printProgress(self):
        p_str = str(self.__index) + "/" + str(self.__maxlen)
        jdprint('%s:%s' % (self.__name, p_str), ifjd=True)
        if self.__index >= self.__maxlen:  self.__over()

    # 百分比进度显示
    def printProgressDegree(self):
        p = 100 * self.getDegree()
        jdprint('%.2f%%' % p, ifjd=True)
        if self.__index >= self.__maxlen: self.__over()

    # 进度条输出
    def printProgressBar(self):
        p = 100 * self.getDegree()
        pi = int(p / 5)
        temp = list()
        for i in range(20):
            if i < pi:
                temp.append("▉")
            else:
                temp.append(" ")
        jdprint(''.join(['\r', self.__name, ':', "".join(temp), '|%.2f%%' % p]), ifjd=True)
        if self.__index >= self.__maxlen: self.__over()

    # 获取最大值
    def getMaxlen(self):
        return self.__maxlen

    # 获取当前进展值
    def getIndex(self):
        return self.__index

    # 获取百分比进程
    def getDegree(self) -> float:
        return self.__index / self.__maxlen

    # 进度增加
    def add(self, i: int = 1):
        self.__index = (self.__index + i) if self.__index + i <= self.__maxlen else self.__maxlen

    # 重置进度类状态
    def reset(self, maxlen=-1):
        self.__index = 0
        if maxlen > 0:
            self.__maxlen = maxlen

    # 监听进度
    def thread_Listening(self, data):
        import threading
        import time
        def temp(data):
            while len(data) < self.__maxlen:
                time.sleep(1)
                self.__index = len(data)
                self.printProgressBar()

        Thread(target=temp, args=(data,)).start()
        jdprint('开始监听进度...')
