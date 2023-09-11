from ...tools.goodlib import ThreadDictGoods
from ...database_tool2.redis import RedisExecutor
from ...tools.time import getNowTime
import json


class Config:
    def __init__(self, name0, redis_connect, dbindex,
                 getdriverfunc, driver_config: dict,
                 getspiderfunc, spider_config: dict):
        # 子类任务名称
        self.__chnames__ = list()
        self.name0 = name0
        # 用于判断是否为更新类型的任务
        self.nowday = getNowTime(gs='%Y-%m-%d')
        self.dtgoods = ThreadDictGoods({'r': [RedisExecutor, {'dbindex': dbindex, **redis_connect}],
                                        'driver': [getdriverfunc,
                                                   driver_config if driver_config is not None else {'headless': True}],
                                        None: [lambda **kwargs: None, {}],
                                        'spider': [getspiderfunc,
                                                   spider_config if spider_config is not None else {}], },
                                       {'driver': lambda x: x.quit(), None: lambda x: x})

    def __setName__(self, name):
        self.name = name
        self.name_wait = f'{name}_wait'
        self.name_ready = f'{name}_ready'

    def addChilds(self, *chnames):
        [self.__chnames__.append(chname) for chname in chnames]

    # 获取线程资源
    def getGood(self, key):
        return self.dtgoods.getThreadKeyGood(key)

    def getValue(self, chname, key, ifjson: bool = True, default=None) -> str or dict:
        assert chname in self.__chnames__, '没有该子任务'
        r = self.dtgoods.getThreadKeyGood('r')
        name = f'{self.name0}_{chname}'
        value = r.hget(name, key)
        if value is None:
            return default
        elif ifjson:
            return json.loads(value)
        else:
            return value

    def getAllValue_to_key_js(self, chname) -> dict:
        assert chname in self.__chnames__, '没有该子任务'
        r = self.dtgoods.getThreadKeyGood('r')
        resultdt = dict()
        name = f'{self.name0}_{chname}'
        for key in r.hkeys(name):
            resultdt[key] = json.loads(r.hget(name, key))
        return resultdt

    def getAllValue_to_dts_strs(self, chname, vkeys: list, ifhavekey=False, split='$$$') -> list:
        key_jss = self.getAllValue_to_key_js(chname)
        results = list()
        for key, jss in key_jss.items():
            for js in jss:
                rs = [key] if ifhavekey else []
                rs += [str(js.get(k, '')) for k in vkeys]
                results.append(split.join(rs))
        return results

    def getAllValue_to_dt_str(self, chname, vkeys: list, ifhavekey=False, split='$$$') -> list:
        key_js = self.getAllValue_to_key_js(chname)
        results = list()
        for key, js in key_js.items():
            rs = [key] if ifhavekey else []
            rs += [str(js.get(k, '')) for k in vkeys]
            results.append(split.join(rs))
        return results

    def getAllValue_to_ls(self, chname, ifhave_key=False) -> list:
        assert chname in self.__chnames__, '没有该子任务'
        r = self.dtgoods.getThreadKeyGood('r')
        name = f'{self.name0}_{chname}'
        if ifhave_key:
            dt = r.hgetall(name)
            # 文本进入也会被json处理
            return [(k, json.loads(v)) for k, v in dt.items()]
        else:
            return [json.loads(v) for v in r.hvals(name)]

    # 可用于新增新的字典
    def putRedis(self, name_hz, key, value):
        r = self.dtgoods.getThreadKeyGood('r')
        r.hset(f'{self.name0}_add_{name_hz}', key, value)

    # 从自定义字典中取值
    def getRedis(self, name_hz, key):
        r = self.dtgoods.getThreadKeyGood('r')
        return r.hget(f'{self.name0}_add_{name_hz}', key)

    def delRedis(self, chname):
        assert chname in self.__chnames__, '没有该子任务'
        r = self.dtgoods.getThreadKeyGood('r')
        self.__setName__(f'{self.name0}_{chname}')
        r.delete(self.name, self.name_wait, self.name_ready)
        print(self.name, '已清理redis数据...')

    def delAllRedis(self):
        for chname in self.__chnames__:
            self.delRedis(chname)
