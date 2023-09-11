import time
from PIL import Image
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
import traceback

# 操作后等待元素变化
def runWaitElement(driver, xpath, func, *args, **kwargs):
    timeout = kwargs.get('timeout', 30)
    locator = (By.XPATH, xpath)
    oldpage = WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator)).get_attribute("innerHTML")
    func(*args, **kwargs)
    # 等待时间
    for i in range(timeout):
        time.sleep(1)
        locator = (By.XPATH, xpath)
        newpage = WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator)) \
            .get_attribute("innerHTML")
        if newpage != oldpage: break


# 添加所有有效的cookies，提示无效的cookies
def addCookies(driver, cookies, iftz):
    for cookie in cookies:
        try:
            driver.add_cookie(cookie)
        except:
            if iftz:
                traceback.print_exc()
                print('[cookie无效]', cookie)
    driver.refresh()


# 模拟清空
def keyClear(e): e.clear()


# 模拟输入
def keyin(e, txt):
    e.send_keys(txt)



# 模拟点击,直接调用js,需要使用唯一xapth,否则只取第一个元素
def click(driver, xpath):
    # driver.execute_script("document.getElementById('" + id + "').onlick")
    driver.execute_script(
        f'document.evaluate(\'{xpath}\', document, null, XPathResult.ANY_TYPE, null).iterateNext().click()')


# 选择下拉栏选项
def select(e, value_text):
    s = Select(e)
    s.select_by_visible_text(value_text)  # 通过文本


# 模拟浏览器下滑至底部
def scroll(driver, maxwaitime=30, speed=500):
    driver.execute_script(""" 
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
            } setTimeout(f, 500); })(); """ % speed)
    for i in range(maxwaitime):
        time.sleep(1)
        if not driver.execute_script('return window.wait;'): break


# 跳至浏览器底部
def goDown(driver):
    driver.execute_script(""" 
            (function () { 
                var y = document.body.scrollHeight; 
                window.scroll(0, y); 
                })(); """)


# 跳至浏览器顶部
def goUp(driver):
    driver.execute_script(""" 
            (function () { 
                var y = document.body.scrollHeight; 
                window.scroll(0, -y); 
                })(); """)


# 移除所有指定标签
def removeAllTags(driver, *tagnames):
    for tagname in tagnames:
        # 移除所有script
        driver.execute_script('''
                    var ss=document.getElementsByTagName("%s");
                    for(var i = ss.length-1; i >=0; i--){
                        ss[i].remove()}''' % tagname)


# 跳转嵌套页面
def changeFrame(driver, iframe_e):
    driver.switch_to.frame(iframe_e)  # 切换到iframe


# 跳转至最外层页面
def parentFrame(driver):
    driver.switch_to.default_content()


# 截图
def screenshot(driver, filepath):
    driver.get_screenshot_as_file(filepath)


# 获取验证码值
def saveYZM(driver, img_e, filepath='temp.png'):
    # 对验证码所在位置进行定位，然后截取验证码图片
    location = img_e.location
    size = img_e.size
    left = location['x']
    top = location['y']
    right = left + size['width']
    bottom = top + size['height']
    driver.save_screenshot(filepath)
    image_obj = Image.open(filepath).crop((left, top, right, bottom))
    image_obj.save(filepath)
    return filepath


def slideDragAction(e, x):
    # 找到滑块
    ActionChains(e).drag_and_drop_by_offset(e, x, 0).perform()


# 清空sessionStorage字典
def clearSessionStorage(driver):
    driver.execute_script("window.sessionStorage.clear();")


# 添加数据至sessionStorage字典
def addSessionStorage(driver, dt):
    for key in dt.keys():
        driver.execute_script("window.sessionStorage.setItem(arguments[0], arguments[1]);", key, dt[key])
