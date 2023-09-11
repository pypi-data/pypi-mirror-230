import func_timeout


# 超时机制装饰器
def timeoutRaise_func(timeout, ifraise=True, error_txt='执行超时!'):
    def temp0(func):
        def temp1(*args, **kwargs):
            @func_timeout.func_set_timeout(timeout)
            def temp2():
                return func(*args, **kwargs)

            try:
                return temp2()
            except func_timeout.exceptions.FunctionTimedOut as e:
                print(func, args, kwargs, error_txt)
                if ifraise:
                    raise e
            except Exception as e:
                raise e

        return temp1

    return temp0
