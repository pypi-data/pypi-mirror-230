import easygui
import json
import time
import sys
import traceback
from datetime import datetime
from multiprocessing import Process
from threading import Thread
from mengling_tool2.database_tool2.redis import RedisExecutor
from mengling_tool2.tools.notice import emailSend
from mengling_tool2.tools.time import TimeTool
from threading import Lock, get_ident


# print捕获者
class Printer:
    def __init__(self):
        # self._lock = Lock()
        self.contendt = {}

    def popContent(self):
        tid = get_ident()
        content = self.contendt.get(tid, '')
        self.flush()
        return content

    def write(self, txt):
        tid = get_ident()
        if self.contendt.get(tid) is None: self.contendt[tid] = ''
        self.contendt[tid] += txt

    def flush(self):
        tid = get_ident()
        self.contendt[tid] = ''


class Body:
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
        self.pter = Printer()
        sys.stdout = self.pter

    def _getR(self):
        return RedisExecutor(self._r_index, **self._r_connect)

    def _getNow(self):
        return datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S")

    def print(self, *txts):
        sys.__stdout__.write(' '.join(txts) + '\n')
        sys.__stdout__.flush()
