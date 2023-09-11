import requests
from .__superclass__ import Spider


class Session(Spider):
    def __init__(self, **kwargs):
        Spider.__init__(self, **kwargs)
        s = requests.session()
        c = requests.cookies.RequestsCookieJar()
        for i in kwargs.get('driver_cookies', []):  # 添加cookie到CookieJar
            c.set(i["name"], i["value"])
        s.cookies.update(c)  # 更新session里的cookie
        self.spider = s
        self.proxies_func = lambda p: {'https': f'http://{p}', 'http': f'http://{p}'}

    def get(self, url, ifobj=False, savepath=None, ifjson=False, **kwargs):
        kwargs['timeout'] = kwargs.get('timeout', self.timeout)
        kwargs['headers'] = kwargs.get('headers', self.headers)
        proxies = kwargs.get('proxies', self.proxies)
        if proxies is None:
            html = self.spider.get(url, **kwargs)
        else:
            kwargs['proxies'] = self.proxies_func(proxies)
            html = self.spider.get(url, **kwargs)
        # 保存源代码
        if savepath is not None: self.save(url, html.text, savepath)
        # 原始对象
        if ifobj:
            return html
        else:
            txt = html.text
            if ifjson:
                return json.loads(txt)
            else:
                return txt

    def post(self, url, data=None, ifobj=False, savepath=None, ifjson=False, **kwargs):
        kwargs['timeout'] = kwargs.get('timeout', self.timeout)
        kwargs['headers'] = kwargs.get('headers', self.headers)
        proxies = kwargs.get('proxies', self.proxies)
        if proxies is None:
            html = self.spider.post(url, data, **kwargs)
        else:
            kwargs['proxies'] = self.proxies_func(proxies)
            html = self.spider.post(url, data, **kwargs)
        # 保存源代码
        if savepath is not None: self.save(url, html.text, savepath)
        # 原始对象
        if ifobj:
            return html
        else:
            txt = html.text
            if ifjson:
                return json.loads(txt)
            else:
                return txt
