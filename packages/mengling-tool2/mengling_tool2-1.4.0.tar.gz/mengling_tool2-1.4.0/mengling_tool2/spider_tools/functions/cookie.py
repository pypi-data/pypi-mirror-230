import base64
import ctypes.wintypes
import json, os, re, sys
import sqlite3
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


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
def __getChromiumCookiedts(*domains, pattern=None, customize_cookiepath=None, datapath=None,
                           if_edge=False, ifhigh_version=False, iftest_chromium=False) -> list:
    if customize_cookiepath:
        # 使用自定义cookie位置
        cookiepath = customize_cookiepath
    else:
        if datapath is None:
            if iftest_chromium:
                __user_data_hz__ = r"\Chromium\User Data"
            elif if_edge:
                __user_data_hz__ = r"\Microsoft\Edge\User Data"
            else:
                __user_data_hz__ = r"\Google\Chrome\User Data"
            datapath = f'{os.environ["LOCALAPPDATA"]}{__user_data_hz__}'
        if ifhigh_version:
            cookiepath = fr'{datapath}\Default\Network\Cookies'
        else:
            cookiepath = fr'{datapath}\Default\Cookies'
    sql = "select host_key,name,encrypted_value from cookies"
    if len(domains) > 0 or pattern is not None:
        sql += " where "
        for domain in domains:
            sql += "host_key='%s' or " % domain
        if pattern is not None: sql += "host_key like '%s' or " % pattern
        sql = str(sql[:-4])
    cookiedts = []
    with sqlite3.connect(cookiepath) as conn:
        conn.text_factory = lambda x: str(x, 'utf-8', 'ignore')
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
                    cookies['domain'] = ts[i]
                else:
                    cookies[lies[i]] = ts[i]
            cookiedts.append(cookies)
    return cookiedts


# 获取谷歌浏览器cookie字典
def getGoogleCookiedts(*domains, pattern=None, datapath=None, ifhigh_version=False) -> list:
    return __getChromiumCookiedts(*domains, pattern=pattern, customize_cookiepath=None, datapath=datapath,
                                  if_edge=False, ifhigh_version=ifhigh_version, iftest_chromium=False)


# 获取edge浏览器cookie字典
def getEdgeCookiedts(*domains, pattern=None, datapath=None, ifhigh_version=True) -> list:
    return __getChromiumCookiedts(*domains, pattern=pattern, customize_cookiepath=None, datapath=datapath,
                                  if_edge=True, ifhigh_version=ifhigh_version, iftest_chromium=False)


# 获取测试浏览器cookie字典
def getTestChromiumCookiedts(*domains, pattern=None, datapath=None, ifhigh_version=False) -> list:
    return __getChromiumCookiedts(*domains, pattern=pattern, customize_cookiepath=None, datapath=datapath,
                                  if_edge=False, ifhigh_version=ifhigh_version, iftest_chromium=True)


# 获取cookie自定义路径字典
def getCustomizeCookiedts(*domains, customize_cookiepath: str, pattern=None) -> list:
    return __getChromiumCookiedts(*domains, pattern=pattern, customize_cookiepath=customize_cookiepath)


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


def getCookie_txt(cookiedts: list, keys=None):
    alldt = dict()
    for dt in cookiedts:
        alldt[dt["name"]] = dt["value"]
    if keys is None:
        cookies = [f'{name}={value}' for name, value in alldt.items()]
    else:
        cookies = [f'{key}={alldt[key]}' for key in keys]
    cookie = '; '.join(cookies)
    return cookie


# 校验cookie提取对应字典映射表
def getCookieMapdt(cookie: str, first_host: str, cookiedts: list):
    txtdt = dict()
    for txt in cookie.split('; '):
        k, v = re.findall('([^=]+)=(.+)', txt)[0]
        txtdt[k] = v
    mapdt = dict()
    for key, value in txtdt.items():
        hs = list()
        for dt in cookiedts:
            if dt['value'] == value:
                if dt['domain'] == first_host and dt['name'] == key:
                    mapdt[key] = first_host
                    hs = 'have'
                    break
                hs.append(f'{key}->{dt}')
        if len(hs) == 0:
            print(key, value, '没有!')
        elif hs != 'have':
            [print(t) for t in hs]
    return mapdt


# 从给定字典中提取cookie
def getDetailedCookie(cookiedts: list, key_host: dict) -> str:
    cookies = list()
    for key, host in key_host.items():
        ifhave = False
        for dt in cookiedts:
            if dt['domain'] == host and dt['name'] == key:
                cookies.append(f'{key}={dt["value"]}')
                ifhave = True
                break
        if not ifhave:
            print(f'{host} -> {key} 没有找到cookie值!')
    return '; '.join(cookies)
