import json
import re
import pandas as pd
from ..data.make import regular
from ..database_tool2.mysql import MysqlExecutor
from ..tools.time import getNowTime, TimeTool
from ..spider_tools.spiders.httpx import Httpx
from chinese_calendar import is_workday
from ..decorates.retry import retryFunc_args
from threading import Lock

_getSqlt = None
_lock = Lock()
TABLE = '主板'
_allcodetp = None


def setSqlt(func):
    global _getSqlt
    _getSqlt = func


def setTable(table):
    global TABLE
    TABLE = table


def getAllCodes() -> tuple:
    global _allcodetp
    with _lock:
        if _allcodetp is None:
            with _getSqlt() as sqlt:
                _allcodetp = tuple(sqlt.select('股票代码', f'{TABLE}_代码', ifget_one_lie=True))
        return _allcodetp


# 获取处理完成后的数据字典(无约束,仅做数据有效化处理)
@retryFunc_args(sleeptime=1, iftz=False)
def fetchDf(code, where='1=1', other="order by `日期` ASC") -> pd.DataFrame:
    with _getSqlt() as sqlt:
        df = sqlt.select("*", TABLE, where=f"`股票代码`='{code}' and {where}", other=other, data_class='df')
        return df


# 获取处理完成后的数据字典(时间约束)
def fetchDateDf(code, mindate: str = None, maxdate: str = None) -> pd.DataFrame:
    mindate = "1900-01-01" if mindate is None else mindate
    maxdate = "2050-01-01" if maxdate is None else maxdate
    # 日期检查
    assert len(re.findall('\d{4}-\d{2}-\d{2}', mindate + maxdate)) == 2, f'日期格式错误{mindate} {maxdate}'
    # 不包括最大值当天
    df = fetchDf(code, where=f"`日期`>='{mindate}' and `日期`<'{maxdate}'")
    return df


# 获取处理完成后的数据字典(某时前数量约束)
def fetchNumDf(code, num, dtime, ifnew=False) -> pd.DataFrame:
    assert len(re.findall('\d{4}-\d{2}-\d{2}', dtime)) == 1, f'日期格式错误{dtime}'
    if ifnew:
        df = fetchDf(code, where=f"`日期`>='{dtime}'",
                     other=f"order by `日期` ASC limit 0,{int(num)}")
    else:
        df = fetchDf(code, where=f"`日期`<'{dtime}'",
                     other=f"order by `日期` DESC limit 0,{int(num)}")
        df.sort_values(by='日期', ascending=True, inplace=True)
    return df


# 获取去突变数据组
def getRegularValues(df, v0=100, ifthree=False) -> list:
    df = df.fillna(0)
    values = regular(df.loc[:, '涨跌幅'], v0=v0)
    if ifthree:
        valuedts = list()
        for i in range(len(values)):
            zdj = df.loc[i, '最低价']
            spj = df.loc[i, '收盘价']
            zgj = df.loc[i, '最高价']
            tempdt = {'zdj': values[i] * zdj / spj, 'spj': values[i], 'zgj': values[i] * zgj / spj}
            valuedts.append(tempdt)
        return valuedts
    return values


@retryFunc_args(ci=3, iftz=True, sleeptime=2)
def getNowDataMap(*codes) -> dict:
    spider = Httpx()
    url = f'https://hqm.stock.sohu.com/getqjson?code={",".join(f"cn_{code}" for code in codes)}'
    js = spider.get(url, ifjson=True)
    spider.close()
    return {code: js.get(f'cn_{code}', []) for code in codes}


# 计算有效目标日期
def target_day(date0, n):
    target_day = TimeTool(date0, gs='%Y-%m-%d')
    for i in range(n):
        target_day.next(1, if_replace=True)
        while not is_workday(target_day.to_datetime()) or target_day.to_datetime().isoweekday() > 5:
            target_day.next(1, if_replace=True)
    return target_day.to_txt()


# 判断是否为交易日
def isTradingDay():
    spider = Httpx()
    url = f'http://tool.bitefu.net/jiari/?d={getNowTime("%Y-%m-%d")}'
    index = spider.get(url)
    spider.close()
    return index == '0'
