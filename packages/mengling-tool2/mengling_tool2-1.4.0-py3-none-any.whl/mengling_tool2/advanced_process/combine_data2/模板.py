import mengling_tool2.spider_tools.spiders.spider_all as zz
from mengling_tool2.advanced_process.combine_data2.main import Combination
import config
import re, time, json


class Test(Combination):
    def __init__(self, name, r_index, r_connect, getspiderfunc, spider_config):
        Combination.__init__(self, name, r_connect, r_index,
                             getspiderfunc=getspiderfunc, spider_config=spider_config)
        self.addChilds('子任务1', '子任务2')
        pass

    def getRateNums(self, data: str):
        spider = self.getGood('spider')
        pass
        return [{'键值': None}]

    def getRatedts(self, data1: str):
        spider = self.getGood('spider')
        pass
        return [{}]


if __name__ == '__main__':
    # 参数
    name = '主任务前置名称'
    datas = ['']
    threadnum1, threadnum2 = 5, 5
    r_index, r_connect = 0, config.REDIS_CONNECT
    getspiderfunc, spider_config = zz.HttpSession, {}
    dbname, table, connect = '其他', name, config.WORK_CONNECT
    columnclassdict = {}

    # 任务定义
    t = Test(name, r_index, r_connect, getspiderfunc, spider_config)

    # 子任务1
    t.change('子任务1')
    t.run_one(t.getRateNums, datas, threadnum=threadnum1)

    # 子任务2
    results = t.getAllValue_to_dts_strs('子任务1', ['键值'])
    t.change('子任务2')
    t.run_one(t.getRatedts, results, threadnum=threadnum2)

    pass
    # 插入数据库
    t.inMysql(dbname, table, ifchecknum=True, ifmyisam=True, connect=connect,
              columnclassdict=columnclassdict)
    # 删除资源
    # t.delAllRedis()
    t.close()
