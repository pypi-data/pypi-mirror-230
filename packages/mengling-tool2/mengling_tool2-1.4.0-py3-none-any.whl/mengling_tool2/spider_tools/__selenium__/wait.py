import time
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


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
    if ifassert:
        e = WebDriverWait(self, timeout, onetime).until(
            EC.presence_of_element_located((constraint_class, constraint)))
    else:
        try:
            e = WebDriverWait(self, timeout, onetime).until(
                EC.presence_of_element_located((constraint_class, constraint)))
        except:
            e = None
    # time.sleep(0.5)
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
