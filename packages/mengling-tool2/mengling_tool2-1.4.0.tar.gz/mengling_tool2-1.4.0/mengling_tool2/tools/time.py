import calendar
import re
import time
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta


class TimeTool:
    def __init__(self, date: datetime or str or int or float, gs="%Y-%m-%d %H:%M:%S"):
        if type(date) is str:
            cdate = re.match('[0-9.]+', date)
            # 对时间戳字符串的识别
            if cdate and len(cdate.group(0)) in (10, 13, 14):
                date = (float(cdate.group(0)) / 1000) if len(cdate.group(0)) == 13 else float(cdate.group(0))
            else:
                ts = re.findall('\d{2}', date)
                assert len(ts) > 3, f'{date} 格式有误'
                year = ts.pop(0) + ts.pop(0)
                month = ts.pop(0)
                day = ts.pop(0)
                h = ts.pop(0) if len(ts) > 0 else '00'
                m = ts.pop(0) if len(ts) > 0 else '00'
                s = ts.pop(0) if len(ts) > 0 else '00'
                date = datetime.strptime(f'{year}-{month}-{day} {h}:{m}:{s}', "%Y-%m-%d %H:%M:%S")
        if type(date) in (int, float):
            date = datetime.fromtimestamp(date)
            # date = time.strftime(gs, timeArray)
        self.date = date
        self.gs = gs

    def _getMonDay(self, if_first, if_return_str):
        first_day, last_day = calendar.monthrange(self.date.year, self.date.mon)
        temp = TimeTool(date(year=self.date.year, month=self.date.mon, day=first_day if if_first else last_day),
                        self.gs)
        if if_return_str:
            return temp.to_txt()
        else:
            return temp

    def getMonFirstDay(self, if_return_str=False):
        return self._getMonDay(True, if_return_str)

    def getMonLastDay(self, if_return_str=False):
        return self._getMonDay(False, if_return_str)

    def next(self, dn, hn=0, mn=0, sn=0, monn=0, if_replace=False, ifreturn_str=True):
        temp = self.date + timedelta(days=dn, hours=hn, minutes=mn, seconds=sn)
        temp += relativedelta(months=monn)
        if if_replace:
            self.date = temp
            t = self
        else:
            t = TimeTool(temp, gs=self.gs)
        if ifreturn_str:
            return t.to_txt()
        else:
            return t

    def to_txt(self, gs=None) -> str:
        return self.date.strftime(gs if gs else self.gs)

    def to_datetime(self) -> datetime:
        return datetime.strptime(self.to_txt(), self.gs)

    def to_stamp(self) -> int:
        # 转换为时间戳
        return round(time.mktime(self.date.timetuple()))

    def isoweekday(self) -> int:
        return self.date.isoweekday()

    def __str__(self):
        return self.to_txt()

    # 相加重载
    def __add__(self, day: int) -> str:
        return self.next(day)

    def _other_class(self, other):
        if type(other) in (str, int, float):
            other = TimeTool(other).date
        elif type(other) == datetime:
            pass
        else:
            other = other.date
            # raise ValueError(f'{type(other)} 类型错误!')
        return other

    # 相减重载
    def __sub__(self, other) -> float:
        return (self.date - self._other_class(other)).total_seconds()

    # 重载大于等于
    def __ge__(self, other) -> bool:
        return self.date >= self._other_class(other)

    # 重载大于
    def __gt__(self, other) -> bool:
        return self.date > self._other_class(other)

    # 重载小于
    def __lt__(self, other) -> bool:
        return self.date < self._other_class(other)

    # 重载小于等于
    def __le__(self, other) -> bool:
        return self.date <= self._other_class(other)


def getNowTime(next_day=0, gs="%Y-%m-%d %H:%M:%S", ifreturn_str=True) -> TimeTool or str:
    t = TimeTool(datetime.now(), gs=gs)
    t.next(next_day, if_replace=True)
    if ifreturn_str:
        return t.to_txt()
    else:
        return t


# 获取时间戳
def getNowStamp() -> float:
    return time.time()


# 运行时间显示装饰器
def runTimeFunc(func):
    def temp(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print('方法', func.__name__, '运行时间：', round(time.time() - start, 6), '秒')
        return result

    return temp


# 获取时间区间
def getTimeSection(date: TimeTool or str or int or datetime, forward: int, backward: int,
                   ifget_str=True, re_gs='%Y-%m-%d') -> list:
    t = TimeTool(date, re_gs)
    results = list()
    for i in range(-forward, backward + 1):
        t.next(i, if_replace=True)
        if ifget_str:
            results.append(t.to_txt())
        else:
            results.append(t.to_datetime())
    return results


# 获取时间区间
def getDatels(start_date: TimeTool or str or int or datetime, end_date: TimeTool or str or int or datetime,
              gs='%Y-%m-%d', interval_day=1, interval_hour=0, ifget_str=True) -> list:
    ds = list()
    st = TimeTool(start_date, gs)
    et = TimeTool(end_date, gs)
    while st <= et:
        ds.append(st.to_txt() if ifget_str else st.to_datetime())
        st.next(interval_day, hn=interval_hour, if_replace=True)
    # 包含最后一天
    return ds


# 输出等待
def printWait(sleeptime):
    for i in range(sleeptime):
        print('\r剩余时间：%s 秒     ' % (sleeptime - i), end='')
        time.sleep(1)


# 计算年龄 周岁
def calculate_age(year, mon, day):
    today = date.today()
    return today.year - int(year) - ((today.month, today.day) < (int(mon), int(day)))


# 休息输出通知函数
def sleePrintTime(sleeptime: int, qz_txt='剩余时间'):
    for i in range(sleeptime):
        print(f'\r{qz_txt}：{sleeptime - i} 秒     ', end='')
        time.sleep(1)


# 获取某月最后一天
def getLastDay(year, mon, ifre_str=True, gs='%Y-%m-%d') -> TimeTool or str:
    firstDayWeekDay, monthRange = calendar.monthrange(year, mon)
    der = TimeTool(date(year=year, month=mon, day=monthRange), gs)
    if ifre_str:
        return der.to_txt()
    else:
        return der


# 秒数转时长
def secondToTime(s0: int, ifre_str=True) -> (int, int, int) or str:
    m, s = divmod(s0, 60)
    h, m = divmod(m, 60)
    if ifre_str:
        return "%02d时%02d分%02d秒" % (h, m, s)
    else:
        return h, m, s
