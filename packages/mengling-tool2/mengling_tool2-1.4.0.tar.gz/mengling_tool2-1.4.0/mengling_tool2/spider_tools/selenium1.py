import random
import time
import traceback
from math import inf
from PIL import Image
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options as Options_c
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait

# 默认代理文本:  代理方式://ip:porn
# socks5://192.168.3.2:1080
IP_PORN = None


class ChromeDriver(webdriver.Chrome):
    def __init__(self, **kwargs):
        ifchromium = kwargs.get('ifchromium', True)
        proxies = kwargs.get('proxies', IP_PORN)
        min_window = kwargs.get('min_window', False)
        max_window = kwargs.get('max_window', False)
        headless = kwargs.get('headless', False)
        minload = kwargs.get('minload', True)
        iphone = kwargs.get('iphone', False)
        no_javascript = kwargs.get('no_javascript', False)
        self.datapath = kwargs.get('datapath', None)
        user_agent = kwargs.get('user_agent', None)
        timeout = kwargs.get('timeout', 30)
        url = kwargs.get('url', None)  # 'chrome://version/'
        options = Options_c()
        if ifchromium:
            # chromedriver的绝对路径
            self.chromedriver_path = "D:/python39/chromium89/my_cdr.exe"
            self.chrome_path = 'D:/python39/chromium89/chrome.exe'
        else:
            # chromedriver的绝对路径
            self.chromedriver_path = "D:/python39/my_cdr.exe"
            self.chrome_path = None  # 则使用默认的谷歌浏览器
        # 最大打开数量,避免缓存过多
        self.getnum = kwargs.get('getnum', inf)

        if self.datapath:
            options.add_argument(r'--user-data-dir=' + self.datapath)
        # 设置代理
        if proxies is not None: options.add_argument(('--proxy-server=' + proxies))
        # 设置打开模式为非开发人员模式_无效
        # options.add_experimental_option('excludeSwitches', ['enable-automation'])
        if headless:
            options.add_argument("--headless")
        # 最低资源加载
        if minload:
            # 禁止加载img及css
            prefs = {"profile.managed_default_content_settings.images": 2,
                     'permissions.default.stylesheet': 2}
            if no_javascript: prefs['profile.managed_default_content_settings.javascript'] = 2
            options.add_experimental_option("prefs", prefs)
            options.add_argument('--disable-gpu')
            # options.add_argument("--disable-javascript")
            # options.add_argument('blink-settings=imagesEnabled=false')
        # 模拟手机端
        if iphone:
            user_agent = 'MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1'
        else:
            if user_agent is None:
                # 避免使用headless的头文件
                # 可能通过判断代理头不一致的方式反爬
                user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
                # user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36'
        options.add_argument('user-agent=' + user_agent)

        # # 语言默认英文
        # options.add_argument('lang=en_US')
        # 忽略私密链接
        options.add_argument('--ignore-certificate-errors')

        # options.add_argument('--user-data-dir=C:/Users/Administrator/AppData/Locol/Google/Chrome/User Data/temp')
        # options.add_experimental_option('excludeSwitches', ['enable-automation'])
        # 无痕模式，避免有缓存后无法显示内容
        # options.add_argument('--incognito')
        # # 隐藏测试
        # options.add_experimental_option('useAutomationExtension', False)
        # 初始化一个driver，并且指定chromedriver的路径
        if self.chrome_path is not None: options.binary_location = self.chrome_path

        # 设置打开模式为非开发人员模式,2021最新方式,多页面依然有效,且屏蔽上方提示栏
        options.add_experimental_option(
            "excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("disable-blink-features=AutomationControlled")

        webdriver.Chrome.__init__(self, executable_path=self.chromedriver_path, options=options)

        # 设置打开模式为非开发人员模式,需要先进一次网页才能生效
        # undefined
        self.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                        Object.defineProperty(navigator, 'webdriver', {
                          get: () => undefined
                        })
                      """})
        # 避免无头
        self.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                       Object.defineProperty(navigator, 'chrome', {
                         get: () => undefined
                       })
                     """})
        self.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                       Object.defineProperty(navigator, 'plugins', {
                         get: () => [1, 2, 3],
                       })
                     """})
        self.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                       Object.defineProperty(navigator, 'languages', {
                         get: () => ['zh-CN', 'zh'],
                       })
                     """})
        self.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                       Object.defineProperty(navigator, 'deviceMemory', {
                         get: () => 8
                       })
                     """})
        if min_window:
            self.minimize_window()  # 浏览器窗口最小化
        elif max_window:
            self.set_window_size(1920, 1080)
            self.maximize_window()  # 浏览器窗口最大化
        # 设置超时时间,超时后网页还是没有加载完成则抛出异常
        # self.set_page_load_timeout(timeout)
        # 需要先进一次网页非开发人员模式才能生效
        if url is not None: self.get(url)
        # 增加自身句柄列表
        self.hands = list(self.window_handles)

    # def quit(self):
    #     webdriver.Chrome.quit(self)
    # if self.datapath is not None:
    #     try:
    #         os.remove(self.datapath + '/BrowserMetrics')  # 删除文件
    #     except:
    #         pass

    # 添加所有有效的cookies，提示无效的cookies
    def addCookies(self, cookies, iftz=True):
        for cookie in cookies:
            try:
                self.add_cookie(cookie)
            except:
                if iftz: print('[cookie无效]', cookie)
        self.refresh()

    # 删除所有元素后重新打开连接
    # 此方法的新链接navigator为false
    def newGet(self, url):
        if self.getnum < 1: assert False, '已达到规定的最大请求数!建议关闭后重新开启'
        try:
            self.execute_script('document.getElementsByTagName("html")[0].remove()')
        except:
            pass
        try:
            self.get(url)
        except TimeoutException:  # 捕获超时异常
            print("已超时,强制跳出...")
        self.getnum -= 1

    # 发送get请求
    def request_get(self, url):
        self.execute_script("""
            var xhr = new XMLHttpRequest();
            xhr.open('GET', '%s', true);
            window.text=-1;
            xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
            xhr.onload = function () {
                window.text= this.responseText;
            };
            xhr.send();
        """ % url)

    # 发送post请求
    def request_post(self, url, data):
        if type(data) == dict:
            data = '&'.join(["{key}={value}".format(key=key, value=data[key]) for key in data.keys()])
        self.execute_script("""
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '%s', true);
            window.text=-1;
            xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
            xhr.onload = function () {
                window.text= this.responseText;
            };
            xhr.send(%s);
        """ % (url, data))

    # 等待获取发送后的返回值
    def wait_getResponse(self, maxci=60, mintime=0.5):
        for i in range(maxci):
            time.sleep(mintime)
            text = self.execute_script("return window.text;")
            if text is None:
                print("没有进行发送请求，无返回值")
                return ""
            if text != -1: return text;
        print('等待时间已过，没有获取到返回值...')
        return ""

    # 等待获取元素加载
    def getWaitElement(self, constraint, constraint_class='xpath', timeout=10, onetime=0.2,
                       ifassert=True) -> WebElement:
        if constraint_class == 'xpath':
            constraint_class = By.XPATH
        elif constraint_class == 'id':
            constraint_class = By.ID
        elif constraint_class == 'class':
            constraint_class = By.CLASS_NAME
        elif constraint_class == 'tag':
            constraint_class = By.TAG_NAME
        else:
            assert False, 'constraint_class 约束类型出错，该元素等待方法无效！'
        try:
            e = WebDriverWait(self, timeout, onetime).until(
                EC.presence_of_element_located((constraint_class, constraint)))
        except:
            if ifassert:
                assert False, traceback.print_exc()
            else:
                e = None
        time.sleep(0.5)
        return e

    # 等待获取全部元素加载
    ##此方法不建议直接使用用于获取元素,获取元素最好用lxml获取
    def getWaitElements(self, constraint, constraint_class='xpath', minnum=1, timeout=15, onetime=0.5) -> list:
        if constraint_class == 'xpath':
            constraint_class = By.XPATH
        elif constraint_class == 'id':
            constraint_class = By.ID
        elif constraint_class == 'class':
            constraint_class = By.CLASS_NAME
        elif constraint_class == 'tag':
            constraint_class = By.TAG_NAME
        else:
            assert False, 'constraint_class 约束类型出错，该元素等待方法无效！'
        es = []
        nowtimeout = timeout
        while len(es) < minnum:
            assert nowtimeout >= 0, '等待时间过长，仅发现%s个元素' % len(es)
            time.sleep(onetime)
            es = WebDriverWait(self, timeout, onetime).until(
                EC.presence_of_all_elements_located((constraint_class, constraint)))
            nowtimeout -= onetime
        return es

    def xpathJsActin(self, xpath, actionfunc: str):
        return self.execute_script(
            'document.evaluate(\'%s\', document, null, XPathResult.ANY_TYPE, null).iterateNext().%s()' % (
                xpath, actionfunc))

    # 等待元素全部加载完成
    def waitElements(self, xpath_str, minnum=1, timeout=30, onetime=0.5):
        locator = ('xpath', xpath_str)
        es = []
        nowtimeout = timeout
        while len(es) < minnum:
            assert nowtimeout >= 0, '等待时间过长，仅发现%s个元素' % len(es)
            time.sleep(onetime)
            es = WebDriverWait(self, timeout, onetime).until(EC.presence_of_all_elements_located(locator))
            nowtimeout -= onetime

    # 操作后等待元素变化
    def runWaitElement(self, xpath, func, *args, **kwargs):
        timeout = kwargs.get('timeout', 30)
        locator = (By.XPATH, xpath)
        oldpage = WebDriverWait(self, timeout).until(EC.presence_of_element_located(locator)).get_attribute("innerHTML")
        func(*args, **kwargs)
        # 等待时间
        for i in range(timeout):
            time.sleep(1)
            locator = (By.XPATH, xpath)
            newpage = WebDriverWait(self, timeout).until(EC.presence_of_element_located(locator)).get_attribute(
                "innerHTML")
            if newpage != oldpage:
                break

    # 获取头文件信息
    def getUserAgent(self):
        return self.execute_script("return navigator.userAgent")

    # 重置driver,不关闭浏览器
    def resetDriver(self):
        len_old = len(self.window_handles)
        self.execute_script('window.open()')
        i = 10
        while len(self.window_handles) == len_old and i > 0:
            time.sleep(1)
            i -= 1
        assert i > 0, '重置失败!'
        self.close()
        self.switch_to.window(self.window_handles[-1])
        self.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                        Object.defineProperty(navigator, 'webdriver', {
                          get: () => false})"""}
                             )
        return self

    # 新建多个窗口,并打开对应链接,最多20个
    def neWindows(self, urls):
        assert 0 < len(urls) <= 20, '链接数最多有20个'
        # 计算需要新开的窗口数量
        newlen = max(len(urls) - len(self.window_handles), 0)
        # 在原窗口基础上在新建n个窗口
        for i in range(newlen):
            self.execute_script('window.open()')
            hands = self.window_handles
            self.switch_to.window(hands[-1])
            self.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                      get: () => false})
                  """})
        # 依次打开链接
        hands = self.window_handles
        for i in range(len(hands)):
            self.switch_to.window(hands[i])
            self.newGet(urls[i])

    # 不等待多开
    def neWindowGet(self, url):
        h1 = self.window_handles
        self.execute_script(f'window.open(\'{url}\')')
        h2 = self.window_handles
        h = (set(h2) - set(h1)).pop()
        self.close()
        self.switch_to.window(h)

    # 关闭其他窗口
    def closeOtherWindow(self):
        for hand in self.hands[1:]:
            self.switch_to.window(hand)
            self.close()
        self.hands = [self.hands[0]]
        self.switch_to.window(self.hands[0])

    # 切换窗口
    def switchWindow(self, index, ifmyhands=False):
        if ifmyhands:
            self.switch_to.window(self.hands[index])
        else:
            hands = self.window_handles
            self.switch_to.window(hands[index])

    # 判断页面内容是否为空
    def ifNull(self):
        txt = self.page_source.strip()
        return txt == '<html><head></head><body></body></html>' or len(txt) == 0

    # 模拟清空
    def keyClear(self, xpath):
        self.getWaitElement(xpath)
        self.find_element_by_xpath(xpath).clear()

    # 模拟输入
    def keyin(self, xpath, txt):
        self.getWaitElement(xpath)
        self.find_element_by_xpath(xpath).send_keys(txt)

    # 模拟点击,直接调用js,需要使用唯一xapth,否则只取第一个元素
    def click(self, xpath, timeout=15):
        # driver.execute_script("document.getElementById('" + id + "').onlick")
        self.getWaitElement(xpath, timeout=timeout)
        self.execute_script(
            f'document.evaluate(\'{xpath}\', document, null, XPathResult.ANY_TYPE, null).iterateNext().click()')

    # 选择下拉栏选项
    def select(self, element_xpath, value_text):
        e = self.find_element_by_xpath(element_xpath)
        s = Select(e)
        s.select_by_visible_text(value_text)  # 通过文本

    # 模拟浏览器下滑至底部
    def scroll(self, maxwaitime=30, speed=500):
        self.execute_script(""" 
            (function () { 
                window.wait=true;
                var y = document.documentElement.scrollTop; 
                var step = %s; 
                function f() { 
                    if (y <= document.body.scrollHeight) { 
                        y += step; 
                        window.scroll(0, y); 
                        setTimeout(f, 50); 
                    }
                    else { 
                        window.scroll(0, y); 
                        window.wait=false;
                    } 
                } 
                setTimeout(f, 500); 
            })(); 
            """ % speed)
        for i in range(maxwaitime):
            time.sleep(1)
            if not self.execute_script('return window.wait;'): break

    # 跳至浏览器底部
    def goDown(self):
        self.execute_script(""" 
                (function () { 
                    var y = document.body.scrollHeight; 
                    window.scroll(0, y); 
                    })(); 
                """)

    # 跳至浏览器顶部
    def goUp(self):
        self.execute_script(""" 
                (function () { 
                    var y = document.body.scrollHeight; 
                    window.scroll(0, -y); 
                    })(); 
                """)

    # 移除所有指定标签
    def removeAllTags(self, *tagnames):
        for tagname in tagnames:
            # 移除所有script
            self.execute_script('''
                        var ss=document.getElementsByTagName("%s");
                        for(var i = ss.length-1; i >=0; i--){
                            ss[i].remove()
                        }''' % tagname)

    # 跳转嵌套页面
    def changeFrame(self, **kwargs):
        xpath = kwargs.get('xpath', '//iframe')
        id = kwargs.get('id', None)
        class_ = kwargs.get('class_', None)
        if id is not None:
            iframe = self.find_element_by_id(id)
        elif class_ is not None:
            iframe = self.find_element_by_class(class_)
        else:
            iframe = self.find_element_by_xpath(xpath)
        self.switch_to.frame(iframe)  # 切换到iframe

    # 跳转至最外层页面
    def parentFrame(self):
        self.switch_to.default_content()

    # 截图
    def screenshot(self, filepath):
        self.get_screenshot_as_file(filepath)

    # 获取验证码值
    def saveYZM(self, img_xpath, filepath='temp.png'):
        # 对验证码所在位置进行定位，然后截取验证码图片
        img = self.getWaitElement(img_xpath)
        location = img.location
        size = img.size
        left = location['x']
        top = location['y']
        right = left + size['width']
        bottom = top + size['height']
        self.save_screenshot(filepath)
        image_obj = Image.open(filepath).crop((left, top, right, bottom))
        image_obj.save(filepath)
        return filepath

    def slideDragAction(self, button_xpath, x):
        # 找到滑块
        slider = self.find_element_by_xpath(button_xpath)
        ActionChains(self).drag_and_drop_by_offset(slider, x, 0).perform()

    def text(self, button_xpath, px):
        slider = self.find_element_by_xpath(button_xpath)
        action = ActionChains(self)
        action.click_and_hold(slider)
        sum = 0
        while sum < px:
            x = random.randint(20, 30)
            action.move_by_offset(sum, 0)
            # time.sleep((random.randint(1, 2)) / 10)
            sum += x
        action.release().perform()

    # 获取LocalStorage字典
    def getLocalStorage(self) -> dict:
        return self.execute_script('''
        var ls = window.localStorage, items = {}; 
        for (var i = 0, k; i < ls.length; ++i) 
          items[k = ls.key(i)] = ls.getItem(k); 
        return items; ''')

    # 清空LocalStorage字典
    def clearLocalStorage(self):
        self.execute_script("window.localStorage.clear();")

    # 添加数据至LocalStorage字典
    def addLocalStorage(self, dt):
        for key in dt.keys():
            self.execute_script("window.localStorage.setItem(arguments[0], arguments[1]);", key, dt[key])

    # 获取sessionStorage字典
    def getSessionStorage(self) -> dict:
        return self.execute_script('''
        var ls = window.sessionStorage, items = {}; 
        for (var i = 0, k; i < ls.length; ++i) 
          items[k = ls.key(i)] = ls.getItem(k); 
        return items; ''')

    # 清空sessionStorage字典
    def clearSessionStorage(self):
        self.execute_script("window.sessionStorage.clear();")

    # 添加数据至sessionStorage字典
    def addSessionStorage(self, dt):
        for key in dt.keys():
            self.execute_script("window.sessionStorage.setItem(arguments[0], arguments[1]);", key, dt[key])

    def getCookie_txt(self, *webs):
        webs = set(webs)
        cookies = list()
        dts = self.get_cookies()
        for dt in dts:
            if dt['domain'] in webs:
                cookies.append(f'{dt["name"]}={dt["value"]}')
        cookie = '; '.join(cookies)
        return cookie
