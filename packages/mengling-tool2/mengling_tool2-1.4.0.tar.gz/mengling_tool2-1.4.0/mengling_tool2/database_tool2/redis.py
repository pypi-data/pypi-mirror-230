from redis import Redis, ConnectionPool
from threading import Lock

_connection_pool = {}
_lock = Lock()


# 切换库需在连接时添加db=库序列
# 建立连接池
class RedisExecutor(Redis):
    def __init__(self, dbindex: int, **connect):
        self.host = connect.get('host', '127.0.0.1')
        self.port = connect.get('port', 6379)
        self.password = connect.get('password', None)
        self.ifassert = connect.get('ifassert', False)
        self.__connect = connect
        self._key = (dbindex, self.host, self.port)
        with _lock:
            # decode_responses默认False返回值为byte类型
            _connection_pool[self._key] = _connection_pool.get(self._key, ConnectionPool(host=self.host, port=self.port,
                                                                             password=self.password,
                                                                             db=dbindex, decode_responses=True))
            # 获取连接
            Redis.__init__(self, connection_pool=_connection_pool[self._key])

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with _lock:
            self.close()

    def _select(self, _class, name, *values, **funcdt):
        if _class in funcdt.keys():
            return funcdt[_class](name, *values)
        else:
            raise ValueError('%s数据类型没有定义!' % _class)

    # 重写方法适应大数据量插入
    def sadd(self, name, *values):
        # 统一插入
        n = 5_0000
        for i in range(0, len(values), n):
            Redis.sadd(self, name, *values[i:i + n])

    # 重写方法适应大数据量删除
    def srem(self, name, *values):
        # 统一删除
        n = 5_0000
        for i in range(0, len(values), n):
            Redis.srem(self, name, *values[i:i + n])

    # 加入
    def addData(self, name, *values, _class='set'):
        return self._select(_class, name, *values, set=self.sadd, list=self.lpush, hash=self.hmset)

    def __getAllLs__(self, name, *null):
        return self.lrange(name, 0, self.llen(name))

    # 取出
    def getData(self, name, *values, _class='set'):
        return self._select(_class, name, *values, set=self.smembers, list=self.__getAllLs__, hash=self.hgetall)

    # 获取数量
    def getLen(self, name, _class='set'):
        return self._select(_class, name, set=self.scard, list=self.llen, hash=self.hlen)

    # 判断是否为成员
    def ifExist(self, name, value, _class='set'):
        return self._select(_class, name, value, set=self.sismember, hash=self.hexists)

    # 导出
    def popData(self, name, _class='set'):
        return self._select(_class, name, set=self.spop, list=self.lpop)

    # 删除
    def delData(self, name, *values, _class='set'):
        return self._select(_class, name, *values, set=self.srem, hash=self.hdel)

    def getNoGetKeys(self, pattern):
        names = self.keys(pattern=pattern)
        keys = list()
        for name in names:
            dt = self.getData(name, _class='hash')
            [keys.append(key) for key in dt.keys() if len(dt[key]) == 0]
        return keys

    def copyTo(self, new_index: int, pattern, new_connect=None):
        names = self.keys(pattern=pattern)
        new_connect = new_connect if new_connect else self.__connect
        r = RedisExecutor(new_index, **new_connect)
        for name in names:
            t = self.type(name)
            print(name, t)
            data = self.getData(name, _class=t)
            if type(data) not in [list, tuple, set]:
                data = [data]
            r.addData(name, *data, _class=t)
        r.close()

    def getAllValues(self, name):
        datas = list()
        for key in self.keys(pattern=name):
            datas.extend(self.hvals(key))
        assert '' not in datas, '有数据未完成抓取!'
        return datas
    # # 获取集合类型值:名字字典
    # def getSet_Key_name(self, namepattern) -> dict:
    #     data_name = dict()
    #     names = self.keys(pattern=namepattern)
    #     if len(names) > 0:
    #         for name in names:
    #             ds = self.smembers(name)
    #             for d in ds:
    #                 data_name[d] = name
    #     return data_name


if __name__ == '__main__':
    import config
    import json

    r = RedisExecutor(0, **config.REDIS_CONNECT)
    name = '210917_京东产品详情'
    for key in r.hkeys(name):
        value = r.hget(name, key)
        js = json.loads(value)[0]
        if len(js['title']) == 0:
            print(key)
            r.hdel(name, key)

    # print(r.spop(name,10))
    # for key in r.hkeys(name):
    #     v = r.hget(name, key)
    #     if v == '300':
    #         print(key)
    # print(key,v)
    # r.hdel(name, key)
    # r.hmset(name, {key + '&fs=true': v})

    r.close()
