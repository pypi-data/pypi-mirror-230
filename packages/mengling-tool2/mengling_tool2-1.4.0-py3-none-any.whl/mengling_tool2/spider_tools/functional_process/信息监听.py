import time
import traceback
from threading import Thread


class Listener:
    # 继承方法
    def __init__(self, spacetime=5, ifloop=False, **kwargs):
        # 间隔时间s
        self.spacetime = spacetime
        # 重复触发开关
        self.ifloop = ifloop
        # 重置浏览器方法
        self.resetDriver = kwargs.get('driver_kwargs_resetDriverFunc_driver', self.resetDriver)
        # 关闭浏览器方法
        self.overDriver = kwargs.get('driver_overDriver', self.overDriver)

    # 初始化方法,用于非继承的情况下
    def __initFunc__(self, kwargs_getDriver_driver, driver_updateFunc,
                     driver_kwargs_triggerFunc_tf, kwargs_executeFunc):
        # 获取浏览器
        self.getDriver = kwargs_getDriver_driver
        # 周期刷新方法
        self.updateFunc = driver_updateFunc
        # 触发器方法
        self.triggerFunc = driver_kwargs_triggerFunc_tf
        # 执行方法
        self.executeFunc = kwargs_executeFunc

    # 默认重置浏览器方法
    def resetDriver(self, driver, **kwargs):
        driver.quit()
        return self.getDriver(**kwargs)

    # 默认关闭浏览器方法
    def overDriver(self, driver):
        driver.quit()

    def listen(self, **kwargs):
        ci = 0
        timels = [(self.spacetime - i) for i in range(self.spacetime)]
        driver = self.getDriver(**kwargs)
        while True:
            try:
                try:
                    self.updateFunc(driver)
                except:
                    print(traceback.format_exc())
                    print('[刷新出错]')
                    raise Exception()
                try:
                    cf = self.triggerFunc(driver, **kwargs)
                except:
                    print(traceback.format_exc())
                    print('[触发出错]')
                    raise Exception()
                if cf:
                    print('[以触发]', '开始执行操作...')
                    try:
                        self.executeFunc(**kwargs)
                        print('[执行成功]')
                        if not self.ifloop:
                            print('[结束循环]')
                            break
                    except:
                        print(traceback.format_exc())
                        print('[执行失败]')
                        raise Exception()
                else:
                    print('[未触发]')
            except:
                print('重新加载浏览器...')
                driver = self.resetDriver(driver, **kwargs)
            ci += 1
            for i in timels:
                print('\r[等待下次监听] %s s    ' % i, end='')
                time.sleep(1)
            print('\r[监听] %s 次         ' % ci)
        print('[监听结束]')
        self.overDriver(driver)

    def run(self, **kwargs):
        th = Thread(target=self.listen, kwargs=kwargs)
        th.setDaemon(True)  # 设置t1为守护线程
        th.start()
        th.join()


if __name__ == '__main__':
    pass
