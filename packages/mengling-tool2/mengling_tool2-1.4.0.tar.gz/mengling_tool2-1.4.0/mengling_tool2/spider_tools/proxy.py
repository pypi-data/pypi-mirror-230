from threading import Lock
import re
import time
import traceback
import requests

# 互斥锁
mutex = Lock()
API = \
    'http://ip.ipjldl.com/api/entry?method=proxyServer.ipinfolist&packid=0&fa=0&fetch_key=&time=2&quantity=1&province=&city=&anonymous=1&ms=1&service=0&protocol=1&distinct=true&format=txt&separator=1&separator_txt='
ADDIP = 'http://www.ipjldl.com/Users-whiteIpAddNew.html?appid=716&appkey=9481418cc19467d2f0f2bd2cfb515376&whiteip='
DELAPI = 'http://www.ipjldl.com/Users-whiteIpDelNew.html?appid=716&appkey=9481418cc19467d2f0f2bd2cfb515376&whiteip=all'


def __getHtml_get(url, **args):
    CRO_headers = {
        'user-agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'}
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


# 未完成多个获取
def getIP():
    mutex.acquire()  # 上锁 注意了此时锁的代码越少越好
    time.sleep(1.5)
    try:
        ip_txt = __getHtml_get(API).strip()
    except:
        traceback.print_exc()
        mutex.release()  # 解锁
        ip_txt = None
    if re.match('^\d+\.\d+\.\d+\.\d+', ip_txt) is None:
        # 添加白名单
        my_ip = re.findall('(\d+\.\d+\.\d+\.\d+)登录IP不是白名单IP，请在用户中心添加该白名单', ip_txt)
        if len(my_ip) > 0:
            print('[添加白名单]', my_ip[0])
            addIP(my_ip[0])
            time.sleep(5)
            ip_txt = __getHtml_get(API).strip()
            if re.match('^\d+\.\d+\.\d+\.\d+', ip_txt) is not None:
                # 清空白名单
                print('[清空白名单]')
                clearIP()
                time.sleep(3)
                addIP(my_ip[0])
                time.sleep(5)
                ip_txt = __getHtml_get(API).strip()
                if re.match('^\d+\.\d+\.\d+\.\d+', ip_txt) is None:
                    print('[代理ip未获取]', ip_txt)
                    ip_txt = None
                    print('获取代理ip失败！ 默认使用本机ip')
        else:
            print('[代理ip未获取]', ip_txt)
            ip_txt = None
            print('获取代理ip失败！ 默认使用本机ip')
    if ip_txt is not None: print('[代理ip]', ip_txt)
    mutex.release()  # 解锁
    return ip_txt


# 添加白名单
def addIP(ip):
    __getHtml_get(ADDIP + ip)


# 清空白名单
def clearIP():
    __getHtml_get(DELAPI)


if __name__ == '__main__':
    print(getIP())
