# 获取头文件信息
def getUserAgent(driver):
    return driver.execute_script("return navigator.userAgent")


# 判断页面内容是否为空
def ifNull(driver):
    txt = driver.page_source.strip()
    return txt == '<html><head></head><body></body></html>' or len(txt) == 0


# 获取LocalStorage字典
def getLocalStorage(driver) -> dict:
    return driver.execute_script('''
    var ls = window.localStorage, items = {}; 
    for (var i = 0, k; i < ls.length; ++i) 
      items[k = ls.key(i)] = ls.getItem(k); 
    return items; ''')


# 获取元素坐标
def getElementPosition(driver, xpath) -> tuple:
    dt = driver.execute_script(
        f'return document.evaluate("{xpath}", document, null, XPathResult.ANY_TYPE, null).iterateNext().getBoundingClientRect();')
    return (dt['x'], dt['y'])

def getCookie_str(driver)->str:
    return driver.execute_script('return document.cookie;')