import socket
import time, os
import requests

CRO_headers = {
    'user-agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
}


# 下载链接至本地
def downData(url, path, filefullname, headers=None, timeout=30, proxies=None, ifcheck_have=True):
    global CRO_headers
    if not headers:
        headers = CRO_headers
    elif 'user-agent' not in headers.keys() and 'User-Agent' not in headers.keys():
        headers['user-agent'] = CRO_headers['user-agent']
    if timeout > 0: socket.setdefaulttimeout(timeout)  # 解决下载不完全问题且避免陷入死循环
    filepath = f'{path}/{filefullname}'
    try:
        # 查看路径是否存在
        if not os.path.exists(path):  os.makedirs(path)
        if ifcheck_have and os.path.exists(filepath):
            print('已存在: ', filepath)
        else:
            proxies = {'https': f'http://{proxies}', 'http': f'http://{proxies}'} if proxies else None
            req = requests.get(url, proxies=proxies, headers=headers)
            with open(filepath, mode='wb') as file:
                file.write(req.content)
    except socket.timeout:
        print(url)
        raise socket.timeout
    except Exception as e:
        print(url)
        raise e
