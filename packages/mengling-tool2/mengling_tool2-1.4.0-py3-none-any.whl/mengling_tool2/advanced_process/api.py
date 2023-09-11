# -*-coding: utf-8 -*-
import json
from ..tools.thread import thread_auto_run
from ..decorates.retry import retryFunc_args
from ..decorates.timeout import timeoutRaise_func
from ..spider_tools.spiders.spider_all import *
from copy import deepcopy
from ..tools.goodlib import ThreadDictGoods


class API:
    def __init__(self, spider_class=Httpx, spider_kw=dict()):
        self.gooder = ThreadDictGoods({'spider': [spider_class, spider_kw]})

    def getUrl(self, paramdt, **kwargs) -> str:
        raise ValueError('需要实现方法')

    @timeoutRaise_func(60, error_txt="接口请求超时!", ifraise=True)
    @retryFunc_args(ci=3)
    def resultPost(self, paramdt: dict, ifjson=True, **kwargs) -> dict or str:
        url = self.getUrl(paramdt, **kwargs)
        spider = self.gooder.getThreadKeyGood('spider')
        response = spider.post(url, json=paramdt, **kwargs)
        return json.loads(response) if ifjson else response

    def getAllPageDatas(self, paramdt0: dict, index_key,
                        js_maxindexFunc_int, js_getcontentFunc_data,
                        index_start=1, n=1,
                        iftz=False, threadnum=3, max_error_num=5,
                        **kwargs) -> list:
        def thread_ceil(index, ifjs=False):
            paramdt = deepcopy(paramdt0)
            paramdt[index_key] = index
            js = self.resultPost(paramdt, **kwargs)
            result = js_getcontentFunc_data(js)
            if ifjs:
                return js
            else:
                return result

        # 完成第一个爬取
        js0 = thread_ceil(index_start, ifjs=True)
        try:
            max_index = js_maxindexFunc_int(js0)
        except Exception as e:
            print(js0)
            raise e
        results = sum(
            thread_auto_run(thread_ceil,
                            list(range(index_start + n, max_index + 1, n)), threadnum,
                            max_error_num=max_error_num, iftz=iftz),
            js_getcontentFunc_data(js0)
        )
        self.gooder.delAllGood(iftz=iftz)
        return results
