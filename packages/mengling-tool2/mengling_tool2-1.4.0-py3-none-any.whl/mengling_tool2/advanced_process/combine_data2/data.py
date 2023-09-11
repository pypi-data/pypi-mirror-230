from ..thread_task import SuperTaskClass


# 完成指定的数据集即可
def run(name, func, dtgoods, datas, threadnum, cellnum, maxloop, iftz):
    r = dtgoods.getThreadKeyGood('r')
    datas = set(datas)
    tempdatas = datas - set(r.hkeys(name))
    while len(tempdatas) > 0 and maxloop > 0:
        datas = tempdatas
        print(f'当前完成进度：{len(datas) - len(tempdatas)}/{len(datas)}')
        SuperTaskClass(func, list(datas), cellnum,
                       name=name,
                       iftz=iftz, threadnum=threadnum).run()
        # 检测数量并进行预备池清理
        tempdatas = datas - set(r.hkeys(name))
        maxloop -= 1


def run_redis(name, name_ready, name_wait, func, dtgoods, threadnum, getnum, cellnum, maxloop, iftz):
    r = dtgoods.getThreadKeyGood('r')
    # 最大错误机制存在bug
    pass
    while maxloop > -3:
        datas = r.spop(name_ready, getnum)
        maxloop -= 1
        print(f'redis总进度：{r.getLen(name, _class="hash")}/{r.getLen(name_wait, _class="set")}')
        if len(datas) > 0:
            run(name, func, dtgoods, datas, threadnum, cellnum, 1, iftz)
        else:
            # 检测数量并进行预备池清理
            if r.getLen(name, _class='hash') < r.getLen(name_wait, _class='set'):
                s = list(r.getData(name_wait, _class='set') - set(r.hkeys(name)))
                for i in range(0, len(s), 20_0000):
                    cs = s[i:i + 20_0000]
                    r.addData(name_ready, *cs, _class='set')
            else:
                break
    if maxloop == -3: raise ValueError('已循环至最大限制,可能存在未完成组合!')
