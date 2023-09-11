import traceback
from ...data.make import encode
from ..functions.args_get import getFakeUserAgent


class Spider:
    def __init__(self, timeout=15, headers: dict = None, proxies: str = None,
                 cookie: str = None, user_agent: str = None,
                 ifrandom=False, **kwargs):
        self.timeout = timeout
        self.headers = headers if headers is not None else dict()
        user_agent_have = self.headers.pop('user-agent', '') + self.headers.pop('User-Agent', '')
        if user_agent is None:
            if ifrandom:
                # 使用随机头
                user_agent = getFakeUserAgent()
            else:
                if len(user_agent_have) > 0:
                    user_agent = user_agent_have
                else:
                    # 使用默认头
                    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
        self.headers['user-agent'] = user_agent
        if cookie is not None: self.headers['cookie'] = cookie
        self.proxies = proxies
        self.config = kwargs
        self.spider = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def get(self, url, ifobj=False, savepath=None, ifjson=False, **kwargs):
        pass

    def post(self, url, data=None, ifobj=False, savepath=None, ifjson=False, **kwargs):
        pass

    # 保存文件
    def save(self, url, result, savepath):
        try:
            with open(f'{savepath}/{encode(url)}.html', encoding='utf-8',
                      mode='w+') as file:
                file.write(result)
        except:
            traceback.print_exc()
            print(url, '\n保存文件失败!')

    # # 检查型获取
    # def checkGet(self, url, txt_checkfunc_b, **kwargs):
    #     txt = self.get(url, **kwargs)
    #     assert txt_checkfunc_b(txt), '不满足条件!'
    #     return txt

    def close(self):
        if self.spider:
            self.spider.close()
