import traceback
from scrapy import Selector
from urllib import request
import re
import time
import requests
import json
import socket
from bs4 import BeautifulSoup
import sqlite3
import os
import sys
import ctypes.wintypes
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from httplib2 import socks
import mengling_tool.asynchronous_tool as yb
from lxml import etree
import urllib.parse
import execjs
import httplib2
from anole import UserAgent

UA = None

CRO_headers = {
    'user-agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'}
FI_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0"}

__HEARDERS = {
    'cache-control': 'no-cache',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
}


# 字符串转headers
def getHeaders_str(string):
    headers = dict()
    lines = string.split('\n')
    for line in lines:
        line = line.strip()
        if line != '':
            key, value = str(re.match('.+?:', line).group()[0:-1]), str(re.search(':.+', line).group()[1:])
            headers[key] = value.strip()
    return headers


# 获取对应的cookie文本
def getCookieStr(drivercookies: list, *names):
    cs = []
    names = set(names)
    for cookie in drivercookies:
        if len(names) == 0 or cookie['domain'] in names:
            cs.append('%s=%s' % (cookie['name'], cookie['value']))
    return '; '.join(cs)


'''用于解密encrypted_value的配套方法'''


def __dpapi_decrypt(encrypted):
    class DATA_BLOB(ctypes.Structure):
        _fields_ = [('cbData', ctypes.wintypes.DWORD),
                    ('pbData', ctypes.POINTER(ctypes.c_char))]

    p = ctypes.create_string_buffer(encrypted, len(encrypted))
    blobin = DATA_BLOB(ctypes.sizeof(p), p)
    blobout = DATA_BLOB()
    retval = ctypes.windll.crypt32.CryptUnprotectData(
        ctypes.byref(blobin), None, None, None, None, 0, ctypes.byref(blobout))
    if not retval:
        raise ctypes.WinError()
    result = ctypes.string_at(blobout.pbData, blobout.cbData)
    ctypes.windll.kernel32.LocalFree(blobout.pbData)
    return result


def __aes_decrypt(datapath, encrypted_txt):
    with open(fr'{datapath}\Local State', encoding='utf-8',
              mode="r") as f:
        jsn = json.loads(str(f.readline()))
    encoded_key = jsn["os_crypt"]["encrypted_key"]
    encrypted_key = base64.b64decode(encoded_key.encode())
    encrypted_key = encrypted_key[5:]
    key = __dpapi_decrypt(encrypted_key)
    nonce = encrypted_txt[3:15]
    cipher = Cipher(algorithms.AES(key), None, backend=default_backend())
    cipher.mode = modes.GCM(nonce)
    decryptor = cipher.decryptor()
    return decryptor.update(encrypted_txt[15:])


def __chrome_decrypt(datapath, encrypted_txt):
    if sys.platform == 'win32':
        try:
            if encrypted_txt[:4] == b'x01x00x00x00':
                decrypted_txt = __dpapi_decrypt(encrypted_txt)
                return decrypted_txt.decode()
            elif encrypted_txt[:3] == b'v10':
                decrypted_txt = __aes_decrypt(datapath, encrypted_txt)
                return decrypted_txt[:-16].decode()
        except WindowsError:
            return None
    else:
        raise WindowsError


# 获取当地谷歌浏览器的cookies文件数据
def getLocalChromeCookieList(*domains, pattern=None, ischromium=False, datapath=None):
    if ischromium:
        __user_data_hz__ = r"\Chromium\User Data"
    else:
        __user_data_hz__ = r"\Google\Chrome\User Data"
    datapath = f'{os.environ["LOCALAPPDATA"]}{__user_data_hz__}' if datapath is None else datapath
    ##高版本的谷歌路径\Default\Network\Cookies
    cookiepath = fr'{datapath}\Default\Cookies'
    sql = "select host_key,name,encrypted_value from cookies"
    if len(domains) > 0 or pattern is not None:
        sql += " where "
        for domain in domains:
            sql += "host_key='%s' or " % domain
        if pattern is not None: sql += "host_key like '%s' or " % pattern
        sql = str(sql[:-4])
    cookielist = []
    with sqlite3.connect(cookiepath) as conn:
        cu = conn.cursor()
        try:
            cls = cu.execute(sql).fetchall()
        except:
            traceback.print_exc()
            raise ValueError(cookiepath)
        lie0 = cu.description  # 获取列
        # 记录列名
        if lie0 is not None:
            lies = [lie[0] for lie in lie0]
        else:
            lies = []
        for ts in cls:
            cookies = dict()
            for i in range(len(ts)):
                if lies[i] == 'encrypted_value':  # 加密处理
                    cookies[lies[i]] = __chrome_decrypt(datapath, ts[i])
                    # 记录到value值
                    cookies['value'] = __chrome_decrypt(datapath, ts[i])
                elif lies[i] == 'value':  # 原value不记录
                    continue
                elif lies[i] == 'host_key':
                    cookies['domain'] = ts[i]
                else:
                    cookies[lies[i]] = ts[i]
            cookielist.append(cookies)
    return cookielist


def getLocalEdgeCookieList(*domains, pattern=None, datapath=None):
    datapath = fr'{os.environ["LOCALAPPDATA"]}\Microsoft\Edge\User Data' if datapath is None else datapath
    cookiepath = fr'{datapath}\Default\Network\Cookies'
    sql = "select host_key,name,encrypted_value from cookies"
    if len(domains) > 0 or pattern is not None:
        sql += " where "
        for domain in domains:
            sql += "host_key='%s' or " % domain
        if pattern is not None: sql += "host_key like '%s' or " % pattern
        sql = str(sql[:-4])
    cookielist = []
    with sqlite3.connect(cookiepath) as conn:
        # 避免出现编码问题
        conn.text_factory = bytes
        cu = conn.cursor()
        cls = cu.execute(sql).fetchall()
        lie0 = cu.description  # 获取列
        # 记录列名
        if lie0 is not None:
            lies = [lie[0] for lie in lie0]
        else:
            lies = []
        for ts in cls:
            cookies = dict()
            for i in range(len(ts)):
                if lies[i] == 'encrypted_value':  # 加密处理
                    cookies[lies[i]] = __chrome_decrypt(datapath, ts[i])
                    # 记录到value值
                    cookies['value'] = __chrome_decrypt(datapath, ts[i])
                elif lies[i] == 'value':  # 原value不记录
                    continue
                elif lies[i] == 'host_key':
                    cookies['domain'] = ts[i].decode('utf-8')
                else:
                    cookies[lies[i]] = ts[i].decode('utf-8')
            cookielist.append(cookies)
    return cookielist


# 获取当地火狐浏览器的cookies文件数据，高版本存在获取不到的情况
def getLocalFirefoxCookieList(*domains, pattern=None, datapath=None):
    if datapath is None:
        cookiepath_common = os.environ['APPDATA'] + r"\Mozilla\Firefox\Profiles"
    else:
        cookiepath_common = datapath
    folds_arr = os.listdir(cookiepath_common)
    folds_end = [os.path.splitext(file)[-1][1:] for file in folds_arr]

    if 'default-release' in folds_end:
        cookie_fold_index = folds_end.index('default-release')
    else:
        cookie_fold_index = folds_end.index('default')
    cookie_fold = folds_arr[cookie_fold_index]
    cookie_path = os.path.join(os.path.join(cookiepath_common, cookie_fold), 'cookies.sqlite')
    # 获取cookie数据
    with sqlite3.connect(cookie_path) as conn:
        cur = conn.cursor()
        sql = "select baseDomain, name, value from moz_cookies"
        if len(domains) > 0 or pattern is not None:
            sql += " where "
            for domain in domains:
                sql += "baseDomain ='%s' or " % domain[1:]
            if pattern is not None: sql += "baseDomain like '%s' or " % pattern
            sql = str(sql[:-4])

        cookiedts = [{'domain': '.' + baseDomain, 'name': name, 'value': value}
                     for baseDomain, name, value in cur.execute(sql).fetchall()
                     if name != 'miniDialog']
    return cookiedts


# 获取本机ip
def getLocalIp():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


# 获取嵌入后的有效链接，替代直接用format
def getUrlFormat(url0, **valuedt):
    for key in valuedt:
        # 转义为url字段，避免类似&的情况
        valuedt[key] = urllib.parse.quote(str(valuedt[key]))
    return url0.format(**valuedt)


# 获取参数编码后的链接
def getEncodeUrl(url0, valuedt: dict):
    encode_params = urllib.parse.urlencode(list(valuedt.items()))
    return f'{url0}?{encode_params}'


# 获取url编码文本
def getUrlEncodeStr(txt: str, encoding='utf-8') -> str:
    return urllib.parse.quote(txt, encoding=encoding)


# 获取原网页,动态网址不能直接获取
def getHtml_get(url, **args):
    global CRO_headers
    headers = args.get('headers', CRO_headers)
    timeout = args.get('timeout', 20)
    proxies = args.get('proxies', None)
    valuetype = args.get('valuetype', 'text')
    ifcheckstatus = args.get('ifcheckstatus', True)
    verify = args.get('verify', True)
    if headers != CRO_headers:
        if 'user-agent' not in headers.keys() and 'User-Agent' not in headers.keys():
            headers['user-agent'] = CRO_headers['user-agent']
    if proxies is None:
        r = requests.get(url, headers=headers, timeout=timeout, verify=verify)
    else:
        r = requests.get(url, headers=headers, proxies={'https': proxies, 'http': proxies},
                         timeout=timeout, verify=verify)
    if ifcheckstatus: r.raise_for_status()  # 如果状态不为200，返回异常
    # 原始对象
    if valuetype == 'text':
        return r.text
    elif valuetype == 'content':
        return r.content
    elif valuetype == 'json':
        return r.json()
    else:
        return r


def getHtml_get_threadPool(urls, n, **args):
    sumdt = dict()
    values = [(url, args) for url in urls]
    ci = args.get('ci', 3)
    sleeptime = args.get('sleeptime', 1)

    def temp_get(url, args):
        nonlocal ci
        nonlocal sumdt
        nonlocal sleeptime
        for i in range(ci):
            try:
                html = getHtml_get(url, **args)
                if html == '':
                    raise Exception()
                else:
                    break
            except:
                time.sleep(sleeptime)
                continue
        if html == '': print('获取源码失败：', url)
        sumdt[url] = html

    pool, ps = yb.threadPool(n, temp_get, values)
    pool.shutdown()
    return sumdt


def getSession(driver_cookies=()):
    session = requests.session()
    c = requests.cookies.RequestsCookieJar()
    for i in driver_cookies:  # 添加cookie到CookieJar
        c.set(i["name"], i["value"])
    session.cookies.update(c)  # 更新session里的cookie
    return session


def getSession_dts(cookies: list = ()):
    session = requests.session()
    for cookie in cookies:
        c = requests.utils.cookiejar_from_dict(cookie)
        session.cookies.update(c)  # 更新session里的cookie
    return session


def sessionGet(session, url, proxies=None, timeout=20, ifjson=False, headers=None):
    global __HEARDERS
    headers = __HEARDERS if headers is None else headers
    html = session.get(url, headers=headers, proxies=proxies, timeout=timeout)
    # 原始对象
    if ifjson:
        return html.json()
    else:
        return html.text


def sessionPost(session, url, data, proxies=None, timeout=20, ifjson=False, headers=None):
    global __HEARDERS
    headers = __HEARDERS if headers is None else headers
    html = session.post(url, data, headers=headers, proxies=proxies, timeout=timeout)
    # 原始对象
    if ifjson:
        return html.json()
    else:
        return html.text


def getHtml_post(url, data, **args):
    global CRO_headers
    headers = args.get('headers', CRO_headers)
    timeout = args.get('timeout', 20)
    encoding = args.get('encoding', 'utf-8')
    proxies = args.get('proxies', None)
    ifobject = args.get('ifobject', False)
    verify = args.get('verify', True)
    if headers != CRO_headers:
        if 'user-agent' not in headers.keys():
            headers['user-agent'] = CRO_headers['user-agent']
    html = requests.post(url, headers=headers, data=data, proxies=proxies, timeout=timeout, verify=verify)
    # 原始对象
    if ifobject: return html
    html.encoding = encoding
    return html.text


def getHtml_open(url, **args):
    global CRO_headers
    headers = args.get('headers', CRO_headers)
    timeout = args.get('timeout', 20)
    proxies = args.get('proxies', None)
    ifobject = args.get('ifobject', False)
    if headers != CRO_headers:
        if 'User-Agent' not in headers.keys():
            headers['User-Agent'] = CRO_headers['uer-agent']
    # 查看路径是否存在
    req = request.Request(url, headers=headers)
    data = request.urlopen(req)
    # 原始对象
    if ifobject:
        return data
    else:
        return data.read().decode('utf-8')


# 关闭httplib2模块的控制台输出
httplib2.debuglevel = -1


def getHttplib2(**kwargs):
    proxies = kwargs.get('proxies', None)
    timeout = kwargs.get('timeout', 20)
    if proxies is None:
        h = httplib2.Http(timeout=timeout)
    else:
        ip, port = proxies.split(':')
        h = httplib2.Http(proxy_info=httplib2.ProxyInfo(socks.PROXY_TYPE_HTTP, ip, int(port)), timeout=timeout)
    return h


def httplib2Get(h, url, **kwargs):
    global __HEARDERS
    headers = kwargs.get('headers', __HEARDERS)
    ifobject = kwargs.get('ifobject', False)
    if headers != __HEARDERS:
        if 'user-agent' not in headers.keys() and 'User-Agent' not in headers.keys():
            headers['user-agent'] = __HEARDERS['user-agent']
        if 'cache-control' not in headers.keys():
            headers['cache-control'] = __HEARDERS['cache-control']

    # 查看路径是否存在
    response, content = h.request(url, headers=headers)
    # 原始对象
    if ifobject:
        return response
    else:
        return content.decode('utf-8')


def httplib2Post(h, url, data, **kwargs):
    global __HEARDERS
    headers = kwargs.get('headers', __HEARDERS)
    ifobject = kwargs.get('ifobject', False)
    if headers != __HEARDERS:
        if 'user-agent' not in headers.keys() and 'User-Agent' not in headers.keys():
            headers['user-agent'] = __HEARDERS['user-agent']
        if 'cache-control' not in headers.keys():
            headers['cache-control'] = __HEARDERS['cache-control']

    # 查看路径是否存在
    response, content = h.request(url, method='POST', headers=headers, body=data)
    # 原始对象
    if ifobject:
        return response
    else:
        return content.decode('utf-8')


# 设置获取数据类型
def getDatas(yuan):
    # 获取所有链接
    pattern = '(https?://[^\s)";]+(\.(\w|/)*))'
    link = re.compile(pattern).findall(yuan)
    # 将文件链接去重并统一输出为列表格式
    return list(set([li[0] for li in link]))


# 下载链接至本地
def downData(url, path, filefullname, **args):
    global CRO_headers
    headers = args.get('headers', CRO_headers)
    timeout = args.get('timeout', 30)
    proxies = args.get('proxies', None)
    tz = args.get('tz', True)
    if headers != CRO_headers:
        if 'user-agent' not in headers.keys():
            headers['user-agent'] = CRO_headers['user-agent']
    if timeout > 0: socket.setdefaulttimeout(timeout)  # 解决下载不完全问题且避免陷入死循环
    try:
        # 查看路径是否存在
        if not os.path.exists(path):  os.makedirs(path)
        if proxies is not None:
            # 更改ip地址用于下载
            # 创造处理器
            proxy_head = request.ProxyHandler()
            # 创建opener
            opener = request.build_opener(proxy_head)
        else:
            opener = request.build_opener()
        filepath = path + '/' + filefullname
        if os.path.exists(filepath):
            print('已存在: ', filepath)
        else:
            # 载入头文件模拟浏览器行为
            headers = [(key, headers[key]) for key in headers.keys()]
            opener.addheaders = headers
            request.install_opener(opener)
            # 开始下载
            request.urlretrieve(url, filepath)
    except socket.timeout:
        if tz:
            print('下载超时！')
            print(url)
        raise socket.timeout
    except Exception as e:
        if tz:
            print("下载出错：", e)
            print(url)
        raise e


# 多线程下载
def downData_threadPool(urls, n, path, format, **args):
    def dfunc(urls, index, n, path, format, args):
        length = len(urls)
        ci = 0
        head_str = args.get('head_str', '')
        ci_max = args.get('ci_max', 3)
        while True:
            if index >= length: break
            try:
                downData(urls[index], path, ''.join([head_str, str(index), format]), **args)
                index += n
                ci = 0
            except Exception as e:
                ci += 1
                if ci < ci_max:
                    print(e)
                    print('丢失：', urls[index])
                    print('重新下载，先休息...', ci)
                    time.sleep(3)
                else:
                    print('下载失败：', urls[index])
                    index += n
                    ci = 0
            time.sleep(0.5)

    pool, ps = yb.threadPool(6, dfunc, [(urls, i, n, path, format, args) for i in range(n)])
    pool.shutdown()


# 下载链接至本地,写入式
def downData_w(url, path, newfullname, **args):
    global CRO_headers
    headers = args.get('headers', CRO_headers)
    timeout = args.get('timeout', 30)
    proxies = args.get('proxies', None)
    tz = args.get('tz', True)
    if headers != CRO_headers:
        if 'User-Agent' not in headers.keys():
            headers['User-Agent'] = CRO_headers['User-Agent']
    try:
        # 查看路径是否存在
        if not os.path.exists(path):  os.makedirs(path)
        req = request.Request(url, headers=CRO_headers)
        data = request.urlopen(req).read()
        with open(path + '/' + newfullname, 'wb') as f:
            f.write(data)
    except Exception as e:
        if tz: print("下载出错：", e)
        raise e


def getSoup(html, BeautifulSoup_value='html.parser'):
    soup = BeautifulSoup(html, BeautifulSoup_value)
    return soup


def getLxml(html):
    return etree.HTML(html)


def getJson(json_str):
    return json.loads(json_str)


# 谷歌翻译，英翻汉
def translate(text):
    assert len(text) < 4891, "翻译的长度超过限制！！！"
    tk = execjs.compile("""
           function TL(a) {
           var k = "";
           var b = 406644;
           var b1 = 3293161072;
           var jd = ".";
           var $b = "+-a^+6";
           var Zb = "+-3^+b+-f";

           for (var e = [], f = 0, g = 0; g < a.length; g++) {
               var m = a.charCodeAt(g);
               128 > m ? e[f++] = m : (2048 > m ? e[f++] = m >> 6 | 192 : (55296 == (m & 64512) && g + 1 < a.length && 56320 == (a.charCodeAt(g + 1) & 64512) ? (m = 65536 + ((m & 1023) << 10) + (a.charCodeAt(++g) & 1023),
               e[f++] = m >> 18 | 240,
               e[f++] = m >> 12 & 63 | 128) : e[f++] = m >> 12 | 224,
               e[f++] = m >> 6 & 63 | 128),
               e[f++] = m & 63 | 128)
           }
           a = b;
           for (f = 0; f < e.length; f++) a += e[f],
           a = RL(a, $b);
           a = RL(a, Zb);
           a ^= b1 || 0;
           0 > a && (a = (a & 2147483647) + 2147483648);
           a %= 1E6;
           return a.toString() + jd + (a ^ b)
       };

       function RL(a, b) {
           var t = "a";
           var Yb = "+";
           for (var c = 0; c < b.length - 2; c += 3) {
               var d = b.charAt(c + 2),
               d = d >= t ? d.charCodeAt(0) - 87 : Number(d),
               d = b.charAt(c + 1) == Yb ? a >>> d: a << d;
               a = b.charAt(c) == Yb ? a + d & 4294967295 : a ^ d
           }
           return a
       }
       """).call("TL", text)

    content = urllib.parse.quote(text)
    url = "http://translate.google.cn/translate_a/single?client=t" \
          "&sl=en&tl=zh-CN&hl=zh-CN&dt=at&dt=bd&dt=ex&dt=ld&dt=md&dt=qca" \
          "&dt=rw&dt=rm&dt=ss&dt=t&ie=UTF-8&oe=UTF-8&clearbtn=1&otf=1&pc=1" \
          "&srcrom=0&ssel=0&tsel=0&kc=2&tk=%s&q=%s" % (tk, content)
    result = getHtml_get(url)
    end = result.find("\",")
    if end > 4: result = result[4:end]
    return result


# 获取识别后的验证码
def getYZM(base64):
    # 调用接口来进行识别,非本地ocr软件
    try:
        json = getJson(
            getHtml_post(
                'https://www.paddlepaddle.org.cn/paddlehub-api/image_classification/chinese_ocr_db_crnn_mobile',
                '{"image":"%s"}' % base64))
        result = json['result'][0]['data'][0]['text']
        return result
    except:
        traceback.print_exc()
        print('[验证码解析失败]', json['result'][0])
        return None


# 获取自身ip
def getMyIp():
    return re.search('\d+\.\d+\.\d+\.\d+', getHtml_get('http://pv.sohu.com/cityjson')).group()


# 获取表格字典
def geTableDt(table_lxml) -> list:
    datadts = list()
    lies = list()
    trs = table_lxml.xpath('./tbody/tr')
    for th in trs[0].xpath('./th'):
        lies.append(th.xpath('string(.)').strip())
    for tr in trs[1:]:
        dt = dict()
        for lie, td in zip(lies, tr.xpath('./td')):
            value = td.xpath('string(.)').strip()
            dt[lie] = value
        datadts.append(dt)
    return datadts


# 获取表格字典,列与值同级
def geTableDt_thtr(table_lxml) -> dict:
    datadt = dict()
    for tr in table_lxml.xpath('./tbody/tr'):
        lie = tr.xpath('./th')[0].xpath('string(.)').strip()
        value = tr.xpath('./td')[0].xpath('string(.)').strip()
        datadt[lie] = value
    return datadt


def geTableDt_lies(table_lxml, lies, minindex=0, maxindex=None):
    datadts = list()
    trs = table_lxml.xpath('./tbody/tr')
    trs = trs[minindex:] if maxindex is None else trs[minindex:maxindex]
    for tr in trs:
        dt = dict()
        for lie, td in zip(lies, tr.xpath('./td')):
            value = td.xpath('string(.)').strip()
            dt[lie] = value
        datadts.append(dt)
    return datadts


# 获取地址对应的经纬度坐标
def getMap(addr) -> dict:
    url = "http://api.map.baidu.com/geocoding/v3/?"  # 百度地图API接口
    para = {
        "address": addr,  # 传入地址参数
        "output": "json",
        "ak": "myv6ZSUbM7bAdN3lKt4wGteYZA3noEZi"  # 百度地图开放平台申请ak
    }
    req = requests.get(url, para)
    req = req.json()
    return req['result']['location']


# 获得随机头
def getFakeUserAgent():
    global UA
    if UA is None: UA = UserAgent()
    return str(UA.random)


# 获取解析对象,弃用,移至解析工具
def getSelector(txt: str):
    return Selector(text=txt)


def getCookie_txt(*webs, pattern=None, ischromium=False, keys=None, datapath=None):
    dts = getLocalChromeCookieList(*webs, pattern=pattern, ischromium=ischromium, datapath=datapath)
    alldt = dict()
    for dt in dts:
        alldt[dt["name"]] = dt["value"]
    if keys is None:
        cookies = [f'{name}={value}' for name, value in alldt.items()]
    else:
        cookies = [f'{key}={alldt[key]}' for key in keys]
    cookie = '; '.join(cookies)
    return cookie


# 从给定字典中提取cookie
def getDetailedCookie(key_host: dict, datapath: str = None, if_edge=False) -> str:
    hosts = set(key_host.values())
    if if_edge:
        dts = getLocalEdgeCookieList(*hosts, datapath=datapath)
    else:
        dts = getLocalChromeCookieList(*hosts, ischromium=False, datapath=datapath)
    cookies = list()
    for key, host in key_host.items():
        ifhave = False
        for dt in dts:
            if dt['domain'] == host and dt['name'] == key:
                cookies.append(f'{key}={dt["value"]}')
                ifhave = True
                break
        if not ifhave:
            print(f'{host} -> {key} 没有找到cookie值!')
    return '; '.join(cookies)
