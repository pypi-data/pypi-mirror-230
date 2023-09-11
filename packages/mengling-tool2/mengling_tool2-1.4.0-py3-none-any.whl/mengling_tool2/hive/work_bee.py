from threading import Thread
import time
import traceback
import requests
from ..data.make import getRandomPassword
from ..decorates.retry import retryFunc_args


class Bee:
    def __init__(self, fc_ip: str, fc_port: int):
        # 生成随机名称
        self.gf_name = getRandomPassword(10)
        self.fc_url0 = f'http://{fc_ip}:{fc_port}'
        self.makefunc = None
        # 记录任务
        self.datas = []
        self.fh_config = {}
        self.sleep_time = 5

    # 登记
    def register(self):
        try:
            r = requests.get(self.fc_url0 + f'/gf/register?gf_name={self.gf_name}')
            dt = r.json()
            if len(dt) == 0:
                return None
            else:
                return dt['makefunc_txt'], dt.get('datas', []), dt.get('fh_config', {})
        except:
            traceback.print_exc()
            assert False, f'错误返回  {r.text}'

    # 提交完成
    def complete(self):
        # 提交完成
        requests.get(self.fc_url0 + f'/gf/complete?gf_name={self.gf_name}')

    # 监听链接
    def linsten(self):
        while True:
            # 请求
            try:
                result = self.register()
            except:
                traceback.print_exc()
                print('监听出错!')
                result = None
            if result is not None:
                func, self.datas, self.fh_config = result
                exec(func + '\nself.makefunc=makefunc')
            time.sleep(self.sleep_time)

    @retryFunc_args()
    def cellRun(self):
        print(f'开始任务...数量:{len(self.datas)}')
        try:
            self.makefunc(self.datas, **self.fh_config)
            self.datas = list()
        except:
            traceback.print_exc()
            print('[失败]')

    def run(self):
        # 开始监听
        print('开始监听:', self.fc_url0)
        Thread(target=self.linsten).start()
        while True:
            if len(self.datas) > 0:
                self.cellRun()
                self.complete()
            time.sleep(self.sleep_time)


if __name__ == '__main__':
    import config

    gbee = Bee(config.FC_CONNECT['fc_ip'], config.FC_CONNECT['fc_port'])
    gbee.run()
