import requests
from .__superclass__ import Spider
import json

class Requests(Spider):
    def __init__(self, **kwargs):
        Spider.__init__(self, **kwargs)
        self.proxies_func = lambda p: {'https': f'http://{p}', 'http': f'http://{p}'}

    def head(self, url, ifobj=False, **kwargs):
        kwargs['timeout'] = kwargs.get('timeout', self.timeout)
        kwargs['headers'] = kwargs.get('headers', self.headers)
        proxies = kwargs.get('proxies', self.proxies)
        if proxies is None:
            r = requests.head(url, **kwargs)
        else:
            kwargs['proxies'] = self.proxies_func(proxies)
            r = requests.head(url, **kwargs)
        if ifobj:
            return r
        else:
            return r.status_code

    def get(self, url, ifobj=False, savepath=None, ifjson=False, **kwargs):
        kwargs['timeout'] = kwargs.get('timeout', self.timeout)
        kwargs['headers'] = kwargs.get('headers', self.headers)
        proxies = kwargs.get('proxies', self.proxies)
        if proxies is None:
            r = requests.get(url, **kwargs)
        else:
            kwargs['proxies'] = self.proxies_func(proxies)
            r = requests.get(url, **kwargs)
        # 保存源代码
        if savepath is not None: self.save(url, r.text, savepath)
        if ifobj:
            return r
        else:
            txt = r.text
            if ifjson:
                return json.loads(txt)
            else:
                return txt

    def post(self, url, data=None, ifobj=False, savepath=None, ifjson=False, **kwargs):
        kwargs['timeout'] = kwargs.get('timeout', self.timeout)
        kwargs['headers'] = kwargs.get('headers', self.headers)
        proxies = kwargs.get('proxies', self.proxies)
        if proxies is None:
            r = requests.post(url, data, **kwargs)
        else:
            kwargs['proxies'] = self.proxies_func(proxies)
            r = requests.post(url, data, **kwargs)
        # 保存源代码
        if savepath is not None: self.save(url, r.text, savepath)
        if ifobj:
            return r
        else:
            txt = r.text
            if ifjson:
                return json.loads(txt)
            else:
                return txt
