from secrets import randbelow
from threading import get_ident


class Goods:
    def __init__(self, getgoodfunc_kwarg: list, closegoodfunc=lambda g: g.close()):
        self.__key_good = dict()
        self.getGoodFunc, self.kwarg = getgoodfunc_kwarg
        self.closeGoodFunc = closegoodfunc

    # 获取线程对应的driver
    def getGood(self, key):
        if self.__key_good.get(key, None) is None:
            self.__key_good[key] = self.getGoodFunc(**self.kwarg)
        good = self.__key_good[key]
        return good

    # 删除线程对应的driver
    def delGood(self, key, iftz=True):
        # 对应池中driver
        if self.__key_good.get(key, None) is not None:
            good = self.__key_good[key]
            self.closeGoodFunc(good)
            self.__key_good.pop(key)
            if iftz: print('线程%s的资源已删除' % key)
        else:
            if iftz: print('线程%s未拥有资源,删除失败' % key)

    def delAllGood(self, iftz=True):
        for key in list(self.__key_good.keys()):
            good = self.__key_good[key]
            self.closeGoodFunc(good)
        self.__key_good = dict()
        if iftz: print('线程资源已全部关闭')


class DictGoods:
    def __init__(self, chkey_getgoodfunc_kwarg: dict, chkey_closegoodfunc: dict = None):
        if chkey_closegoodfunc is None:
            chkey_closegoodfunc = dict()
        self.__key_good = dict()
        # 用于设置内部子资源以字典形式存放
        self.getgoodfunc_kwarg = chkey_getgoodfunc_kwarg
        # 设置默认关闭方法
        for chkey in chkey_getgoodfunc_kwarg.keys():
            if chkey_closegoodfunc.get(chkey, None) is None:
                chkey_closegoodfunc[chkey] = lambda x: x.close()
        self.chkey_closegoodfunc = chkey_closegoodfunc

    def addDict(self, chkey_getgoodfunc_kwarg: dict, chkey_closegoodfunc: dict = None):
        if chkey_closegoodfunc is None:
            chkey_closegoodfunc = dict()
        self.getgoodfunc_kwarg.update(chkey_getgoodfunc_kwarg)
        for chkey in chkey_getgoodfunc_kwarg.keys():
            if chkey_closegoodfunc.get(chkey, None) is None:
                chkey_closegoodfunc[chkey] = lambda x: x.close()
        self.chkey_closegoodfunc.update(chkey_closegoodfunc)

    # 获取线程对应的driver
    def getKeyGood(self, key, chkey):
        if self.__key_good.get(key, None) is None: self.__key_good[key] = dict()
        if self.__key_good[key].get(chkey, None) is None:
            func, kwarg = self.getgoodfunc_kwarg[chkey]
            self.__key_good[key][chkey] = func(**kwarg)
        good = self.__key_good[key][chkey]
        return good

    # 删除线程对应的driver
    def delKeyGood(self, key, iftz=True):
        # 对应池中driver
        if self.__key_good.get(key, None) is not None:
            goodt = self.__key_good[key]
            [self.chkey_closegoodfunc[chkey](goodt[chkey]) for chkey in goodt.keys()]
            self.__key_good.pop(key)
            if iftz: print('线程%s的资源已删除' % key)
        else:
            if iftz: print('线程%s未拥有资源,删除失败' % key)

    def delAllGood(self, iftz=True):
        for key in list(self.__key_good.keys()):
            goodt = self.__key_good[key]
            [self.chkey_closegoodfunc[chkey](goodt[chkey]) for chkey in goodt.keys()]
            self.__key_good.pop(key)
        self.__key_good = dict()
        if iftz: print('线程资源已全部关闭')


class ThreadGoods(Goods):
    def __init__(self, getgoodfunc_kwarg: list, closegoodfunc=lambda g: g.close()):
        Goods.__init__(self, getgoodfunc_kwarg, closegoodfunc)

    # 获取线程对应的资源
    def getThreadGood(self):
        return self.getGood(get_ident())

    # 删除线程对应的资源
    def delThreadGood(self, iftz=True):
        return self.delGood(get_ident(), iftz=iftz)


class ThreadDictGoods(DictGoods):
    def __init__(self, chkey_getgoodfunc_kwarg: dict, chkey_closegoodfunc: dict = None):
        DictGoods.__init__(self, chkey_getgoodfunc_kwarg, chkey_closegoodfunc)

    # 获取线程对应的资源
    def getThreadKeyGood(self, chkey):
        return self.getKeyGood(get_ident(), chkey)

    # 删除线程对应的资源
    def delThreadKeyGood(self, iftz=True):
        return self.delKeyGood(get_ident(), iftz=iftz)


# 随机分布资源库
class RandomData:
    def __init__(self):
        self.all_weight = 0
        self.__dtls = list()

    def addFunc(self, weight: int, func, *args, **kwargs):
        assert weight > 0, '权值需大于0!'
        self.all_weight += weight
        self.__dtls.append({'weight': self.all_weight, 'value': (func, args, kwargs), 'type': 'func'})

    def addValues(self, weight, *values):
        assert weight > 0, '权值需大于0!'
        for value in values:
            self.all_weight += weight
            self.__dtls.append({'weight': self.all_weight, 'value': value})

    def randomGet(self):
        r = randbelow(self.all_weight)
        for dt in self.__dtls:
            if dt['weight'] > r:
                if dt.get('type') == 'func':
                    func, args, kwargs = dt['value']
                    return func(*args, **kwargs)
                else:
                    return dt['value']
        assert False, '出现错误!'
