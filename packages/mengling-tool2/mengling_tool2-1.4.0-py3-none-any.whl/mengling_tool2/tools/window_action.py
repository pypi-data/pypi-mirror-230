from datetime import datetime
import os, time
import shutil
import psutil
import pyautogui
import win32api
import win32con
from dateutil import rrule


# 获取分辨率
def getResolvingPower():
    size = pyautogui.size()
    return size.width, size.height


# 鼠标移动至坐标
def mouse_moveto(x, y, duration=0.25):
    # 为none时保持当前位置不变
    pyautogui.moveTo(x, y, duration=duration, tween=pyautogui.easeInQuad)


# 相对位置移动
def mouse_move(dx=0, dy=0, duration=0.25):
    pyautogui.moveRel(dx, dy, duration=duration, tween=pyautogui.easeInQuad)


# 鼠标点击
def mouse_click(ifdown=True, ifup=True):
    if ifdown:
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.18)
    if ifup:
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


# 字符输入
def key_in(txt: str):
    for ch in txt:
        if '\u4e00' <= ch <= '\u9fff':
            assert False, '不能包含中文字符!'
        else:
            pass
    pyautogui.typewrite(txt)


# 按键动作
def key_action(ch: str, ifdown=True, ifup=True):
    if ifdown:
        pyautogui.keyDown(ch)
    time.sleep(0.18)
    if ifup:
        pyautogui.keyUp(ch)


# 按键动作-组合键
def key_actions(*chs):
    pyautogui.hotkey(*chs)  # 可以使用组合键


# 获取鼠标坐标
def getMousePosition():
    p = pyautogui.position()
    return p.x, p.y


# 实时获取鼠标坐标
def printMousePoint():
    p0 = None
    while True:
        p = getMousePosition()
        if p != p0:
            print(p)
            p0 = p
        time.sleep(0.25)


# 获取全部的pid信息
def getAllPids(ifhaveobj=True):
    pid_names = list()
    pids = psutil.pids()
    for pid in pids:
        p = psutil.Process(pid)
        if ifhaveobj:
            ls = [pid, p.name, p]
        else:
            ls = [pid, p.name]
        pid_names.append(ls)
    return pid_names


# 关闭指定的所有进程
def killAll(progressname):
    os.system(f'taskkill /f /im {progressname}')


def cleanSelenium():
    try:
        os.system('taskkill /f /im chromedriver.exe && taskkill /f /im chrome.exe')
    except:
        pass
    # 删除临时文件夹下的文件
    tempath = os.environ['LOCALAPPDATA'] + '\Temp'
    root, dirs, files = next(os.walk(tempath))
    for dir in dirs:
        chdir = f'{root}/{dir}'
        if 'scoped_dir' in chdir:
            shutil.rmtree(chdir)
            print('删除:', chdir)
        for chd in next(os.walk(chdir))[1]:
            if 'scoped_dir' in chd:
                shutil.rmtree(f'{chdir}/{chd}')
                print('删除:', f'{chdir}/{chd}')


def __order(order, timing: str = '0000-00-00 00:00:00', delay_time=0):
    if timing != '0000-00-00 00/00/00':
        date = datetime.strptime(timing, '%Y-%m-%d %H:%M:%S')
        date_now = datetime.now()
        sed = rrule.rrule(rrule.SECONDLY, dtstart=date_now, until=date).count()
    else:
        sed = 0
    sed += delay_time
    print('休息', sed, 's...')
    time.sleep(sed)
    os.system(order)


def lock_order(timing: str = '0000-00-00 00:00:00', delay_time=0):
    print('锁定!')
    __order('rundll32 user32.dll,LockWorkStation', timing=timing, delay_time=delay_time)


def reboot_order(timing: str = '0000-00-00 00:00:00', delay_time=0):
    print('重启!')
    __order('shutdown -r -f -t 0', timing=timing, delay_time=delay_time)


def shutdown_order(timing: str = '0000-00-00 00:00:00', delay_time=0):
    print('关机!')
    __order('shutdown -s -f -t 0', timing=timing, delay_time=delay_time)


if __name__ == '__main__':
    cleanSelenium()
