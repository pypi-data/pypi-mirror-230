from secrets import choice
from threading import Lock

# 同步资源数据结构
class Resource:
    def __init__(self, max_error_num: int, datas: list = None):
        if datas is None: datas = list()
        self.lock = Lock()
        self.__datadt__ = dict()
        for data in datas:
            self.__datadt__[data] = 0
        self.max_error_num = max_error_num

    def getLen(self):
        with self.lock:
            l = len(self.__datadt__)
        return l

    def put(self, data):
        with self.lock:
            self.__datadt__[data] = 0

    def get(self, num=1) -> list:
        with self.lock:
            ds = list(self.__datadt__.keys())
        return ds[:num]

    # 随机取出一条
    def randomGet(self, default=None):
        with self.lock:
            try:
                data = choice(list(self.__datadt__.keys()))
            except:
                data = default
        return data

    def error(self, data):
        with self.lock:
            if self.__datadt__.get(data) is not None:
                if self.__datadt__[data] >= self.max_error_num:
                    self.__datadt__.pop(data)
                else:
                    self.__datadt__[data] += 1