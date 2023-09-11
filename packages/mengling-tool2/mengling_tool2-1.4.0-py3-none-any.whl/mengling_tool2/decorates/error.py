import traceback


# 捕获装饰器方法
def tryFunc_args(iftz=True, except_return_value=None):
    def temp(func):
        def temp_ch(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except:
                if iftz:
                    traceback.print_exc()
                return except_return_value

        return temp_ch

    return temp
