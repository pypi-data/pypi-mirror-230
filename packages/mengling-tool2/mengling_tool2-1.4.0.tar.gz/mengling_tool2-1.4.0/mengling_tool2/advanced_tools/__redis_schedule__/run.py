from .base.arg import Arg
from .base.status import Status
from .base.body import *


class _Ceil(Body):
    # 执行开始
    def _ceil_start(self, task_name, status: Status, max_run_week) -> dict:
        with self._getR() as r:
            sdt = status.run(max_run_week)
            if self._iftz: self.print(f"\x1b[33m{sdt} {task_name} 开始执行...\x1b[0m")
            r.hset(self._r_status, task_name, json.dumps(status.get(), ensure_ascii=False))
            kwg = r.hget(self._r_name_taskwg, task_name)
            return json.loads(kwg) if kwg else {}

    # 执行结束
    def _ceil_end(self, exec_result, exec_error, exec_taskwg,
                  task_name, status: Status, week, error_week, emails):
        edt = self._getNow()
        with self._getR() as r:
            if exec_result: r.hset(self._r_result, task_name, f'{edt}\n{exec_result}')
            # 变化
            if exec_error:
                r.hset(self._r_result, f'{task_name}_error', f'{edt}\n{exec_error}')
                ifemail = status.error(error_week)
                if ifemail: emailSend(f'{self._r_name}-{task_name} 任务错误!', exec_error, mane_mails=emails)
            else:
                status.wait(week)
            r.hset(self._r_status, task_name, json.dumps(status.get(), ensure_ascii=False))
            r.hset(self._r_name_taskwg, task_name, json.dumps(exec_taskwg, ensure_ascii=False))
        if self._iftz:
            self.print(f"\x1b[{31 if exec_error else 32}m{edt} {task_name} {'出现错误-' if exec_error else ''}执行结束!\n"
                       f"执行时间:{status.last_running_seconds:.4f}s"
                       f"\n下次执行:{status.next_time}\x1b[0m")

    # 单任务执行,不能修改固定参数
    def _ceil(self, task_name, ml, arg: Arg, status: Status):
        __exec_taskwg__ = self._ceil_start(task_name, status, arg.max_run_week)
        ml = ml.replace('\n', '\n    ')
        if arg.reload:
            self.pter = Printer()
            sys.stdout = self.pter
        try:
            exec(f'''
import traceback,sys
__ml_exec_error__ = None
try:
    {ml}
except:
    __ml_exec_error__=traceback.format_exc()
            '''.strip())
            ml_error = None
        except:
            ml_error = traceback.format_exc()
        # 从当前命名空间中获取对象,键名与赋值的变量名需要不同
        ml_result = self.pter.popContent()
        ml_error = ml_error if ml_error else locals()["__ml_exec_error__"]
        self._ceil_end(ml_result, ml_error, __exec_taskwg__, task_name, status,
                       arg.week, arg.error_week, arg.emails)


class Run(_Ceil):
    def __run(self, task_name, exe, task_arg: Arg, task_status: Status):
        # 多进程或多线程运行
        func = Process if task_arg.reload else Thread
        t = func(target=self._ceil,
                 args=(task_name, exe, task_arg, task_status))
        t.daemon = True
        t.start()

    # 一次周期
    def _run(self):
        with self._getR() as r:
            for task_name, txt in r.hgetall(self._r_name_arg).items():
                try:
                    task_arg = Arg(txt)
                    if task_arg.stop: continue
                    # 获取状态
                    task_status = Status(r.hget(self._r_status, task_name), task_arg.max_error_num)
                    # 判断执行
                    status = task_status.getStatus()
                    if status == '等待':
                        exe = r.hget(self._r_name_code, task_name)
                        assert exe, f'{task_name} 没有对应代码!'
                        self.__run(task_name, exe, task_arg, task_status)
                    elif status == '卡死':
                        emailSend(f'{self._r_name}-{task_name} 任务警告!',
                                  f'任务执行时间过长!\ntask_arg:{task_arg}\ntask_status:{task_status}',
                                  mane_mails=task_arg.emails)
                        task_status.timeout(task_arg.max_run_week)
                        r.hset(self._r_status, task_name, json.dumps(task_status.get(), ensure_ascii=False))
                except:
                    self.print(task_name, '错误!')
                    traceback.print_exc()
