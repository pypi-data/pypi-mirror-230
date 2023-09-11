from math import inf
from .__selenium__.init import *
from .__selenium__.open import *
from .__selenium__.wait import *
from .__selenium__.operation import *
from .__selenium__.get import *
from selenium.webdriver.common.keys import Keys


# 使用相对导入的py文件不能作为启动文件
class ChromeDriver(webdriver.Chrome):
    # 默认代理文本:  代理方式://ip:porn
    # socks5://192.168.3.2:1080
    def __init__(self, ifchromium=False, custom_cd_cm: tuple = None, proxies=None, min_window=False,
                 max_window=False, headless=False, minload=False, ifiphone=False, timeout=15,
                 datapath=None, user_agent=None, url=None, getnum=inf,
                 chrome_version='90', **kwargs):
        # 初始化
        chrome_init(self, ifchromium=ifchromium, proxies=proxies, min_window=min_window, max_window=max_window,
                    headless=headless, minload=minload, ifiphone=ifiphone, datapath=datapath, custom_cd_cm=custom_cd_cm,
                    user_agent=user_agent, url=url, getnum=getnum, chrome_version=chrome_version, timeout=timeout)

    def newGet(self, url):
        return newGet(self, url)

    def neWindowGet(self, url):
        return neWindowGet(self, url)

    def addCookies(self, *cookies, iftz=True):
        return addCookies(self, cookies, iftz)

    def request_get(self, url):
        return request_get(self, url)

    def request_post(self, url, data):
        return request_post(self, url, data)

    def getWaitElement(self, constraint, timeout=10, ifassert=True):
        return getWaitElement(self, constraint, timeout=timeout, ifassert=ifassert)

    def getWaitElements(self, constraint, minnum=1, timeout=15):
        return getWaitElements(self, constraint, minnum=minnum, timeout=timeout)

    def runWaitElement(self, xpath, func, *args, **kwargs):
        return runWaitElement(self, xpath, func, *args, **kwargs)

    def getUserAgent(self):
        return getUserAgent(self)

    # 模拟清空
    def keyClear(self, xpath, timeout=15):
        e = self.getWaitElement(xpath, timeout=timeout)
        return keyClear(e)

    # 模拟输入
    def keyin(self, xpath, txt, timeout=15, ifclear=False, backspace_num=0):
        e = self.getWaitElement(xpath, timeout=timeout)
        act = ActionChains(self)
        act.move_to_element(e).click().perform()
        if ifclear:
            if backspace_num > 0:
                [self.keyin(xpath, Keys.BACK_SPACE) for i in range(backspace_num)]
            else:
                self.keyClear(xpath)
        return keyin(e, txt)

    # 模拟点击,直接调用js,需要使用唯一xapth,否则只取第一个元素
    def click(self, xpath, timeout=15):
        e = self.getWaitElement(xpath, timeout=timeout)
        act = ActionChains(self)
        act.move_to_element(e).click().perform()
        return  # click(self, xpath)

    # 选择下拉栏选项
    def select(self, xpath, value_text):
        e = self.getWaitElement(xpath)
        return select(e, value_text)

    # 模拟浏览器下滑至底部
    def scroll(self, maxwaitime=15, speed=1000):
        return scroll(self, maxwaitime=maxwaitime, speed=speed)

    # 跳至浏览器底部
    def goDown(self):
        return goDown(self)

    # 跳至浏览器顶部
    def goUp(self):
        return goUp(self)

    # 移除所有指定标签
    def removeAllTags(self, *tagnames):
        return removeAllTags(self, *tagnames)

    def slideDragAction(self, button_xpath, x):
        e = self.getWaitElement(button_xpath)
        return slideDragAction(e, x)

    # 跳转嵌套页面
    def changeFrame(self, xpath='//iframe'):
        e = self.getWaitElement(xpath)
        return changeFrame(self, e)

    # 跳转至最外层页面
    def parentFrame(self):
        return parentFrame(self)

    def closeAll(self):
        # 可能涉及到cookie问题需要调用close方法才行
        self.close()
        # time.sleep(1)
        self.quit()

    def getLocalStorage(self):
        return getLocalStorage(self)

    # 获取元素坐标
    def getElementPosition(self, xpath) -> tuple:
        self.getWaitElement(xpath)
        return getElementPosition(self, xpath)

    def getCookie_str(self) -> str:
        return getCookie_str(self)

    def switchWindow(self, index):
        return switchWindow(self, index)

    def closeOtherWindow(self):
        return closeOtherWindow(self)


# 使用相对导入的py文件不能作为启动文件
class FirefoxDriver(webdriver.Firefox):
    # 默认代理文本:  代理方式://ip:porn
    # socks5://192.168.3.2:1080
    def __init__(self, proxies=None, min_window=False,
                 max_window=False, headless=False, minload=False, ifiphone=False,
                 datapath=None, user_agent=None, url=None, getnum=inf, **kwargs):
        # 初始化
        firefox_init(self, proxies=proxies, min_window=min_window, max_window=max_window,
                     headless=headless, minload=minload, ifiphone=ifiphone, datapath=datapath,
                     user_agent=user_agent, url=url, getnum=getnum)

    def newGet(self, url): return newGet(self, url)

    def addCookies(self, *cookies, iftz=True): return addCookies(self, cookies, iftz)

    def request_get(self, url): return request_get(self, url)

    def request_post(self, url, data): return request_post(self, url, data)

    def getWaitElement(self, constraint, timeout=10, ifassert=True):
        return getWaitElement(self, constraint, timeout=timeout, ifassert=ifassert)

    def getWaitElements(self, constraint, minnum=1, timeout=15):
        return getWaitElements(self, constraint, minnum=minnum, timeout=timeout)

    def runWaitElement(self, xpath, func, *args, **kwargs):
        return runWaitElement(self, xpath, func, *args, **kwargs)

    def getUserAgent(self): return getUserAgent(self)

    # 模拟清空
    def keyClear(self, xpath):
        e = self.getWaitElement(xpath)
        return keyClear(e)

    # 模拟输入
    def keyin(self, xpath, txt):
        e = self.getWaitElement(xpath)
        return keyin(e, txt)

    # 模拟点击,直接调用js,需要使用唯一xapth,否则只取第一个元素
    def click(self, xpath): return click(self, xpath)

    # 选择下拉栏选项
    def select(self, xpath, value_text):
        e = self.getWaitElement(xpath)
        return select(e, value_text)

    # 模拟浏览器下滑至底部
    def scroll(self, maxwaitime=30, speed=500): return scroll(self, maxwaitime=maxwaitime, speed=speed)

    # 跳至浏览器底部
    def goDown(self): return goDown(self)

    # 跳至浏览器顶部
    def goUp(self): return goUp(self)

    # 移除所有指定标签
    def removeAllTags(self, *tagnames): return removeAllTags(self, *tagnames)

    def slideDragAction(self, button_xpath, x):
        e = self.getWaitElement(button_xpath)
        return slideDragAction(e, x)

    # 跳转嵌套页面
    def changeFrame(self, xpath='//iframe'):
        e = self.getWaitElement(xpath)
        return changeFrame(self, e)

    # 跳转至最外层页面
    def parentFrame(self): return parentFrame(self)
