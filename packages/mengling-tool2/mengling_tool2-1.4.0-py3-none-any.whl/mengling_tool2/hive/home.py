import time, json
import traceback
from threading import Lock
from flask import Flask, request


def lockFunc(lock):
    def func(f):
        def temp(*args, **kwargs):
            lock.acquire()
            try:
                result = f(*args, **kwargs)
            except:
                traceback.print_exc()
                result = '', 400, []
            lock.release()
            return result

        return temp

    return func


class Hive:
    def __init__(self, port=4305):
        self.app = Flask(__name__)
        self.port = port
        self.lock = Lock()
        # 记录蜂后的任务,先来先后的顺序执行每个蜂后
        self.fhtaskdt = dict()
        # 正在执行的任务
        self.fh_name = None
        self.datast = set()
        self.makefunc_txt = None
        self.fh_config = None
        self.cellnum = None
        # 记录工蜂的情况
        self.gfdt = dict()
        self.gfdatadt = dict()

        # 蜂后登记
        @lockFunc(self.lock)
        @self.app.route('/fh/register', methods=['POST'])
        def fh_register():
            txt = request.form.to_dict()['data']
            dt = json.loads(txt)
            name = dt.get('fh_name')
            if self.fh_name == name:
                print(name, '蜂后已重连...')
                self.__loadFH__(**dt)
                return ''
            elif name is None:
                return '', 417, []
            else:
                if self.fh_name is None:
                    self.__loadFH__(**dt)
                else:
                    print(name, '蜂后加入队列...')
                    self.fhtaskdt[name] = dt
                return ''

        # 蜂后查询
        @lockFunc(self.lock)
        @self.app.route('/fh/check')
        def fh_check():
            name = request.args.get('fh_name')
            # 执行名字相同且预备池数量为空且没有工蜂在执行任务
            if self.fh_name == name:
                if len(self.datast) + len(self.gfdatadt) == 0:
                    # 开始下一个任务
                    fhname, dt = None, {'datas': []}
                    for fhname in self.fhtaskdt.keys():
                        dt = self.fhtaskdt.pop(fhname)
                        break
                    if fhname is not None:
                        self.__loadFH__(fhname, **dt)
                    return '0'
                else:
                    # 检查一遍超时工蜂情况
                    t = time.time()
                    num = len(self.datast)
                    for gf in list(self.gfdt.keys()):
                        gfdatas = self.gfdatadt.get(gf, [])
                        num += len(gfdatas)
                        # 超时30s则移除
                        if t - self.gfdt[gf] > 30:
                            self.datast.update(self.gfdatadt.pop(gf, []))
                            self.gfdt.pop(gf)
                            print(f'工蜂:{gf} 已超时!')
                    return str(num)
            else:
                return '-1'

        # 工蜂登记
        @lockFunc(self.lock)
        @self.app.route('/gf/register')
        def gf_register():
            name = request.args.get('gf_name')
            # 更新时间
            self.gfdt[name] = time.time()
            # 没有任务则加入任务
            if self.gfdatadt.get(name) is None and len(self.datast) > 0:
                datas = [self.datast.pop() for i in range(min(self.cellnum, len(self.datast)))]
                self.gfdatadt[name] = datas
                return json.dumps({'datas': datas, 'fh_config': self.fh_config, 'makefunc_txt': self.makefunc_txt})
            else:
                return '{}'

        # 工蜂完成
        @self.app.route('/gf/complete')
        def gf_complete():
            name = request.args.get('gf_name')
            self.gfdatadt.pop(name)
            return ''

    # 装载蜂后
    def __loadFH__(self, fh_name, datas, makefunc_txt, fh_config: dict = None, cellnum=10_0000):
        print(f'{fh_name} 蜂后任务开始,总数量:{len(datas)} 单位数量:{cellnum}')
        self.fh_name = fh_name
        self.datast = set(datas)
        self.makefunc_txt = makefunc_txt
        self.fh_config = fh_config if fh_config is not None else {}
        self.cellnum = cellnum

    def run(self):
        self.app.run(host='0.0.0.0', port=self.port)


if __name__ == '__main__':
    Hive(4305).run()
