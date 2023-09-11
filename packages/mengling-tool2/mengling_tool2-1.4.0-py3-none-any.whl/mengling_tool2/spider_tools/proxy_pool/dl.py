import json, time
import traceback
from threading import Thread, Lock
from . import webfunc
from ...tools.goodlib import ThreadDictGoods
from ...tools.progress import jdprint
from ...tools.thread import thread_auto_run
from ...database_tool2.redis import RedisExecutor
from ..functions.make import getHeaders_str
from ..functions.args_get import getFakeUserAgent
from ..spiders.httpx import Httpx

__dlfuncs__ = [
    webfunc.freeProxy01,
    webfunc.freeProxy02,
    webfunc.freeProxy03,
    webfunc.freeProxy04,
    webfunc.freeProxy05,
    webfunc.freeProxy06,
    webfunc.freeProxy07,
    webfunc.freeProxy08,
    webfunc.freeProxy10,
    webfunc.freeProxy12,
    webfunc.freeProxy14,
    webfunc.my_dl01,
    webfunc.my_dl02,
    webfunc.my_dl03,
    webfunc.qtdl,
]


def getWebIpdt():
    while True:
        for func in __dlfuncs__:
            try:
                ipdts = func()
                assert len(ipdts) > 0, f'{func} 返回数量为0!'
            except:
                # traceback.print_exc()
                continue
            for ipdt in ipdts:
                yield ipdt


ymx_headers = getHeaders_str('''
accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
accept-encoding: gzip, deflate, br
accept-language: zh-CN,zh;q=0.9
sec-ch-ua: "Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"
sec-ch-ua-mobile: ?0
sec-fetch-dest: document
sec-fetch-mode: navigate
sec-fetch-site: none
sec-fetch-user: ?1
upgrade-insecure-requests: 1
user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36
''')


class DL:
    def __init__(self, dbindex, name, connect, checkurl=None, checkweek=60, maxerrornum=1, min_ip_num=20, ifcheck=True):
        self.name = name
        self.goodt = ThreadDictGoods({'spider': [Httpx, {'headers': ymx_headers}],  #
                                      'r': [RedisExecutor, {'dbindex': dbindex, **connect}]})
        self.checkurl = checkurl
        # self.lock = Lock()
        self.ifcheck = ifcheck
        self.checkweek = checkweek
        self.maxerrornum = maxerrornum
        self.min_ip_num = min_ip_num
        # 记录非检查下的出错ip
        self.erroripst = set()
        self._lock = Lock()

    # 非检验错误通知
    def errorInform(self, ip):
        r = self.goodt.getThreadKeyGood('r')
        ipdt = json.loads(r.hget(self.name, ip))
        ipdt['error'] = ipdt.get('error', 0) + 1
        r.hset(self.name, ip, json.dumps(ipdt))

    # 非检验成功通知
    def sucInform(self, ip):
        r = self.goodt.getThreadKeyGood('r')
        ipdt = json.loads(r.hget(self.name, ip))
        ipdt['error'] = 0
        r.hset(self.name, ip, json.dumps(ipdt))

    # 验证方法
    def yz(self, ip) -> bool:
        spider = self.goodt.getThreadKeyGood('spider')
        try:
            spider.headers['user-agent'] = getFakeUserAgent()
            txt = spider.get(self.checkurl, proxies=ip)
            assert len(txt) > 10_0000
            # assert spider.get(self.checkurl, proxies=ip,ifobj=True).status_code == 200
            return True
        except:
            return False

    # 验证已有ip
    def checkHaveIps(self):

        def opition(ipdt_txt):
            r = self.goodt.getThreadKeyGood('r')
            ipdt = json.loads(ipdt_txt)
            error = ipdt.pop('error', 0)
            ip = ipdt['host']
            b = self.yz(ip)
            with self._lock:
                if not b:
                    error += 1
                    if error > self.maxerrornum:
                        r.hdel(self.name, ip)
                        jdprint('[删除]', ip)
                    else:
                        ipdt['error'] = error
                        r.hset(self.name, ip, json.dumps(ipdt))
                        jdprint(f'[错误{error}次]', ip)
                else:
                    ipdt['error'] = 0
                    ipdt['successful'] = ipdt.get('successful', 0) + 1
                    r.hset(self.name, ip, json.dumps(ipdt))
                    jdprint(f'[校验成功]', ip)
            self.goodt.delThreadKeyGood(iftz=False)

        r = self.goodt.getThreadKeyGood('r')
        while True:
            jdprint('开始检查...')
            with self._lock:
                ipdts = r.hvals(self.name)
            if self.ifcheck:
                # 自检查
                thread_auto_run(opition, ipdts, threadnum=5, if_error=False, iftz=False)
            else:
                for ipdt_txt in ipdts:
                    ipdt = json.loads(ipdt_txt)
                    if ipdt.get('error', 0) > self.maxerrornum:
                        with self._lock:
                            r.hdel(self.name, ipdt['host'])
                        jdprint('[删除]', ipdt['host'])
                        self.erroripst.add(ipdt['host'])
            time.sleep(self.checkweek)

    # 收集新ip
    def collect(self):
        ipit = getWebIpdt()

        def opition(ipdt):
            r = self.goodt.getThreadKeyGood('r')
            ip = ipdt['host']
            with self._lock:
                b = r.hexists(self.name, ip)
            if b:
                jdprint('[已存在]', ip)
            else:
                b = self.yz(ip)
                with self._lock:
                    if b and self.ifcheck:
                        r.hset(self.name, ip, json.dumps(ipdt))
                        jdprint('[新增]', ipdt)
                    elif self.ifcheck:
                        jdprint('[失败]', ip)
                    elif ip in self.erroripst:
                        jdprint('[失败ip]', ip)
                    else:
                        r.hset(self.name, ip, json.dumps(ipdt))
                        jdprint('[非检测新增]', ipdt)
            self.goodt.delThreadKeyGood(iftz=False)

        r = self.goodt.getThreadKeyGood('r')
        while True:
            with self._lock:
                iplen = r.hlen(self.name)
            if iplen < self.min_ip_num:
                jdprint(f'数量不足,开始收集{self.min_ip_num * 2}个...')
                ipdtags = [next(ipit) for i in range(self.min_ip_num * 2)]
                thread_auto_run(opition, ipdtags, threadnum=5, if_error=False, iftz=False)
            else:
                jdprint('数量已足够,收集进入休息...')
                time.sleep(self.checkweek / 2)

    def run(self):
        t1 = Thread(target=self.checkHaveIps)
        t1.start()
        t2 = Thread(target=self.collect)
        t2.start()
        t1.join()
        t2.join()

#
# if __name__ == '__main__':
#     # 参数
#     dbindex, name, connect = 14, '测试代理池', config.REDIS_CONNECT
#     maxerrornum = 1
#     min_ip_num = 30
#     ifcheck = True
#     checkweek = 60
#     checkurl = 'https://www.amazon.com/' if ifcheck else None
#
#     # 流程
#     DL(dbindex, name, connect, checkurl, maxerrornum=maxerrornum,
#        min_ip_num=min_ip_num, ifcheck=ifcheck, checkweek=checkweek).run()
