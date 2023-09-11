import time
import traceback
from threading import Lock, Thread
from ..tools.time import getNowTime
from ..tools.goodlib import ThreadGoods
from ..database_tool2.redis import RedisExecutor
from ..tools.notice import emailSend, customize_emailSend, Sender
import re


class _Wsdt:
    def __init__(self, func, args, kwargs, emails, sender, cycle, errsleept, if_beginrun, time_periods):
        self.func = func
        self.args = args if args else []
        self.kwargs = kwargs if kwargs else {}
        self.emails = emails
        self.sender = sender
        self.sleept = 0
        self.cycle = cycle
        self.errsleept = errsleept
        self.iferror = False
        self.if_beginrun = if_beginrun
        self.time_periods = time_periods
        self.status = '等待中'


# 周期任务
class WeekSchedule:
    def __init__(self, r_index, week_name='周期任务', **r_connect):
        self._good = ThreadGoods([RedisExecutor, {'dbindex': r_index, **r_connect}])
        # 参数字典记录
        self._mapdt = dict()
        self._lock = Lock()
        self.week_name = week_name

    # 映射方法及链接组
    def mapping(self, name, cycle, func, args: list = None, kwargs: dict = None,
                errorsleeptime=600, tztool_sender: Sender = None, if_beginrun=True,
                emails: list = ('1321443305@qq.com',),
                time_periods: tuple or list = (('00:00:00', '24:00:00'),)):
        assert name not in self._mapdt.keys(), f'{name} 已存在重复名称!'
        # 运行时间区间格式判断
        assert all((re.match('\d{2}:\d{2}:\d{2}$', tp[0])
                    and re.match('\d{2}:\d{2}:\d{2}$', tp[1])
                    and tp[0] < tp[1]) for tp in time_periods), '运行区间不满足格式或初始大于等于结束时间'
        self._mapdt[name] = _Wsdt(func, args, kwargs, emails, tztool_sender, cycle, errorsleeptime, if_beginrun,
                                  time_periods)

    def getWser(self, name) -> _Wsdt:
        return self._mapdt[name]

    def _sleep(self, wser):
        while wser.sleept > 0:
            wser.sleept -= 1
            wser.status = wser.sleept
            time.sleep(1)

    def __run_one__(self, name):
        wser = self.getWser(name)
        r = self._good.getThreadGood()
        # 重置redis状态
        r.delete(f'{self.week_name}_error')
        if not wser.if_beginrun:
            wser.status = f'初始休眠{wser.cycle}s'
            time.sleep(wser.cycle)
        while True:
            # 休眠判断
            while not any((tp[0] <= getNowTime(gs='%H:%M:%S') <= tp[1]) for tp in wser.time_periods):
                wser.status = '休眠中'
                time.sleep(10)
            try:
                wser.status = '执行中'
                # 执行一次,返回状态,字符串长度不超过10
                result = wser.func(*wser.args, **wser.kwargs)
                if result:
                    if type(result) != str:
                        result, rt = result
                    else:
                        # 默认休息3s
                        result, rt = result, 3
                    wser.status = f'{result[:10]}...' if len(result) > 10 else result
                    time.sleep(rt)
                wser.sleept = wser.cycle
                wser.iferror = False
            except:
                wser.status = '发生错误'
                error = traceback.format_exc()
                r.hset(f'{self.week_name}_error', name,
                       f'{getNowTime(gs="%Y/%m/%d %H:%M:%S")}\n{error}')
                wser.sleept = wser.errsleept
                # 再次出错发送邮件通知
                if wser.iferror:
                    wser.status = '发送邮件'
                    if wser.sender:
                        customize_emailSend(wser.sender, f'{self.week_name} 错误-{name}',
                                            error, mane_mails=wser.emails)
                    else:
                        emailSend(f'{self.week_name} 错误-{name}', error, mane_mails=wser.emails)
                wser.iferror = True
            self._sleep(wser)

    def run(self, all_note=True):
        for name in self._mapdt.keys():
            t = Thread(target=self.__run_one__, args=(name,))
            t.setDaemon(True)
            t.start()
        txts = list()
        # 信息显示
        while True:
            time.sleep(1)
            txts.clear()
            for name, wser in self._mapdt.items():
                txts.append(f"{name}: {wser.status}  ")
            if all_note:
                retxt = "/".join(txts)
                print(f'\r{retxt}                  ', end='')
            else:
                for txt in txts:
                    print(f'\r{txt}                  ', end='')
                    time.sleep(0.3)

