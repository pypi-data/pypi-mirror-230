import httplib2
from httplib2 import socks
from .__superclass__ import Spider
import re

httplib2.debuglevel = -1


class Httplib2(Spider):
    def __init__(self, **kwargs):
        Spider.__init__(self, **kwargs)
        self.spider = self.__getH__(self.proxies)

    def __getH__(self, proxies):
        self.proxies = proxies
        if proxies is None:
            h = httplib2.Http(timeout=self.timeout)
        else:
            ip, port = self.proxies.split(':')
            h = httplib2.Http(proxy_info=httplib2.ProxyInfo(socks.PROXY_TYPE_HTTP, ip, int(port)), timeout=self.timeout)
        return h

    def get(self, url, ifobj=False, savepath=None, ifjson=False, **kwargs):
        kwargs['timeout'] = kwargs.get('timeout', self.timeout)
        kwargs['headers'] = kwargs.get('headers', self.headers)
        proxies = kwargs.get('proxies', self.proxies)
        if proxies == self.proxies:
            response, content = self.spider.request(url, method='GET', headers=kwargs['headers'])
        else:
            self.close()
            self.spider = self.__getH__(proxies)
            response, content = self.spider.request(url, method='GET', headers=kwargs['headers'])
        # 保存源代码
        if savepath is not None: self.save(url, content.decode('utf-8'), savepath)
        if ifobj:
            return response
        else:
            try:
                bm = re.findall('charset=([0-9a-zA-Z-]+)', response.get('content-type'))[0]
            except:
                bm = 'utf-8'
            txt = content.decode(bm)
            if ifjson:
                return json.loads(txt)
            else:
                return txt

    def post(self, url, data=None, ifobj=False, savepath=None, ifjson=False, **kwargs):
        kwargs['timeout'] = kwargs.get('timeout', self.timeout)
        kwargs['headers'] = kwargs.get('headers', self.headers)
        proxies = kwargs.get('proxies', self.proxies)
        if type(data) == dict:
            data = '&'.join([f'{d}={data[d]}' for d in data.keys()])
        if proxies == self.proxies:
            response, content = self.spider.request(url, method='POST', body=data, headers=kwargs['headers'])
        else:
            self.close()
            self.spider = self.__getH__(proxies)
            response, content = self.spider.request(url, method='POST', body=data, headers=kwargs['headers'])
        # 保存源代码
        if savepath is not None: self.save(url, content.decode('utf-8'), savepath)
        if ifobj:
            return response
        else:
            try:
                bm = re.findall('charset=([0-9a-zA-Z-]+)', response.get('content-type'))[0]
            except:
                bm = 'utf-8'
            txt = content.decode(bm)
            if ifjson:
                return json.loads(txt)
            else:
                return txt
