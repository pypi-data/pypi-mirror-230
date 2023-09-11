import asyncio
import os
from pyppeteer import launch

from ..asynchronous_tool import getTasks, tasksRun

'''js_str可以为tag、#id.class、.class、#id等形式'''


##存在问题,暂不使用
async def __notRequest(page, classs):
    pass

    # await page.setRequestInterception(True)
    #
    # # 过滤图片等请求
    # async def intercept_request(req):
    #     """请求过滤"""
    #     if req.resourceType in classs:
    #         await req.abort()
    #     else:
    #         await req.continue_()
    #
    # async def intercept_response(res: Response):
    #     print('拦截到请求来源:%s' % res.url)
    #
    # # page.on('request', intercept_request)
    # page.on('response', intercept_response)


async def __setPage(page, no_javascript=False, iphone=False):
    # if min_window: ()  # 浏览器窗口最小化
    # 防止反爬虫检测
    # 以下为插入中间js，将淘宝会为了检测浏览器而调用的js修改其结果。
    await page.evaluateOnNewDocument('() =>{Object.defineProperties(navigator,{webdriver:{get: () => undefined}})}')
    # # 设置窗口尺寸
    await page.setViewport({'width': 1920, 'height': 1080})
    # 模拟手机端
    if iphone:
        await page.setUserAgent(
            "MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1")
    else:
        await page.setUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36")
    return page


# waitUntils = ['domcontentloaded', 'load', 'networkidle0', 'networkidle2']
# 访问网站page.goto(url,{'waitUntil': 'load'， 'timeout': 10000})
# page.close()
# 需要调用协程运行的方法才能使用
async def getPage(**kwargs):
    ip_porn = kwargs.get('ip_porn', None)
    # min_window = datadt.get('min_window', False)
    max_window = kwargs.get('max_window', False)
    headless = kwargs.get('headless', False)
    minload = kwargs.get('minload', True)
    iphone = kwargs.get('iphone', False)
    no_javascript = kwargs.get('no_javascript', False)
    datapath = kwargs.get('datapath', None)
    executablePath = kwargs.get('executablePath', 'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe')
    if not os.path.exists(executablePath): executablePath = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
    arglist = ['--enable-automation', '--no-sandbox', '--log-level=30']
    if datapath is not None: arglist.append(f'--user-data-dir={datapath}')
    if ip_porn is not None: arglist.append('--proxy-server=' + ip_porn)  # 使用代理
    if max_window: arglist.append("--window-size=1960,1080")
    # 最低资源加载,图片禁用暂不生效
    if minload:
        arglist.append('--disable-gpu')
        arglist.append("--disable-javascript")
        arglist.append('blink-settings=imagesEnabled=false')
        arglist.append('--profile.managed_default_content_settings.images=2')
    # 语言默认英文
    # arglist.append('--lang=en_US')
    # 忽略私密链接
    arglist.append('--ignore-certificate-errors')
    # 关闭自动化提示框
    arglist.append('--disable-infobars')
    arglist.append('--permissions.default.stylesheet=2')
    browser = await launch(executablePath=executablePath, headless=headless, autoClose=False, dumpio=True, args=arglist)
    page = (await browser.pages())[0]
    await __setPage(page, no_javascript, iphone)
    return page


async def newGet(page, url, **options):
    waituntil = options.get('waitUntil', 'load')
    # 秒数处理
    timeout = options.get('timeout', 30)
    await page.evaluate('document.getElementsByTagName("html")[0].remove()')
    await page.goto(url, options={'waitUntil': waituntil, 'timeout': timeout * 1000})


# 重置driver,不关闭浏览器
async def resetDriver(page, minload=True, no_javascript=False):
    browser = page.browser
    page = await browser.newPage()
    # 关闭之前的窗口
    [(await p.close()) for p in (await browser.pages())[:-1]]
    await __setPage(page, no_javascript)
    return page


# 新建多个窗口,并打开对应链接,最多20个
async def neWindow(page, urls, **kwargs):
    assert 0 < len(urls) <= 20, '链接数最多有20个'
    browser = page.browser
    # 计算需要新开的窗口数量
    newlen = max(len(urls) - len(await browser.pages()), 0)
    # 在原窗口基础上在新建n个窗口
    for i in range(newlen):
        page = await browser.newPage()
        await __setPage(page)
    # 依次打开链接
    pages = await browser.pages()
    for i in range(len(pages)):
        await newGet(pages[i], urls[i], **kwargs)


# 添加所有有效的cookies，提示无效的cookies
async def addCookies(page, cookies, iftz=True):
    for cookie in cookies:
        try:
            await page.setCookie(cookie)
        except:
            if iftz: print('[cookie无效]', cookie)


# 发送get请求
async def request_get(page, url):
    await page.evaluate("""
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
async def request_post(page, url, data):
    if type(data) == dict:
        data = '&'.join(["{key}={value}".format(key=key, value=data[key]) for key in data.keys()])
    await page.evaluate("""
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
async def wait_getResponse(page, maxci=10, mintime=0.5):
    for i in range(maxci):
        await sleep(mintime)
        text = await page.evaluate("return window.text;")
        if text is None:
            print("没有进行发送请求，无返回值")
            return ""
        if text != -1: return text;
    print('等待时间已过，没有获取到返回值...')
    return ""


async def screenshot(page, filepath):
    await page.screenshot({'path': filepath})


async def sleep(time):
    await asyncio.sleep(time)


# 跳转至底部
async def jumpBottom(page):
    await page.evaluate('window.scrollBy(0, document.body.scrollHeight)')


# 模拟下滑至底部
async def scroll(page):
    await page.evaluate('_ => {window.scrollBy(0, window.innerHeight);}')


# # 等待获取元素加载
# async def getWaitElements(page, xpath, timeout=15000):
#     try:
#         return page.waitForXPath(xpath, timeout=timeout)
#     except Exception as e:
#         # print('[错误]', driver.current_url, constraint)
#         raise e


# # 获取元素对象
# async def getElements_xpath(element, xpath_str):
#     return await element.xpath(xpath_str)
#
#
# # 获取元素对象
# async def getElements_js(element, js_str):
#     return await element.querySelectorAll(js_str)
#
#
# # 批量获取元素属性或文本
# async def getAttributesValues(attribute, *elements):
#     texts = []
#     for element in elements:
#         text = await (await element.getProperty(attribute if attribute != 'text' else 'textContent')).jsonValue()
#         texts.append(text)
#     return texts
#
#
# 获取元素属性或文本
async def getWaitElementValues(page, xpath, attribute=None, minnum=1, timeout=20):
    elements = []
    for i in range(timeout):
        elements = await page.xpath(xpath)
        if len(elements) >= minnum:
            break
        else:
            await sleep(1)

    assert len(elements) >= minnum, '[超时] %s' % xpath
    if attribute is None:
        return elements
    elif attribute == 'text':
        attribute = 'textContent'
    attributes = list()
    for element in elements:
        # 获取属性值
        attributes.append(await (await element.getProperty(attribute)).jsonValue())

    return attributes


#
#
# # 获取单个元素属性或文本
# async def getAttributeValue_js(element, js_str, attribute):
#     return await element.Jeval(js_str, 'node => node.' + (attribute if attribute != 'text' else 'textContent'))

'''js_str可以为tag、#id.class、.class、#id等形式'''


# 触发输入事件
async def keyInput(page, js_str, value, delay=100):
    await page.type(js_str, value, {'delay': delay})


# 触发点击事件
async def click(page, js_str):
    # 浏览器不能处于最小化，否则会一直等待
    await page.click(js_str)


# 模拟滑块拖动
async def slideDrag(page, js_str, x, delay=1500):
    await page.hover(js_str)  # 不同场景的验证码模块能名字不同。
    await page.mouse.down()
    await page.mouse.move(x, 0, {'delay': delay})
    await page.mouse.up()


# 聚焦元素，便于直接调用鼠标或键盘操作
async def focus(page, js_str):
    page.focus(js_str)


def pyppeteer_tool(urls, n, **args):
    # cookies = pc.getLocalChromeCookieList('.acg18.moe', 'acg18.moe', '.acgget.com')
    html_dict = dict()
    cookies = args.get('cookies', [])
    timeout = args.get('timeout', 30000)
    waitUntils = ['domcontentloaded', 'load', 'networkidle0', 'networkidle2']
    wait_index = args.get('wait_index', 0)
    wait_js_str = args.get('wait_js_str', None)
    wait_xpath_str = args.get('wait_xpath_str', None)
    tns = 0

    async def temp(urls, cookies, timeout, waitUntil):
        nonlocal html_dict
        nonlocal tns
        tn = tns
        tns += 1
        browser, page = await getPage()
        await page.setCookie(*cookies)
        for url in urls:
            html = ''
            for ci in range(1, 4):
                try:
                    await page.goto(url, {'waitUntil': waitUntil, 'timeout': timeout})
                    if wait_js_str is not None: await page.waitFor(wait_js_str, {'timeout': timeout})
                    if wait_xpath_str is not None: await page.waitForXPath(wait_xpath_str, {'timeout': timeout})
                    html = await page.content()
                    break
                except Exception as e:
                    print(e)
                    print('协程', tn, '失败，正在重试...第', ci, '次')
                    await asyncio.sleep(2)

            if html == '': print(url, '访问失败，以跳过')
            html_dict[url] = html
            await asyncio.sleep(1)
        await browser.close()

    tasks_url = getTasks(n, urls)
    tasks = [temp(us, cookies, timeout, waitUntils[wait_index]) for us in tasks_url]
    tasksRun(*tasks)
    # while len(html_dict.keys()) < len(urls):
    #     asyncio.sleep(1)
    return html_dict


# 处理协程的装饰器方法
def resultFunc(async_func, *args, **kwargs):
    return tasksRun(async_func(*args, **kwargs))[0]
