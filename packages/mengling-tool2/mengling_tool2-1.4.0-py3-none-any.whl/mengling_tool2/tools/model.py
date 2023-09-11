import importlib
import types


# 重新加载当前导入的所有模块
def reloadAllModel():
    print(dir())
    for md in dir():
        if '__' not in md:
            print(md)
            print(types.ModuleType(md))
            importlib.reload(md)
