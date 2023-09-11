from .thread_task import SuperTaskClass
from ..tools.goodlib import ThreadDictGoods
from ..database_tool2.mysql import MysqlExecutor
from ..tools.time import getNowTime
from ..spider_tools.selenium2 import ChromeDriver
from ..spider_tools.spiders.httpx import Httpx


class KeyValue(SuperTaskClass):
    def __init__(self, dbname, table, connect: dict, key_ifHave_b, key_getValue_dts,
                 iftz=True, columnclassdict: dict = None, ifdayupdate=False,
                 getdriverfunc=ChromeDriver, driver_config: dict = None,
                 getspiderfunc=Httpx, spider_config: dict = None):
        self.table = table
        self.columnclassdict = columnclassdict if columnclassdict is not None else {}
        self.dtgoods = ThreadDictGoods({'sqltool': [MysqlExecutor, {'dbname': dbname, 'ifassert': True, **connect}],
                                        'driver': [getdriverfunc,
                                                   driver_config if driver_config is not None else {'headless': True}],
                                        None: [lambda **kwargs: None, {}],
                                        'spider': [getspiderfunc, spider_config if spider_config is not None else {}]},
                                       {'driver': lambda x: x.quit(), None: lambda x: x})
        self.__ifHave__ = key_ifHave_b
        self.__getValue__ = key_getValue_dts
        self.ifdayupdate = ifdayupdate
        self.__nowday__ = getNowTime(gs='%Y-%m-%d')
        SuperTaskClass.__init__(self, self.__childFunc__, [], cellnum=1, name=table, iftz=iftz)

    # 获取线程资源
    def getGood(self, key):
        return self.dtgoods.getThreadKeyGood(key)

    # 快捷获取判断方法
    def getIfHaveFunc_default(self, keyname):
        def temp(key):
            sqltool = self.dtgoods.getThreadKeyGood('sqltool')
            time_where = f"`更新日期`='{self.__nowday__}'" if self.ifdayupdate else 'true'
            return sqltool.ifGet(self.table, where=f"`{keyname}`='{key}' and {time_where}")

        return temp

    def __save__(self, dts):
        sqltool = self.dtgoods.getThreadKeyGood('sqltool')
        try:
            sqltool.insert_create_dt(self.table, *dts, columnclassdict=self.columnclassdict)
            sqltool.commit()
        except:
            sqltool.rollback()
            assert False, f'数据插入错误! 已回滚'

    def __childFunc__(self, key):
        key = key[0]
        dts = self.__getValue__(key)
        if self.ifdayupdate:
            for dt in dts: dt['更新日期'] = self.__nowday__
        self.__save__(dts)

    def run(self, keys, threadnum=10, maxloopnum: int = -1):
        sqltool = self.dtgoods.getThreadKeyGood('sqltool')
        if self.ifdayupdate:
            if sqltool.ifGet(self.table, where=f"`更新日期`='{self.__nowday__}'"):
                print('此任务的更新日期也存在,不做插入操作!')
                sqltool.close()
                return
        print('[总量]', len(keys))
        while maxloopnum < 0 or maxloopnum > 0:
            # 表格不存在时不用判断
            if sqltool.ifExist(self.table):
                datast = set([key for key in keys if not self.__ifHave__(key)])
            else:
                datast = set(keys)
            if len(datast) > 0:
                self.datas = datast
                self.threadnum = threadnum
                SuperTaskClass.run(self)
                self.dtgoods.delAllGood()
            else:
                self.dtgoods.delAllGood()
                break
            maxloopnum -= 1
