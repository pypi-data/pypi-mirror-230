import time
from threading import currentThread, Lock


# 资源池
class ResourcePool:
    def __init__(self, objs: list, timeout=15, iftz=False, backfunc=lambda x: None):
        self.__objs__ = objs
        self.__timeout__ = timeout
        # 使用字典
        self.__makemap__ = dict()
        # 用户字典
        self.__tidmap__ = dict()
        for i in range(len(objs)):
            self.__makemap__[i] = False
        self.__lock__ = Lock()
        self.__iftz__ = iftz
        self.__backfunc__ = backfunc

    # 获取
    def __getObj__(self, tid):
        obj = None
        with self.__lock__:
            index = self.__tidmap__.get(tid)
            if index is None:
                # 判断是否还有剩余
                for i, r in self.__makemap__.items():
                    if not r:
                        self.__makemap__[i] = True
                        self.__tidmap__[tid] = i
                        obj = self.__objs__[i]
                        if self.__iftz__: print(f'tid:{tid} 分配资源成功!')
                        break
            else:
                obj = self.__objs__[index]
                if self.__iftz__: print(f'tid:{tid} 已有资源')
        return obj

    def getLen(self):
        return len(self.__objs__)

    # 默认使用当前线程id为标识符
    def get(self, tid=None):
        tid = currentThread().ident if tid is None else tid
        obj = self.__getObj__(tid)
        i = 1
        # 判断获取是否成功,选择进入排队模式
        while obj is None and i < self.__timeout__:
            time.sleep(1)
            if self.__iftz__: print(f'tid:{tid} 等待资源分配 {i}s/{self.__timeout__}s')
            obj = self.__getObj__(tid)
            i += 1
        if obj is None:
            raise TimeoutError(f'tid:{tid} 排队已超时')
        else:
            return obj

    # 归还资源控制权
    def back(self, tid=None):
        tid = currentThread().ident if tid is None else tid
        with self.__lock__:
            index = self.__tidmap__.get(tid)
            if index is not None:
                self.__makemap__[index] = False
                self.__tidmap__.pop(tid)
                self.__backfunc__(self.__objs__[index])
                if self.__iftz__:
                    print(f'tid:{tid} 资源已归还,闲置资源剩余{len(self.__objs__) - len(self.__tidmap__)}个')

    def add(self, obj):
        with self.__lock__:
            self.__makemap__[len(self.__objs__)] = False
            self.__objs__.append(obj)
            if self.__iftz__:
                print(f'新增资源成功,闲置资源剩余{len(self.__objs__) - len(self.__tidmap__)}个')

    def closeAll(self, closefunc=lambda x: x.close()):
        for obj in self.__objs__:
            try:
                closefunc(obj)
            except:
                pass
        # 清空字典
        self.__makemap__.clear()
        self.__tidmap__.clear()
        if self.__iftz__: print('资源释放完成...')
