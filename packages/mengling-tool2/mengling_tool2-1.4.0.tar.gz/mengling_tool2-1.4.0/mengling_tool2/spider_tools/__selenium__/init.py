from selenium import webdriver
from .stealth_min_js import driver_js


def __getGeneralOptions(options, headless, minload, proxies):
    # 设置代理
    if proxies is not None: options.add_argument(('--proxy-server=' + proxies))
    if headless: options.add_argument("--headless")
    # 最低资源加载
    if minload:
        # 禁止加载img及css
        try:
            prefs = {"profile.managed_default_content_settings.images": 2,
                     'permissions.default.stylesheet': 2}
            options.add_experimental_option("prefs", prefs)
        except:
            options.set_preference('permissions.default.image', 2)
        options.add_argument('--disable-gpu')
    else:
        try:
            prefs = {"profile.managed_default_content_settings.images": 1,
                     'permissions.default.stylesheet': 1}
            options.add_experimental_option("prefs", prefs)
        except:
            options.set_preference('permissions.default.image', 1)
    # 忽略私密链接
    options.add_argument('--ignore-certificate-errors')


def __getGeneralAction(driver, min_window, max_window, url, timeout):
    if min_window:
        driver.minimize_window()  # 浏览器窗口最小化
    elif max_window:
        driver.set_window_size(1920, 1080)
        driver.maximize_window()  # 浏览器窗口最大化
    # 设置超时时间,超时后网页还是没有加载完成则抛出异常
    driver.set_page_load_timeout(timeout)
    # 需要先进一次网页非开发人员模式才能生效
    if url: driver.get(url)
    # 增加自身句柄列表
    driver.hands = list(driver.window_handles)


def chrome_init(driver, headless, ifiphone, user_agent, minload, ifchromium, custom_cd_cm,
                proxies, getnum, min_window, max_window, url, datapath, chrome_version, timeout):
    # driver.timeout = timeout
    if custom_cd_cm is None:
        if ifchromium:
            # chromedriver的绝对路径
            driver.chromedriver_path = f"D:/python39/chromium{chrome_version}/my_cdr.exe"
            driver.chrome_path = f'D:/python39/chromium{chrome_version}/chrome.exe'
        else:
            # chromedriver的绝对路径
            driver.chromedriver_path = "D:/python39/my_cdr.exe"
            driver.chrome_path = None  # 则使用默认的谷歌浏览器
    else:
        driver.chromedriver_path, driver.chrome_path = custom_cd_cm
    # 最大打开数量,避免缓存过多
    driver.getnum = getnum

    options = webdriver.ChromeOptions()
    if datapath is not None: options.add_argument(r'--user-data-dir=' + datapath)
    # 模拟手机端
    if ifiphone:
        user_agent = 'MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1'
    else:
        if user_agent is None:
            # 避免使用headless的头文件,可能通过判断代理头不一致的方式反爬
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
            # user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36'
    options.add_argument('user-agent=' + user_agent)
    __getGeneralOptions(options, headless=headless, minload=minload, proxies=proxies)
    # 初始化一个driver，并且指定chromedriver的路径
    if driver.chrome_path is not None: options.binary_location = driver.chrome_path

    # 设置打开模式为非开发人员模式,2021最新方式,多页面依然有效,且屏蔽上方提示栏
    options.add_experimental_option(
        "excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("disable-blink-features=AutomationControlled")

    webdriver.Chrome.__init__(driver, executable_path=driver.chromedriver_path, options=options)
    # 使用特殊js改变行为参数
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": driver_js
    })
    # 设置打开模式为非开发人员模式,需要先进一次网页才能生效
    # undefined
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """Object.defineProperty(navigator, 'webdriver', {
                                  get: () => undefined
                                })"""})
    # 避免无头
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """Object.defineProperty(navigator, 'chrome', {
                                 get: () => undefined
                               })"""})
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """Object.defineProperty(navigator, 'vendor', {
                                      get: () => ''
                                    })"""})
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """Object.defineProperty(navigator, 'plugins', {
                                 get: () => [1, 2, 3],
                               })"""})
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """Object.defineProperty(navigator, 'languages', {
                                 get: () => ['zh-CN', 'zh'],
                               })"""})
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """Object.defineProperty(navigator, 'deviceMemory', {
                                 get: () => 8
                               })"""})
    __getGeneralAction(driver, min_window=min_window, max_window=max_window, url=url, timeout=timeout)


def firefox_init(driver, headless, ifiphone, user_agent, minload,
                 proxies, getnum, min_window, max_window, url, datapath):
    # 最大打开数量,避免缓存过多
    driver.getnum = getnum
    options = webdriver.FirefoxOptions()
    __getGeneralOptions(options, headless=headless, minload=minload, proxies=proxies)
    # 模拟手机端
    if ifiphone:
        user_agent = 'MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1'
    else:
        if user_agent is None:
            # 避免使用headless的头文件,可能通过判断代理头不一致的方式反爬
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/50.0'
            # user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36'
    # datapath无法生效
    profile = webdriver.FirefoxProfile(datapath)
    profile.set_preference("dom.webdriver.enabled", False)
    profile.set_preference("general.useragent.override", user_agent)
    webdriver.Firefox.__init__(driver, executable_path=r'D:\python39\geckodriver.exe',
                               options=options, firefox_profile=profile)
    __getGeneralAction(driver, min_window=min_window, max_window=max_window, url=url, timeout=timeout)
