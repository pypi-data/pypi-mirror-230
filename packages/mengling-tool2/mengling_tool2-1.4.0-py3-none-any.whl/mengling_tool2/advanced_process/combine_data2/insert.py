import json
from ...tools.progress import jdprint
from ...database_tool2.mysql import MysqlExecutor
from ...database_tool2.postgresql import PostgresqlExecutor
from ...tools.time import runTimeFunc
from ...tools.thread import getTasks, threads_run
from pandas import DataFrame
import warnings


# 数量检查
def checknum(dtgoods, name, name_wait):
    r = dtgoods.getThreadKeyGood('r')
    assert r.getLen(name, _class='hash') == r.getLen(name_wait), \
        f'数量不一致,不执行插入数据库任务! {r.getLen(name, _class="hash")}/{r.getLen(name_wait)}'


# 获取全部列
def _getLies(r, dts):
    if dts:
        lies = list(DataFrame(data=dts).columns)
        return lies
    else:
        return []


# 数据迭代器
def _datait(r, name, n, if_auto_data=True, nowday=None):
    allkeys = r.hkeys(name)
    for i in range(0, len(allkeys), n):
        redts = list()
        for txt in r.hmget(name, allkeys[i:i + n]):
            for dt in json.loads(txt):
                for k in dt.keys():
                    # 格式清洗
                    if if_auto_data and type(dt[k]) in (tuple, list, dict):
                        dt[k] = json.dumps(dt[k], ensure_ascii=False)
                    dt[k] = str(dt[k]).strip().replace('\x00', '')
                # 添加更新日期
                if nowday:  dt['更新日期'] = nowday
                redts.append(dt)
        yield redts
    yield None


def _ch_insert(dbname, connect, table, lies, dts, cig):
    sqltool = MysqlExecutor(dbname, **connect)
    try:
        sqltool.insert_create_dt(table, *dts, lies=lies, ifcreate=False)
        sqltool.commit()
    except Exception as e:
        sqltool.rollback()
        cig['error'] = e
    sqltool.close()


@runTimeFunc
def inMysql_old(name, name_wait, dbname, table, connect, lies, columnclassdict: dict, key, threadnum,
                ifmyisam, ifdeltable, n, dtgoods, ifchecknum, nowday, if_auto_data):
    connect = connect.copy()
    connect['ifassert'] = True
    sqltool = MysqlExecutor(dbname, **connect)
    r = dtgoods.getThreadKeyGood('r')
    jdprint('读取及处理redis数据...')
    if ifchecknum:
        assert r.getLen(name, _class='hash') == r.getLen(name_wait), \
            f'数量不一致,不执行插入数据库任务! {r.getLen(name, _class="hash")}/{r.getLen(name_wait)}'
    if nowday:
        print(nowday)
        if sqltool.ifGet(table, where=f"`更新日期`='{nowday}'"):
            print('存在同日期数据,删除旧版')
            sqltool.delete(table, where=f"`更新日期`='{nowday}'")
    elif ifdeltable:
        sqltool.deleteTable(table)
    sqltool.commit()
    allkeys = r.hkeys(name)
    all_value_len = 0
    if not sqltool.ifExist(table):
        if lies is None:
            jsons = r.hmget(name, allkeys[:n])
            values = list()
            for j in jsons:
                dts = json.loads(j)
                values.extend(dts)
            lies = list(DataFrame(data=values).columns)
        if len(lies) > 0:
            if nowday: lies.append('更新日期')
            sqltool.createTable(table, lies, columnclassdict=columnclassdict if columnclassdict is not None else {},
                                key=key, ifmyisam=ifmyisam)

    for i in range(0, len(allkeys), n):
        jsons = r.hmget(name, allkeys[i:i + n])
        values = list()
        for j in jsons:
            dts = json.loads(j)
            values.extend(dts)
        jdprint('插入mysql...%s' % n)
        all_value_len += len(values)
        if len(values) > 0:
            # 增加更新日期
            if nowday:
                for dt in values: dt['更新日期'] = nowday
            # 数据清洗
            for dt in values:
                for k in dt.keys():
                    # 格式清洗
                    if if_auto_data and type(dt[k]) in (tuple, list, dict):
                        dt[k] = json.dumps(dt[k])
                    dt[k] = str(dt[k]).strip().replace('\x00', '')

            sqltool.thread_insert_commit(table, values, lies=lies,
                                         threadnum=threadnum, ifcreate=False)
    if all_value_len == 0:
        print('没有数据插入数据库!')
    elif (nowday is None and sqltool.getNum(table) != all_value_len) \
            or (nowday and sqltool.getNum(table, where=f"`更新日期`={nowday}") != all_value_len):
        sqltool.close()
        raise ValueError('数量不一致,插入出现错误!')
    sqltool.close()


@runTimeFunc
def inMysql(name, dbname, table, connect, lies, threadnum, n, dtgoods,
            nowday, if_auto_data, ifdeltable, ifmyisam=True, key=None, coldt=None):
    connect = connect.copy()
    connect['ifassert'] = True
    sqltool = MysqlExecutor(dbname, **connect)
    r = dtgoods.getThreadKeyGood('r')
    # 数据准备
    jdprint('读取及处理redis数据...')
    datait = _datait(r, name, n, if_auto_data, nowday)
    datadts = next(datait)
    if lies is None: lies = _getLies(r, datadts)
    if len(lies) == 0:
        warnings.warn(f'{name} 没有获的列,不执行插入操作!')
        return
    # 处理结果表
    if nowday and sqltool.ifExist(table):
        sqltool.delete(table, f"`更新日期`='{nowday}'")
        sqltool.commit()
    else:
        if ifdeltable: sqltool.deleteTable(table)
        sqltool.createTable(table, lies, columnclassdict=coldt, key=key, ifmyisam=ifmyisam)

    all_value_len = 0
    cig = dict()
    # 插入
    while True:
        if datadts:
            all_value_len += len(datadts)
        else:
            break
        jdprint('插入mysql...%s' % n)
        tasks = getTasks(threadnum, datadts)
        threads_run(_ch_insert, [[dbname, connect, table, lies, dts, cig] for dts in tasks], ifone=False)
        # 子任务出现错误抛出
        if cig.get('error'):
            raise cig['error']
        else:
            datadts = next(datait)
    if all_value_len == 0: print('没有数据插入数据库!')
    sqltool.close()


@runTimeFunc
def inMysql_strict(name, dbname, table, connect, lies, threadnum, n,
                   dtgoods, nowday, if_auto_data, ifdeltable,
                   ifmyisam=True, key=None, coldt=None):
    temp_table = table + '_datatemp'
    connect = connect.copy()
    connect['ifassert'] = True
    sqltool = MysqlExecutor(dbname, **connect)
    r = dtgoods.getThreadKeyGood('r')
    jdprint('读取及处理redis数据...')
    datait = _datait(r, name, n, if_auto_data, nowday)
    datadts = next(datait)
    if lies is None: lies = _getLies(r, datadts)
    if len(lies) == 0:
        warnings.warn(f'{name} 没有获的列,不执行插入操作!')
        return
    # 删除临时表
    sqltool.deleteTable(temp_table)

    all_value_len = 0
    cig = dict()
    # 创建临时表
    sqltool.createTable(temp_table, lies, columnclassdict=coldt, key=key, ifmyisam=ifmyisam)
    # 插入临时表
    while True:
        if datadts:
            all_value_len += len(datadts)
        else:
            break
        jdprint('插入mysql...%s' % n)
        tasks = getTasks(threadnum, datadts)
        threads_run(_ch_insert, [[dbname, connect, temp_table, lies, dts, cig] for dts in tasks], ifone=False)
        if cig.get('error'):
            raise cig['error']
        else:
            datadts = next(datait)
    if all_value_len == 0: print('没有数据插入数据库!')
    # 处理结果表
    if sqltool.ifExist(table):
        if ifdeltable:
            if nowday is None:
                sqltool.deleteTable(table)
            else:
                sqltool.delete(table, f"`更新日期`='{nowday}'")
                sqltool.commit()
    else:
        sqltool.createTable(table, lies, columnclassdict=coldt, key=key, ifmyisam=False)
    # 同步数据
    try:
        sqltool.run(f'INSERT INTO `{table}` select * from `{temp_table}`')
        sqltool.commit()
    except Exception as e:
        sqltool.rollback()
        sqltool.close()
        raise e
    sqltool.deleteTable(temp_table)
    sqltool.close()


def _ch_pg_insert(dbname, connect, table, lies, dts, cig):
    with PostgresqlExecutor(dbname, **connect) as pgt:
        try:
            pgt.insert_create_dt(table, *dts, lies=lies, ifcreate=False)
            pgt.commit()
        except Exception as e:
            pgt.rollback()
            cig['error'] = e


@runTimeFunc
def inPGsql(name, dbname, table, connect, lies, threadnum, n, dtgoods,
            nowday, if_auto_data, ifdeltable, key=None, colmap=None):
    connect = connect.copy()
    connect['ifassert'] = True
    r = dtgoods.getThreadKeyGood('r')
    with PostgresqlExecutor(dbname, **connect) as pgt:
        # 数据准备
        jdprint('读取及处理redis数据...')
        datait = _datait(r, name, n, if_auto_data, nowday)
        datadts = next(datait)
        if lies is None: lies = _getLies(r, datadts)
        if len(lies) == 0:
            warnings.warn(f'{name} 没有获的列,不执行插入操作!')
            return
        # 处理结果表
        if nowday and pgt.ifExist(table):
            pgt.delete(table, f"\"更新日期\"='{nowday}'")
        else:
            if ifdeltable: pgt.deleteTable(table)
            pgt.createTable(table, lies, colmap=colmap, key=key)
        pgt.commit()

    all_value_len = 0
    cig = dict()
    # 插入
    while True:
        if datadts:
            all_value_len += len(datadts)
        else:
            break
        jdprint('插入pgsql...%s' % n)
        tasks = getTasks(threadnum, datadts)
        threads_run(_ch_pg_insert, [[dbname, connect, table, lies, dts, cig] for dts in tasks], ifone=False)
        # 子任务出现错误抛出
        if cig.get('error'):
            raise cig['error']
        else:
            datadts = next(datait)
    if all_value_len == 0: print('没有数据插入数据库!')
