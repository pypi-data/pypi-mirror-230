import httpx
from .__superclass__ import Spider
import json


class Httpx(Spider):
    def __init__(self, http2=False, **kwargs):
        Spider.__init__(self, **kwargs)
        self.http2 = http2
        # 高级设置会出现代理不生效的情况
        self.proxies_func = lambda p: f"http://{p}" if p is not None else None
        self.spider = self.__getH__(self.proxies)

    def __getH__(self, proxies):
        self.proxies = proxies
        # 装载时调用
        proxies = self.proxies_func(proxies)
        return httpx.Client(proxies=proxies, http2=self.http2)

    def head(self, url, ifobj=False, **kwargs):
        kwargs['timeout'] = kwargs.get('timeout', self.timeout)
        kwargs['headers'] = kwargs.get('headers', self.headers)
        proxies = kwargs.pop('proxies', self.proxies)
        kwargs['proxies'] = self.proxies_func(proxies)
        if proxies == self.proxies:
            r = httpx.head(url, **kwargs)
        else:
            self.close()
            self.spider = self.__getH__(proxies)
            r = httpx.head(url, **kwargs)
        if ifobj:
            return r
        else:
            return r.status_code

    def get(self, url, ifobj=False, savepath=None, ifjson=False, **kwargs):
        kwargs['timeout'] = kwargs.get('timeout', self.timeout)
        kwargs['headers'] = kwargs.get('headers', self.headers)
        proxies = kwargs.pop('proxies', self.proxies)
        if proxies == self.proxies:
            # 不支持socks代理方式
            r = self.spider.get(url, **kwargs)
        else:
            self.close()
            self.spider = self.__getH__(proxies)
            r = self.spider.get(url, **kwargs)
        # 保存源代码
        if savepath is not None: self.save(url, r.text, savepath)
        if ifobj:
            return r
        else:
            if ifjson:
                return json.loads(r.text)
            else:
                return r.text

    def post(self, url, data=None, ifobj=False, savepath=None, ifjson=False, **kwargs):
        kwargs['timeout'] = kwargs.get('timeout', self.timeout)
        kwargs['headers'] = kwargs.get('headers', self.headers)
        proxies = kwargs.pop('proxies', self.proxies)
        if proxies == self.proxies:
            r = self.spider.post(url, data=data, **kwargs)
        else:
            self.close()
            self.spider = self.__getH__(proxies)
            r = self.spider.post(url, data=data, **kwargs)
        # 保存源代码
        if savepath is not None: self.save(url, r.text, savepath)
        if ifobj:
            return r
        else:
            if ifjson:
                return json.loads(r.text)
            else:
                return r.text
