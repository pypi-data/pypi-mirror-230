import time, re, json
import traceback
import requests
from ..decorates.retry import retryFunc_args


class Queen:
    def __init__(self, fh_name: str, fc_ip: str, fc_port: int, fh_config: dict, strdatas: list,
                 strs_kwarg_makefunc: str,
                 cellnum: int = 10_0000, sleep_time=10):
        self.fh_name = fh_name
        self.fc_url0 = f'http://{fc_ip}:{fc_port}'
        self.fh_config = fh_config
        self.datas = strdatas
        self.cellnum = cellnum
        self.makefunc_txt = strs_kwarg_makefunc.strip()
        self.sleep_time = sleep_time

    # 登记
    def register(self):
        print(self.fh_name, '蜂后登记...')
        r = requests.post(self.fc_url0 + '/fh/register',
                          data={'data': json.dumps(
                              {'fh_name': self.fh_name, 'datas': list(self.datas), 'makefunc_txt': self.makefunc_txt,
                               'fh_config': self.fh_config, 'cellnum': self.cellnum})})
        return r.status_code == 200

    # 检查完成情况
    def check(self):
        try:
            num = int(requests.get(self.fc_url0 + f'/fh/check?fh_name={self.fh_name}').text)
        except:
            traceback.print_exc()
            print('检查出现错误!')
            return False
        if num == -1:
            return False
        else:
            n, now = len(self.datas) - num, len(self.datas)
            print(f'\r进度：{n if n >= 0 else 0}/{now}', end='')
            return n == now

    @retryFunc_args()
    def run(self):
        # 检验代码格式
        assert re.match('^def makefunc\(', self.makefunc_txt) is not None
        assert self.register(), '登记蜂后失败,请重新运行!'
        print('登记成功!')
        print('数量：', len(self.datas))
        print('参数：', self.fh_config)
        time.sleep(self.sleep_time)
        while not self.check():
            time.sleep(self.sleep_time)
        print('任务全部完成!')


if __name__ == '__main__':
    txt = '''
    def makefunc(data, a=0):
        print('值:', data, '参数:', a)
        time.sleep(1)
    '''
    qbee = Queen('测试', '127.0.0.1', 4305, {'a': 1}, list(range(10000)), txt)
    qbee.run()
