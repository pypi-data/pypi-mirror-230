import time
import traceback
from threading import Lock, Thread
from ..tools.time import getNowTime
from ..tools.goodlib import ThreadGoods
from ..database_tool2.redis import RedisExecutor
from ..spider_tools.spiders.httpSession import HttpSession
from ..tools.notice import emailSend, customize_emailSend, Sender


# 雷达
class Radar:
    def __init__(self, r_index, **r_connect):
        self.good = ThreadGoods([RedisExecutor, {'dbindex': r_index, **r_connect}])
        # 参数字典记录
        self.mapdt = dict()
        self.lock = Lock()

    # 映射方法及链接组
    def mapping(self, name0, cycle, spider_urlss_getDatasfunc_title_links, *urls,
                spider_mode=HttpSession, spider_config: dict = None,
                errorsleeptime=600, ifirst_email=False, tztool_sender: Sender = None,
                emails: list = ('1321443305@qq.com',)):
        spider_config = {} if spider_config is None else spider_config
        name = f'雷达探测-{name0}'
        assert name not in self.mapdt.keys(), f'{name0} 已存在重复名称!'
        self.mapdt[name] = {
            'ifirst_email': ifirst_email,
            'func': spider_urlss_getDatasfunc_title_links,
            'urls': urls, 'emails': emails, 'sender': tztool_sender,
            'sleeptime': 0, 'cycle': cycle, 'errorsleeptime': errorsleeptime,
            'spider_mode': spider_mode, 'spider_config': spider_config,
        }

    def emailSend(self, sender, *args, **kwargs):
        with self.lock:
            error = None
            for i in range(3):
                try:
                    if sender:
                        customize_emailSend(sender, *args, **kwargs)
                    else:
                        emailSend(*args, **kwargs)
                    error = None
                    break
                except:
                    error = traceback.format_exc()
            if error: raise ValueError(error)

    def __run_one__(self, name):
        dt = self.mapdt[name]
        spider = dt['spider_mode'](**dt['spider_config'])
        b = False
        r = self.good.getThreadGood()
        # 重置redis状态
        r.delete(name, f'{name}_error')
        while True:
            for i in range(dt['sleeptime']):
                dt['sleeptime'] -= 1
                time.sleep(1)
            # 重置状态
            temps = list()
            try:
                # 执行一次
                title_links = dt['func'](spider, *dt['urls'])
                for title, link in title_links:
                    k = f'{title}\n{link}'
                    if not r.sismember(name, k):
                        r.sadd(name, k)
                        temps.append((title, link))
                if len(temps) > 0:
                    # 控制第一次是否发送
                    if b or dt['ifirst_email']:
                        self.emailSend(dt['sender'], name, temps, ifhtml=True, mane_mails=dt['emails'])
                    else:
                        b = True
                dt['sleeptime'] = dt['cycle']
            except:
                error = traceback.format_exc()
                # 将记录值取出
                if len(temps) > 0: r.srem(name, *[f'{title}\n{link}' for title, link in temps])
                r.set(f'{name}_error', f'{getNowTime(gs="%Y/%m/%d %H:%M:%S")}\n{error}')
                dt['sleeptime'] = dt['errorsleeptime']

    def run(self):
        for name in self.mapdt.keys():
            t = Thread(target=self.__run_one__, args=(name,))
            t.setDaemon(True)
            t.start()
        txts = list()
        # 信息显示
        while True:
            time.sleep(1)
            txts.clear()
            for name, dt in self.mapdt.items():
                txts.append(f"{name.replace('雷达探测-', '')}: {dt['sleeptime'] if dt['sleeptime'] > 0 else '正在执行'} ")
            retxt = "/".join(txts)
            print(f'\r{retxt}                  ', end='')
