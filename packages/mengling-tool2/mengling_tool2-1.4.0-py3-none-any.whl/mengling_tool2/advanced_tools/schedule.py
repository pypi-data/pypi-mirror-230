from ..database_tool2.mysql import MysqlExecutor
from ..tools.notice import emailSend
from ..tools.time import getNowTime, TimeTool
from ..tools.notice import getColorStr
import time
import math
from multiprocessing import Lock, Process
import traceback


class Tasker:
    def __init__(self, table, dbname, connect: dict, process_maxnum=3, sleeptime0: int = 86400):
        # 调度表名
        self.table = table
        # 链接配置
        self.connect = {'dbname': dbname, **connect}
        # 最大进程数
        self.process_maxnum = process_maxnum
        # 半天
        self.sleeptime0 = sleeptime0
        self.sleeptime = sleeptime0
        self.lock = Lock()

    def error_send(self, title, txt):
        emailSend(title, txt)

    def run_ch(self, taskname, model, func, arg, nowtime, nextime):
        start = time.time()
        print('\n', f'{getColorStr(taskname, color_index=32)} 任务开始')
        try:
            arg = arg if arg != '-' else ""
            # 重新加载模块,注意命令严格遵守换行格式
            # 注意：更改了导入模块依赖的模块后，重新加载的函数不会对这些模块生效，需要重启任务调度
            if model != '-':
                ml = f'import {model} as model\nmodel.{func}({arg})'
            else:
                ml = f'{func}({arg})'
            exec(ml)
            end = time.time()
            print(f'work_task：{taskname} 运行成功！，运行时间: {math.ceil(end - start)} 秒')
        except:
            print(f'work_task：{taskname} 运行失败！')
            err = traceback.format_exc()
            print(err)
            self.error_send(f'{taskname} 任务失败!', err)
        # 更新时间
        with MysqlExecutor(**self.connect) as myt:
            try:
                myt.update_dt(self.table, {'上次运行时间': nowtime.to_txt(), '下次运行时间': nextime.to_txt()},
                              where=f"`任务名`='{taskname}'")
                myt.commit()
            except:
                myt.rollback()
                traceback.print_exc()

    def run(self):
        # 重置工具包模块
        nowtime = getNowTime(ifreturn_str=False)
        print('任务组开始执行...' + nowtime.to_txt())
        # log_save(nowtime.strftime("%Y_%m_%d"))
        self.sleeptime = self.sleeptime0
        try:
            with MysqlExecutor(**self.connect) as myt:
                taskdts = myt.select('*', self.table)
            args = []
            for task in taskdts:
                # 启用选项控制
                if task['启用'] == b'\x00': continue
                # 格式不正确一律视为None值
                try:
                    task['下次运行时间'] = TimeTool(task['下次运行时间'])
                    task['上次运行时间'] = TimeTool(task['上次运行时间'])
                except:
                    task['下次运行时间'], task['上次运行时间'] = None, None
                if task['下次运行时间'] is None or task['下次运行时间'] < nowtime:
                    if nowtime.to_txt(gs='%H:%M:%S') < task['时刻']:
                        # 早跑
                        temptime = nowtime
                    else:
                        # 晚跑
                        temptime = nowtime.next(task['周期'], ifreturn_str=False)
                    # 月度定时处理
                    if 31 >= task['月度'] > 0:
                        b = False
                        for i in range(345):
                            temptime.next(1, if_replace=True)
                            if temptime.date.day == task['月度']:
                                b = True
                                break
                        if not b: raise ValueError(f'月度设置有问题 {task["月度"]}')
                    # 计算下次运行时间
                    nextime = TimeTool(temptime.to_txt(gs="%Y/%m/%d ") + task['时刻'])
                    # 根据周末设置进行下次运行时间的调整
                    if task['周末'] != b'\x00' and nextime.isoweekday() in [6, 7]:
                        nextime.next(8 - nextime.isoweekday(), if_replace=True)

                    arg = [task['任务名'], task['模块'], task['方法'], task['参数'], nowtime, nextime]
                    # log_save(nowtime.strftime("%Y_%m_%d"))
                    args.append(arg)
            # 多进程运行
            ts = [Process(target=self.run_ch, args=args[i]) for i in range(min(self.process_maxnum, len(args)))]
            for t in ts:
                t.daemon = True
                t.start()
            [t.join() for t in ts]
            # 计算下次运行时间
            with MysqlExecutor(**self.connect) as myt:
                dates = myt.select('下次运行时间', self.table, where="`启用`=1", ifget_one_lie=True)
            mintime = TimeTool(min(dates))
            nowtime = getNowTime(ifreturn_str=False)
            if nowtime > mintime:
                self.sleeptime = 3
            else:
                self.sleeptime = math.ceil(min(self.sleeptime, mintime - nowtime + 3))
        except:
            print('任务组执行出错，请及时查看！')
            err = traceback.format_exc()
            print(err)
            self.error_send('任务组执行出错，请及时查看！', err)
        print(f'开始等待下一次任务...{self.sleeptime}秒\n\n')
        for i in range(self.sleeptime):
            print('\r剩余时间：%s 秒     ' % (self.sleeptime - i), end='')
            time.sleep(1)
