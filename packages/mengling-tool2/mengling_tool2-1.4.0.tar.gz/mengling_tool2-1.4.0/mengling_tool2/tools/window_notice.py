from win32api import MessageBox
from win32con import MB_OK, MB_OKCANCEL

# 弹窗通知
def windowTip(title, content, ifcancel=False):
    # 值为1或2
    return MessageBox(0, content, title, MB_OKCANCEL if ifcancel else MB_OK) == 1


# 弹窗警告
def windowWarning(title, content):
    return MessageBox(0, content, title, MB_OK) == 1


# 弹窗错误
def windowError(title, content):
    return MessageBox(0, content, title, MB_OK) == 1

