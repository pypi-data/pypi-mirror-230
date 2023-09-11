_SELECT = dict()


# 多项选择方法
def select_parent(name, key, *args, **kwargs):
    return _SELECT[name][key](*args, **kwargs)


# 多项选择装饰器用于注册
def selectFunc_child(name, key=None):
    assert not (_SELECT.get(name) and _SELECT[name].get(key)), f'{name} {key} 已存在!'

    def temp(func):
        _SELECT[name] = _SELECT.get(name, dict())
        _SELECT[name][key] = func
        return lambda *args, **kwargs: func(*args, **kwargs)

    return temp
