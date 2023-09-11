import json
import time
from math import inf
from threading import Lock, get_ident
from ...data.structure import Synchro
from ...spider_tools.spiders.httpx import Httpx
from ...spider_tools.selenium2 import ChromeDriver
from .data import run_redis
from .config import Config
from .insert import inMysql_old, inMysql, inMysql_strict, checknum, inPGsql
import traceback


class Combination(Config):
    def __init__(self, name0, redis_connect, dbindex=0,
                 getdriverfunc=ChromeDriver, driver_config: dict = None,
                 getspiderfunc=Httpx, spider_config: dict = None):
        Config.__init__(self, name0, redis_connect, dbindex,
                        getdriverfunc, driver_config,
                        getspiderfunc, spider_config)
        self.__lock__ = Lock()
        self.__public_itdts__ = list()
        # 线程分配资源情况
        self.__thread_distributedt__ = dict()

    def __getChildFunc__(self, configs, func, cellnum):
        def temp(datas):
            if configs[0] > 0 and not configs[1]:
                print(f'等待休息{configs[0]}s...')
                time.sleep(configs[0])
            if configs[1]: configs[1] = False
            try:
                # 参数多态化
                if cellnum > 1:
                    base_dts_dt = func(datas)
                elif cellnum == 1:
                    base = datas[0]
                    base_dts_dt = {base: func(base)}
                else:
                    # 无参数启动
                    base_dts_dt = {0: func()}
            except Exception as e:
                self.errorDistribute()
                raise e
            self.backDistribute()
            r = self.dtgoods.getThreadKeyGood('r')
            for key, ls in base_dts_dt.items():
                # 不再清洗数据
                # for dt in base_dts_dt[base]:
                #     for key in dt.keys():
                #         key = str(key).strip()
                #         # 全部定义为字符串类型
                #         dt[key] = str(dt[key]).strip()
                # assert type(ls) == list, f'键:{key} 值的类型必须为list! 当前为{type(ls)}'
                # 记录
                r.addData(self.name, {key: json.dumps(ls, ensure_ascii=False)}, _class='hash')

        return temp

    def setDistributeFunc(self, *funcits, ci=inf, sleeptime=0, maxerrornum=5):
        for funcit in funcits:
            objer = Synchro(funcit, maxerrornum)
            self.__public_itdts__.append(
                {'objer': objer, 'makeid': None,
                 'ci': ci, 'ci0': ci, 'time': 0, 'sleeptime': sleeptime, })

    def change(self, chname):
        assert chname in self.__chnames__, '没有该子任务'
        self.__setName__(f'{self.name0}_{chname}')

    # 获取分配资源
    def getDistribute(self):
        if len(self.__public_itdts__) == 0: return None
        cid = get_ident()
        if self.__thread_distributedt__.get(cid) is None:
            ifget = False
            while True:
                tmin = 999
                with self.__lock__:
                    for dbdt in self.__public_itdts__:
                        # 是否使用
                        if dbdt['makeid'] is None:
                            t = int(dbdt['time'] + dbdt['sleeptime'] - time.time())
                            # 是否在休眠
                            if t <= 0:
                                # 次数是否耗尽
                                if dbdt['ci'] > 0:
                                    dbdt['makeid'] = cid
                                    dbdt['ci'] -= 1
                                    self.__thread_distributedt__[cid] = dbdt
                                    ifget = True
                                    break
                                # 进入休眠
                                else:
                                    dbdt['ci'] = dbdt['ci0']
                                    dbdt['time'] = time.time()
                            else:
                                tmin = min(t, tmin)
                if ifget:
                    break
                else:
                    print(f'\r{cid}没有可用资源... 最短剩余时间:{tmin}', end='')
                    time.sleep(1)
        tig = self.__thread_distributedt__[cid]
        # 需要资源再进行生产
        return tig['objer'].getData()

    # 资源错误
    def errorDistribute(self):
        cid = get_ident()
        dbdt = self.__thread_distributedt__.get(cid)
        if dbdt:
            b = dbdt['objer'].errorData(dbdt['objer'].data)
            # 重置状态
            if b:
                dbdt['ci'] = dbdt['ci0']
                dbdt['time'] = 0
            self.backDistribute()

    # 重置资源错误情况
    def resetErrorDistribute(self):
        cid = get_ident()
        dbdt = self.__thread_distributedt__.get(cid)
        if dbdt:
            dbdt['objer'].resetError(dbdt['objer'].data)

    # 资源归还
    def backDistribute(self):
        cid = get_ident()
        dbdt = self.__thread_distributedt__.get(cid)
        if dbdt:
            dbdt['makeid'] = None
            self.__thread_distributedt__[cid] = None

    # 资源关闭
    def closeDistribute(self, func=lambda x: x.close()):
        if func:
            for dbdt in self.__public_itdts__:
                try:
                    func(dbdt['objer'].data)
                except:
                    traceback.print_exc()
        self.__public_itdts__.clear()

    def run(self, strs_func_base_js, strs, cellnum: int, threadnum=10,
            getnum=10_0000, maxloop=20, sleeptime=0, iftz=True):
        r = self.dtgoods.getThreadKeyGood('r')
        if len(strs) > 0:
            r.addData(self.name_wait, *[str(s) for s in strs], _class='set')
        elif r.getLen(self.name_wait, _class='set') == 0:
            try:
                raise ValueError('redis中没有组合数据!')
            except:
                traceback.print_exc()
            self.dtgoods.delAllGood(iftz)
            return -1
        func = self.__getChildFunc__([sleeptime, True], strs_func_base_js, cellnum)
        run_redis(self.name, self.name_ready, self.name_wait, func, self.dtgoods,
                  threadnum, getnum, cellnum, maxloop, iftz)
        self.dtgoods.delAllGood(iftz)

    def run_one(self, str_func_js, strs, threadnum=10, getnum=10_0000, maxloop=20, sleeptime=0, iftz=True):
        # 单个和多个处理不同,参数多态化
        return self.run(str_func_js, strs, 1, threadnum, getnum, maxloop, sleeptime, iftz)

    # 无参数启动
    def run_nodata(self, str_func_js, maxloop=20, sleeptime=0, iftz=True):
        return self.run(str_func_js, [0], 0, 1, 1, maxloop, sleeptime, iftz)

    def inMysql(self, dbname, table, connect, lies=None, columnclassdict: dict = None, key=None, threadnum=10,
                ifmyisam=True, ifdeltable=True, n=50_0000, ifchecknum=True, ifdayupdate=False,
                if_auto_data=True):
        return inMysql_old(self.name, self.name_wait, dbname, table, connect, lies, columnclassdict, key, threadnum,
                           ifmyisam, ifdeltable, n, self.dtgoods, ifchecknum, self.nowday if ifdayupdate else None,
                           if_auto_data)

    def inMysql_new(self, dbname, table, connect, lies=None, columnclassdict: dict = None, key=None, threadnum=10,
                    ifmyisam=True, ifdeltable=True, n=50_0000, ifchecknum=True, ifdayupdate=False,
                    if_auto_data=True):
        if ifchecknum: checknum(self.dtgoods, self.name, self.name_wait)
        return inMysql(self.name, dbname, table, connect, lies, threadnum, n, self.dtgoods,
                       self.nowday if ifdayupdate else None, if_auto_data, ifdeltable,
                       ifmyisam, key, columnclassdict)

    def inMysql_strict(self, dbname, table, connect, lies=None, columnclassdict: dict = None, key=None, threadnum=10,
                       ifmyisam=True, ifdeltable=True, n=50_0000, ifchecknum=True, ifdayupdate=False,
                       if_auto_data=True):
        if ifchecknum: checknum(self.dtgoods, self.name, self.name_wait)
        return inMysql_strict(self.name, dbname, table, connect, lies, threadnum, n, self.dtgoods,
                              self.nowday if ifdayupdate else None, if_auto_data, ifdeltable,
                              ifmyisam, key, columnclassdict)

    def inPGsql(self, dbname, table, connect, lies=None, colmap: dict = None, key=None, threadnum=10,
                ifdeltable=True, n=50_0000, ifchecknum=True, ifdayupdate=False, if_auto_data=True):
        if ifchecknum: checknum(self.dtgoods, self.name, self.name_wait)
        return inPGsql(self.name, dbname, table, connect, lies, threadnum, n, self.dtgoods,
                       self.nowday if ifdayupdate else None, if_auto_data, ifdeltable,
                       key, colmap)

    def close(self, iftz=True, close_distribute_func=None):
        self.closeDistribute(close_distribute_func)
        self.dtgoods.delAllGood(iftz)
