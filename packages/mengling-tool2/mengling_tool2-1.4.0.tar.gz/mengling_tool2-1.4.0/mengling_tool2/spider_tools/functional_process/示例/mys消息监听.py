import mengling_tool.spider_tools.pyppeteer as pyp
from mengling_tool.spider_tools.functional_process.信息监听 import Listener
import mengling_tool.notice_tool as tz


class MYS(Listener):
    def __init__(self, urls):
        self.urls = urls
        self.tdls = [None for i in urls]
        Listener.__init__(self, spacetime=10, ifloop=True,
                          driver_kwargs_resetDriverFunc_driver=self.reset,
                          driver_overDriver=self.over)
        # 记录新信息
        self.newdatas = list()

    def getDriver(self, **kwargs):
        async def temp():
            return await pyp.getPage(headless=True)

        return pyp.resultFunc(temp)

    def updateFunc(self, page):
        async def temp(page):
            await pyp.neWindow(page, self.urls)

        pyp.resultFunc(temp, page)

    def triggerFunc(self, page, **kwargs):
        async def temp(page):

            async def t(page, i):
                page = (await page.browser.pages())[i]
                title = (await pyp.getWaitElementValues(page,
                                                        '//div[@class="mhy-account-center-content-container__list"]//div[@class="mhy-article-card__title"]/h3',
                                                        'text'))[0].strip()
                if self.tdls[i] == None:
                    print('当前标题: %s' % title)
                elif self.tdls[i] != title:
                    href = (await pyp.getWaitElementValues(page,
                                                           '//div[@class="mhy-account-center-content-container__list"]//div[@class="mhy-article-card__title"]/..',
                                                           'href'))[0].strip()
                    self.newdatas.append([title, href])
                self.tdls[i] = title

            [await t(page, i) for i in range(len(self.urls))]
            return len(self.newdatas) > 0

        return pyp.resultFunc(temp, page)

    def executeFunc(self, **kwargs):
        tz.emailSend('mys新消息', '\n'.join([('%s\n%s' % (title, url)) for title, url in self.newdatas]))
        self.newdatas.clear()

    def reset(self, page, **kwargs):
        async def temp(page):
            page = await pyp.resetDriver(page)
            return page

        return pyp.resultFunc(temp, page)

    def over(self, page):
        async def temp(page):
            await page.browser.close()

        pyp.resultFunc(temp, page)


if __name__ == '__main__':
    urls = ['https://bbs.mihoyo.com/ys/accountCenter/postList?id=75276539',
            'https://bbs.mihoyo.com/ys/accountCenter/postList?id=75276545',
            'https://bbs.mihoyo.com/ys/accountCenter/postList?id=75276557']
    MYS(urls).listen()
