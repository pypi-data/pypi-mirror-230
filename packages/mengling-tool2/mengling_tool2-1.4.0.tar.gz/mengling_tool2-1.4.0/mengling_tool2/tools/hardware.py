from multiprocessing import cpu_count

'''需要在if __name__=='__main__':的环境下运行'''


# 获取cpu数量
def getCPUNumber():
    return cpu_count()

# # 获取进程同步对象
# def getManager():
#     # 需要在if __name__=="__main__"下执行
#     return multiprocessing.Manager()
