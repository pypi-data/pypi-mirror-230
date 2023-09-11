import requests_html
from .__superclass__ import Spider
import json

# 含有渲染功能
# requests_html支持异步请求
class HttpSession(Spider):
    def __init__(self, ifrender=False, **kwargs):
        Spider.__init__(self, **kwargs)
        self.spider = requests_html.HTMLSession()
        # 是否输出为渲染后的结果
        self.ifrender = ifrender
        self.proxies_func = lambda p: {'https': f'http://{p}', 'http': f'http://{p}'}

    def get(self, url, ifobj=False, savepath=None, ifjson=False, **kwargs):
        kwargs['timeout'] = kwargs.get('timeout', self.timeout)
        kwargs['headers'] = kwargs.get('headers', self.headers)
        proxies = kwargs.get('proxies', self.proxies)
        if proxies is None:
            obj = self.spider.get(url, **kwargs)
        else:
            kwargs['proxies'] = self.proxies_func(proxies)
            obj = self.spider.get(url, **kwargs)
        # 渲染
        if self.ifrender:  obj.html.render()
        # 保存源代码
        if savepath is not None: self.save(url, obj.html.html, savepath)
        # 原始对象
        if ifobj:
            return obj
        else:
            txt = obj.text
            if ifjson:
                return json.loads(txt)
            else:
                return txt

    def post(self, url, data=None, ifobj=False, savepath=None, ifjson=False, **kwargs):
        kwargs['timeout'] = kwargs.get('timeout', self.timeout)
        kwargs['headers'] = kwargs.get('headers', self.headers)
        proxies = kwargs.get('proxies', self.proxies)
        if proxies is None:
            obj = self.spider.post(url, data, **kwargs)
        else:
            kwargs['proxies'] = self.proxies_func(proxies)
            obj = self.spider.post(url, data, **kwargs)
        # 渲染
        if self.ifrender:  obj.html.render()
        # 保存源代码
        if savepath is not None: self.save(url, obj.html.html, savepath)
        # 原始对象
        if ifobj:
            return obj
        else:
            txt = obj.text
            if ifjson:
                return json.loads(txt)
            else:
                return txt
