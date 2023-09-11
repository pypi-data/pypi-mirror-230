import json
import time
from datetime import datetime


def _getDate(td):
    return datetime.fromtimestamp(td).strftime("%Y-%m-%d %H:%M:%S")


# 任务状态类型
class Status:
    def __init__(self, txt: str, max_error_num: int):
        if txt:
            kwg = json.loads(txt)
        else:
            kwg = {}
        self._sd = None
        self._max_error_num = max_error_num
        self._status = kwg.get('status', '等待')
        self._td = kwg.get('td', time.time())
        self._start_time = kwg.get('start_time')
        self._end_time = kwg.get('end_time')
        self._fault_error_num = kwg.get('fault_error_num', max_error_num)
        self.last_running_seconds = kwg.get('last_running_seconds')
        self.next_time = kwg.get('next_time')

    def get(self) -> dict:
        return {
            'status': self._status,
            'start_time': self._start_time,
            'end_time': self._end_time,
            'next_time': self.next_time,
            'fault_error_num': self._fault_error_num,
            'last_running_seconds': self.last_running_seconds,
            'td': self._td,
        }

    def run(self, max_run_week):
        self._sd = time.time()
        self._start_time = _getDate(self._sd)
        self._end_time = None
        self.next_time = None
        self._td = self._sd + max_run_week
        self._status = '运行'
        return self._start_time

    def wait(self, week):
        ed = time.time()
        self._status = '等待'
        self._td = ed + week
        self.next_time = _getDate(self._td)
        self.last_running_seconds = ed - self._sd
        self._end_time = _getDate(ed)

    def error(self, error_week):
        ed = time.time()
        self._fault_error_num -= 1
        self._status = '错误'
        self._td = ed + error_week
        self.next_time = _getDate(self._td)
        self.last_running_seconds = ed - self._sd
        self._end_time = _getDate(ed)
        if self._fault_error_num <= 0:
            self._fault_error_num = self._max_error_num
            return True
        else:
            return False

    def timeout(self, max_run_week):
        # 通知时间下移
        self._td = time.time() + max_run_week

    def getStatus(self):
        if self._td <= time.time():
            if self._status == '运行':
                return '卡死'
            else:
                return '等待'
        else:
            return '运行'
