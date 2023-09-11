# 缓存
class Cache:
    def __init__(self, datadt: dict = None):
        if datadt is None: datadt = dict()
        self.datadt = datadt

    def get(self, key, kwarg_getvalue_data, **kwargs):
        try:
            data = self.datadt[key]
        except:
            data = kwarg_getvalue_data(**kwargs)
            self.datadt[key] = data
        return data