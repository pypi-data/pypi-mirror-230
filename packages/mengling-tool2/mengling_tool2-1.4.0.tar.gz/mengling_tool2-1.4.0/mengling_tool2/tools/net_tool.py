import telnetlib
from threading import Lock, Thread
import traceback
import eventlet


def __thread_auto_run(arg_func, args, threadnum: int, ifwait=True):
    lock = Lock()
    args = list(args)
    length = len(args)

    def temp():
        while True:
            lock.acquire()
            if len(args) > 0:
                arg = args.pop(0)
                print(f'\r{length - len(args)}/{length}', end='')
            else:
                lock.release()
                break
            lock.release()
            try:
                arg_func(arg)
            except:
                traceback.print_exc()
                lock.acquire()
                args.append(arg)
                print(f'\r{length - len(args)}/{length}', end='')
                lock.release()

    ts = [Thread(target=temp) for i in range(threadnum)]
    [t.start() for t in ts]
    if ifwait: [t.join() for t in ts]


# ip端口是否连接
def ifPornOpen(ip: str, porn: int) -> bool:
    with telnetlib.Telnet() as server:
        try:
            server.open(ip, porn)
            return True
        except:
            return False


# 获取全部端口
def getAllPorns() -> list:
    return [i for i in range(1, 65536)]


# 获取全部开放端口
def getAllOpenPorns(ip: str, theadnum: int = 20, minp: int = 1, maxp: int = 65535, timeout=15) -> list:
    ls = list()
    lock = Lock()

    def temp(porn):
        eventlet.monkey_patch()  # 必须加这条代码
        with eventlet.Timeout(timeout, False):  # 设置超时时间为2秒
            if ifPornOpen(ip, porn):
                lock.acquire()
                ls.append(porn)
                print('\n开放端口:', porn)
                lock.release()
            return
        print('\n连接超时:', porn)

    __thread_auto_run(temp, [i for i in range(minp, maxp + 1)], theadnum)
    return ls
