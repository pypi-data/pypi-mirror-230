import traceback
from threading import Lock


# 用于同步操作
class Synchro:
    def __init__(self, it: iter, maxerrornum=0, data_errorfunc=lambda x: None):
        self.it = it
        self.errorfunc = data_errorfunc
        self.maxerrornum = maxerrornum
        self.errornum = 0
        self.lock = Lock()
        self.data = None
        self.ifinitdata = True

    def getData(self):
        with self.lock:
            if self.ifinitdata:
                try:
                    self.data = next(self.it)
                    self.ifinitdata = False
                except:
                    traceback.print_exc()
                    self.data = None
            data = self.data
        return data

    def resetError(self, data):
        with self.lock:
            if data == self.data: self.errornum = 0

    def errorData(self, data) -> bool:
        with self.lock:
            b = False
            if data == self.data:
                if self.errornum >= self.maxerrornum:
                    try:
                        self.errorfunc(self.data)
                    except:
                        traceback.print_exc()
                    try:
                        self.data = next(self.it)
                        b = True
                    except:
                        traceback.print_exc()
                        self.data = None
                        print('同步迭代器出错,可能为全部消耗!默认返回None')
                    self.errornum = 0
                else:
                    self.errornum += 1
            return b
