import time
from appium.webdriver import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from appium import webdriver


class Appium(webdriver.Remote):
    def __init__(self, app_package, appactivity,
                 pversion='6.0.1', device_name='driver_name',
                 allyes_authority=True, no_reset=False,
                 link="http://localhost:4723/wd/hub", **kwargs):
        self.caps = {
            "platformVersion": pversion,
            "platformName": 'Android',
            "deviceName": device_name,
            "appPackage": app_package,
            "appActivity": appactivity,
            "autoGrantPermissions": allyes_authority,
            "noReset": no_reset,
            **kwargs
        }
        webdriver.Remote.__init__(self, link, self.caps)

    def getWaitElement(self, constraint, constraint_class='id', timeout=15) -> WebElement:
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
        e = WebDriverWait(self, timeout).until(EC.presence_of_element_located((constraint_class, constraint)))
        return e

    def getWaitElements(self, constraint, constraint_class='id', minnum=1, timeout=15, onetime=0.5) -> list:
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
