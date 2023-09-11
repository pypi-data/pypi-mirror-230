import socket
import time
from threading import Thread
import re
import traceback


# 获取本机局域网ip地址,linux系统该方法无效
def getLanIP():
    ip_address = socket.gethostbyname(socket.gethostname())
    return ip_address


class UDPTool:
    # 双向连接
    def __init__(self, port: int):
        self.buffsize = 1024 * 1024
        self.port = port
        self.__mls = []  # 存放接受到的命令
        # SOCK_STREAM基于tcp协议,socket.SOCK_DGRAM基于udp协议
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 套接字对象
        # 监听开启标识
        self.ifstart = False

    # 获取命令
    def getMLdt(self):
        if len(self.__mls) > 0:
            return self.__mls.pop(0)
        else:
            return None

    # 发送结果
    def sendJG(self, ip_port: tuple, index, jg):
        self.__socket.sendto(('%s_%s' % (index, jg)).encode(encoding='utf-8'), ip_port)

    # 开启监听,默认为局域网ip,局域网监听需要本机局域网ip不能选择127.0.0.1
    ## 同ip不同端口的通信必须保证发送的端口已开启监听
    def start_receive(self, ip_s=None, appendFunc=None):
        self.ifstart = True
        appendFunc = self.__mls.append if appendFunc is None else appendFunc
        ip_port = (ip_s if ip_s is not None else getLanIP(), self.port)

        def openServer():
            nonlocal self
            self.__socket.bind(ip_port)  # 绑定ip及端口
            print('[监听开启] %s:%s' % ip_port)
            while True:
                try:
                    data, client_addr = self.__socket.recvfrom(self.buffsize)
                except:
                    print('[监听关闭]')
                    if self.ifstart: traceback.print_exc()
                    break
                index, data = re.findall('^([-0-9]+)_(.*)$', data.decode(encoding='utf-8'))[0]
                # 获取来自show端的命令,并缓存
                appendFunc({'ip': client_addr[0], 'port': client_addr[1], 'index': index, 'data': data})

        Thread(target=openServer).start()

    # 关闭监听
    def close_receive(self):
        self.ifstart = False
        self.__socket.close()
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 套接字对象


if __name__ == '__main__':
    sc = UDPTool(2468)
    sc.start_receive('192.168.20.111')
    i = 0
    while True:
        ml = sc.getMLdt()
        if ml != None: print(ml)
        time.sleep(0.05)
