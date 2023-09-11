from multiprocessing import Manager, Process
from concurrent.futures import ProcessPoolExecutor


# 获取进程同步管理对象
def getProcessManager():
    return Manager()


# 多进程
# 参数不能是自定义类型的实例对象，或者这种实例对象的方法
def process_run(func, argslist: list, ifwait=True):
    ns = []
    for args in argslist:
        n = Process(target=func, args=tuple(args))
        ns.append(n)
    [n.start() for n in ns]
    if ifwait: [n.join() for n in ns]


# 不好用，进程出错不会通知
# 进程池
def processPool(maxnum, func, argslist, onevalue=False):
    pool = ProcessPoolExecutor(max_workers=maxnum)
    ps = []
    for args in argslist:
        if onevalue:
            ps.append(pool.submit(func, args))  # 放入单值
        else:
            ps.append(pool.submit(func, *args))  # 执行多值
    # pools.map(func, *argslist)  # 维持执行的进程总数为num，当一个进程执行完毕后会开始执行排在后面的进程
    return pool, ps
