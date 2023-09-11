import json
import socket
import threading
import traceback

BUFFSIZE = 1024 * 1024


# 获取本机局域网ip地址,linux系统该方法无效
def getLanIP():
    ip_address = socket.gethostbyname(socket.gethostname())
    return ip_address


# 获取协议数据组
def getSends(data):
    data = str(data).encode(encoding='utf-8')
    sendatas = list()
    # 超过最大长度则进行拆解
    cell_length = BUFFSIZE - 200
    for i in range(0, len(data), cell_length):
        sendatas.append(data[i:i + cell_length])
    index, maxindex = 1, len(sendatas)
    res = list()
    for sendata in sendatas:
        data = sendata.decode(encoding='utf-8')
        js = json.dumps({'index': index, 'maxindex': maxindex, 'data': data})
        res.append(js.encode(encoding='utf-8'))
        index += 1
    return res


# 服务端
# 仅能实现一对一联系
class TCPServer:
    # 双向连接
    def __init__(self, timeout=30):
        self.__mls = []  # 存放接受到的命令
        # SOCK_STREAM基于tcp协议,socket.SOCK_DGRAM基于udp协议
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 套接字对象
        self.__socket.settimeout(timeout)
        # 监听开启标识
        self.ifstart = False
        # 监听信息
        self.linsten_iport = None
        self.__datas = list()
        self.client = None

    # 获取命令
    def getML(self):
        if len(self.__mls) > 0:
            return self.__mls.pop(0)
        else:
            return None

    # 发送反馈
    def sendFK(self, data):
        res = getSends(data)
        # 服务端需要客户端先发送连接才可以回答
        try:
            [self.client.send(r) for r in res]
        except:
            traceback.print_exc()
            assert False, '服务端需要客户端先发送连接才可以回答!'

    def __saveData(self, ip_port, data):
        js = json.loads(data.decode(encoding='utf-8'))
        self.__datas.append(js['data'])
        if js['index'] == js['maxindex']:
            redata = ''.join(self.__datas)
            # 获取来自show端的命令,并缓存
            self.__mls.append((ip_port, redata))
            self.__datas.clear()

    # 开启监听,默认为局域网ip,局域网监听需要本机局域网ip不能选择127.0.0.1
    def start_receive(self, ip_port):
        self.ifstart = True
        self.linsten_iport = ip_port

        def openServer():
            nonlocal self
            # 复用重复端口
            self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.__socket.bind(ip_port)  # 绑定ip及端口
            self.__socket.listen(5)  # 监听
            print('[监听开启] %s:%s' % ip_port)
            client, addr = self.__socket.accept()  # 等待客户端连接
            self.client = client
            print('[连接建立] %s:%s' % addr)
            while True:
                try:
                    data = client.recv(BUFFSIZE)
                    self.__saveData(addr, data)
                except:
                    print('[监听关闭]')
                    if self.ifstart: traceback.print_exc()
                    break

        threading.Thread(target=openServer).start()

    # 关闭监听
    def close_receive(self):
        self.ifstart = False
        self.__socket.close()
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 套接字对象


# 服务端
class TCPClient:
    def __init__(self):
        self.__fks = []  # 存放接受到的命令
        # SOCK_STREAM基于tcp协议,socket.SOCK_DGRAM基于udp协议
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 套接字对象
        self.ifstart = False
        # 连接信息
        self.connect_iport = None
        self.__datas = list()

    # 获取反馈
    def getFK(self):
        if len(self.__fks) > 0:
            return self.__fks.pop(0)
        else:
            return None

    def connect(self, ip_port: tuple):
        self.connect_iport = ip_port
        self.__socket.connect(ip_port)
        print('[已连接](%s:%s)' % ip_port)
        # 开启反馈监听
        threading.Thread(target=self.__start_receive__).start()

    # 发送命令
    def sendML(self, data):
        res = getSends(data)
        # 服务端需要客户端先发送连接才可以回答
        try:
            [self.__socket.send(r) for r in res]
        except:
            traceback.print_exc()
            assert False, '客户端需要先进行连接!'

    def __saveData(self, data):
        js = json.loads(data.decode(encoding='utf-8'))
        self.__datas.append(js['data'])
        if js['index'] == js['maxindex']:
            redata = ''.join(self.__datas)
            # 获取来自show端的命令,并缓存
            self.__fks.append(redata)
            self.__datas.clear()

    # 开启监听,默认为局域网ip,局域网监听需要本机局域网ip不能选择127.0.0.1
    def __start_receive__(self):
        self.ifstart = True

        def openClient():
            nonlocal self
            while True:
                try:
                    # 获取服务器端反馈
                    recvdata = self.__socket.recv(BUFFSIZE)
                    self.__saveData(recvdata)
                except:
                    print('[监听关闭]')
                    if self.ifstart: traceback.print_exc()
                    break

        threading.Thread(target=openClient).start()

    # 关闭监听
    def close_receive(self):
        self.ifstart = False
        self.__socket.close()
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 套接字对象


if __name__ == '__main__':
    server = TCPServer()
    server.start_receive(('192.168.20.111', 2468))

    # def temp(s):
    #     while True:
    #         s.sendFK('反馈')
    #
    #
    # threading.Thread(target=temp, args=(server,)).start()

    while True:
        data = server.getML()
        if data is not None:
            print(data)
