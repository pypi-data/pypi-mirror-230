from selenium.common.exceptions import TimeoutException


# 删除所有元素后重新打开连接
# 此方法的新链接navigator为false
def newGet(driver, url):
    if driver.getnum < 1: assert False, '已达到规定的最大请求数!建议关闭后重新开启'
    try:
        driver.execute_script('document.getElementsByTagName("html")[0].remove()')
    except:
        pass
    try:
        driver.get(url)
    except TimeoutException:  # 捕获超时异常
        print("已超时,强制跳出...")
    driver.getnum -= 1


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
    for hand in self.window_handles[1:]:
        self.switch_to.window(hand)
        self.close()
    self.switch_to.window(self.window_handles[0])


# 切换窗口
def switchWindow(self, index):
    self.switch_to.window(self.window_handles[index])


# 发送get请求
def request_get(driver, url):
    driver.execute_script("""
           var xhr = new XMLHttpRequest();
           xhr.open('GET', '%s', true);
           window.text=-1;
           xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
           xhr.onload = function () {
               window.text= this.responseText;
           };  xhr.send();""" % url)


# 发送post请求
def request_post(driver, url, data):
    if type(data) == dict:
        data = '&'.join(["{key}={value}".format(key=key, value=data[key]) for key in data.keys()])
    driver.execute_script("""
           var xhr = new XMLHttpRequest();
           xhr.open('POST', '%s', true);
           window.text=-1;
           xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
           xhr.onload = function () {
               window.text= this.responseText;
           };xhr.send(%s); """ % (url, data))
