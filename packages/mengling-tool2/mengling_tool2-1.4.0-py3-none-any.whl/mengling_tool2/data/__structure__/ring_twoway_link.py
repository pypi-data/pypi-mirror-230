from threading import Lock


# 同步环状双向链表
class LinkedLooplist:
    def __init__(self, datas):
        self.index = 0
        self.__data__ = [data for data in datas]
        self.lock = Lock()

    def next(self, n=1):
        with self.lock:
            self.index += n
            self.index = self.index % len(self.__data__)
            data = self.__data__[self.index]
        return data

    def get(self):
        with self.lock:
            data = self.__data__[self.index]
        return data

    def getLen(self):
        with self.lock:
            l = len(self.__data__)
        return l
