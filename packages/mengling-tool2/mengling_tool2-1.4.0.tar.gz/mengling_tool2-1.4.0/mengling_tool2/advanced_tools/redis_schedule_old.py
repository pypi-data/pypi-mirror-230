import easygui
import json
import time
import traceback
from datetime import datetime
from multiprocessing import Process
from threading import Thread
from ..database_tool2.redis import RedisExecutor
from ..tools.notice import setSysPrint, defSysPrint, emailSend
from ..tools.time import TimeTool


def _getDate(t):
    return datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")


#
# # 获取调度器记录的变量字典
# def getTasKwg() -> dict:
#     return __getTasKwg__()


class RSchedule:
    def __init__(self, r_index, r_connect, r_name, iftz=True):
        self._r_index = r_index
        self._r_connect = r_connect
        self._r_name = r_name
        self._r_name_arg = f'{r_name}_arg'
        self._r_name_code = f'{r_name}_code'
        self._r_name_taskwg = f'{r_name}_taskwg'
        self._r_status = f'{r_name}_status'
        self._r_result = f'{r_name}_result'
        self._iftz = iftz

    def _getR(self):
        return RedisExecutor(self._r_index, **self._r_connect)

    # 执行开始
    def _ceil_start(self, sd, task_name, status, max_error_num, error_week) -> dict:
        sdt = _getDate(sd)
        if self._iftz: print(f"\x1b[33m{sdt} {task_name} 开始执行...\x1b[0m")
        with self._getR() as r:
            status['start_time'] = sdt
            status['end_time'] = ''
            status['next_time'] = ''
            status['td'] = sd + error_week
            status['fault_error_num'] = status.get('fault_error_num', max_error_num)
            status['status'] = '运行'
            r.hset(self._r_status, task_name, json.dumps(status, ensure_ascii=False))
            kwg = r.hget(self._r_name_taskwg, task_name)
            return json.loads(kwg) if kwg else {}

    # 执行结束
    def _ceil_end(self, exec_result, exec_error, exec_taskwg,
                  task_name, status, sd, week, error_week, max_error_num, emails):
        ed = time.time()
        edt = _getDate(ed)
        with self._getR() as r:
            if exec_result: r.hset(self._r_result, task_name, f'{edt}\n{exec_result}')
            status['end_time'] = edt
            # 变化
            if exec_error:
                r.hset(self._r_result, f'{task_name}_error', f'{edt}\n{exec_error}')
                status['fault_error_num'] -= 1
                status['status'] = '错误'
                status['td'] = ed + error_week
                status['next_time'] = _getDate(status['td'])
                status['last_running_seconds'] = ed - sd
            else:
                status['status'] = '等待'
                status['td'] = ed + week
                status['next_time'] = _getDate(status['td'])
                status['last_running_seconds'] = ed - sd
            # 消息通知
            if status['fault_error_num'] <= 0:
                status['fault_error_num'] = max_error_num
                emailSend(f'{self._r_name}-{task_name} 任务错误!', exec_error, mane_mails=emails)
            r.hset(self._r_status, task_name, json.dumps(status, ensure_ascii=False))
            r.hset(self._r_name_taskwg, task_name, json.dumps(exec_taskwg, ensure_ascii=False))
        if self._iftz:
            print(f"\x1b[{31 if exec_error else 32}m{edt} {task_name} {'出现错误-' if exec_error else ''}执行结束!\n"
                  f"执行时间:{status['last_running_seconds']:.4f}s"
                  f"\n下次执行:{status['next_time']}\x1b[0m")

    # 单任务执行,不能修改固定参数
    def _ceil(self, task_name, ml, week, error_week, max_error_num, emails, status):
        sd = time.time()
        __exec_taskwg__ = self._ceil_start(sd, task_name, status, max_error_num, error_week)
        ml = ml.replace('\n', '\n    ')
        setSysPrint(if_clear=False)
        try:
            exec(f'''
import traceback,sys
__ml_exec_error__ = None
try:
    {ml}
except:
    __ml_exec_error__=traceback.format_exc()
__ml_exec_result__ = sys.stdout.content
            '''.strip())
            ml_error = None
        except:
            ml_error = traceback.format_exc()
        defSysPrint()
        # 从当前命名空间中获取对象,键名与赋值的变量名需要不同
        ml_result = locals().get("__ml_exec_result__")
        ml_error = ml_error if ml_error else locals()["__ml_exec_error__"]
        self._ceil_end(ml_result, ml_error, __exec_taskwg__, task_name, status, sd,
                       week, error_week, max_error_num, emails)

    # 一次周期
    def _week(self):
        # notes = []
        with self._getR() as r:
            for task_name, txt in r.hgetall(self._r_name_arg).items():
                try:
                    task_arg = json.loads(txt)
                    week = task_arg['week']
                    if_reload = task_arg['reload']
                    error_week = task_arg['error_week']
                    max_error_num = task_arg['max_error_num']
                    emails = task_arg['emails']
                    exe = r.hget(self._r_name_code, task_name)
                    assert exe, f'{task_name} 没有对应代码!'
                    task_status = r.hget(self._r_status, task_name)
                    if not task_status: task_status = '{}'
                    task_status = json.loads(task_status)
                    # notes.append(f'{task_name}:{task_status.get("status", "等待")}')
                    nd = time.time()
                    if task_status.get('td', 0) <= nd:
                        # 判断任务执行卡住的情况
                        if task_status.get('next_time', 1):
                            # 多进程或多线程运行
                            func = Process if if_reload else Thread
                            t = func(target=self._ceil,
                                     args=(task_name, exe, week, error_week, max_error_num, emails, task_status))
                            t.daemon = True
                            t.start()
                        else:
                            emailSend(f'{self._r_name}-{task_name} 任务警告!',
                                      f'任务执行时间过长!\ntask_arg:{task_arg}\ntask_status:{task_status}',
                                      mane_mails=emails)
                            # 通知时间下移
                            task_status['td'] = nd + error_week
                            r.hset(self._r_status, task_name, json.dumps(task_status, ensure_ascii=False))
                except:
                    print(task_name, '错误!')
                    traceback.print_exc()
        # print('\r' + '/'.join(notes), end='')

    def run(self, sleep_time=1, if_init=True):
        with self._getR() as r:
            if if_init:
                print('重置结果及状态字典')
                r.delete(self._r_status, self._r_result)
            names = r.hkeys(self._r_name_arg)
            print(f'当前记录任务:{names}')
        print(_getDate(time.time()))
        print(f'周期任务开始...间隔时间{sleep_time}s')
        while True:
            self._week()
            time.sleep(sleep_time)

    # 记录任务
    def saveTask(self, task_name, week: int, max_error_num: int, error_week,
                 py_path: str = None, if_replace=False, emails=None, reload=False):
        if not py_path:
            py_path = easygui.fileopenbox()
        with open(py_path, mode='r', encoding='utf-8') as file:
            ml = file.read().strip()
        with self._getR() as r:
            if r.hget(self._r_name_arg, task_name):
                if if_replace:
                    print(task_name, '已替换')
                else:
                    raise ValueError(task_name, '已存在!')
            arg = {'week': week,
                   'error_week': error_week,
                   'reload': reload,
                   'max_error_num': max_error_num,
                   'emails': emails if emails else ['1321443305@qq.com'],
                   }
            r.hset(self._r_name_arg, task_name, json.dumps(arg, ensure_ascii=False))
            r.hset(self._r_name_code, task_name, ml)
