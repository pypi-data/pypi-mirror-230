import time
from traceback import format_exc


# 需设置参数
def retryFunc_args(name='', ci=3, sleeptime=5, sleepfunc=time.sleep, iftz=True):
    def retryFunc(func):
        def temp(*values, **kwargs):
            e = None
            for i in range(1, ci + 1):
                try:
                    return func(*values, **kwargs)
                except:
                    e = format_exc()
                    if iftz:
                        print(e)
                        print(name, '失败，正在重试...第', i, '次，休息', sleeptime, '秒')
                    if sleeptime > 0: sleepfunc(sleeptime)
            print('错误参数组：', values)
            raise ValueError(f'{e}\n重试全部失败，抛出错误')

        return temp

    return retryFunc



