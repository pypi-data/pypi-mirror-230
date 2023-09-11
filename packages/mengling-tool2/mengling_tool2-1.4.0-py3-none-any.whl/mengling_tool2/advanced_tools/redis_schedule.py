from .__redis_schedule__.run import Run, Arg
from .__redis_schedule__.save_task import SaveTask
import time
import sys
import json


#
# # 获取调度器记录的变量字典
# def getTasKwg() -> dict:
#     return __getTasKwg__()


class RSchedule(Run, SaveTask):
    def run(self, sleep_time=1, if_init=True):
        with self._getR() as r:
            if if_init:
                self.print('重置结果及状态字典')
                r.delete(self._r_status, self._r_result)
            run_tasks, stop_tasks = [], []
            for task_name, txt in r.hgetall(self._r_name_arg).items():
                arg = Arg(txt)
                if arg.stop:
                    stop_tasks.append(task_name)
                else:
                    run_tasks.append(task_name)
                r.hset(self._r_name_arg, task_name, json.dumps(arg.get(), ensure_ascii=False))
            self.print(f'当前运行任务:{run_tasks}')
            self.print(f'当前停止任务:{stop_tasks}')
        self.print(self._getNow())
        self.print(f'周期任务开始...间隔时间{sleep_time}s')
        while True:
            self._run()
            time.sleep(sleep_time)
