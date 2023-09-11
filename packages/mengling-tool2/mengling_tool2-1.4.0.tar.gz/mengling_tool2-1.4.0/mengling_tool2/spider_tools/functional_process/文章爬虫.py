from bs4 import BeautifulSoup
from ...functions.thread_old import SuperTaskClass
from ...asynchronous_tool import retryFunc


class TitleSpider:
    def __init__(self, pages: list, **kwargs):
        """
        处理预览列表，跳页，处理详情页面，记录功能

        :param pages: 需要抓取的页数列表
        """
        # 页面列表
        self.pages = pages
        self.ci = kwargs.get('ci', 3)

    def __initFunc__(self, getDriver_driver, driver_page_goPage,
                     driver_page_getPageData_data, data_saveDataP,
                     driver_href_getDetail_data, url_data_saveDataD,
                     args_childThreadOver=lambda x: x.close()):
        self.getDriver = getDriver_driver
        self.goPage = driver_page_goPage
        self.getPageData = driver_page_getPageData_data
        self.saveDataP = data_saveDataP
        self.getDetail = driver_href_getDetail_data
        self.saveDataD = url_data_saveDataD
        self.childThreadOver = args_childThreadOver

    # 获取单位元素组
    def getElementsls(self, htmls, tag_str=None, tag_constraint: dict = None):
        if tag_constraint is None:
            tag_constraint = {}
        elementsls = list()
        for html in htmls:
            soup = BeautifulSoup(html, 'html.parser')
            if tag_str is not None:
                tags = soup.find_all(tag_str, **tag_constraint)
                if len(tags) == 0: print("文章没有解析对象")
            else:
                tags = [soup]
            elementsls.append(tags)
        return elementsls

    # 使用单位元素字典获取子属性值字典
    def getAttributeValue(self, element, tag_str, tag_constraint: dict, attribute):
        # 直接访问母元素
        if tag_str == '':
            tags = [element]
        else:
            tags = element.find_all(tag_str, **tag_constraint)
        values = list()
        if len(tags) == 0:
            print(tag_str, tag_constraint, attribute, "子节点没有解析对象")
        for tag in tags:
            if attribute == 'text':
                value = tag.text
            elif attribute == 'content':
                value = str(tag)
            elif attribute == 'string':
                value = tag.string
            else:
                value = tag.attrs.get(attribute, '')
            values.append(value)
        return values

    # 运行方法
    def run_p(self, threadnum=3):
        print('预览获取开始...')

        @retryFunc
        def temp(driver, url):
            self.goPage(driver, url)
            data = self.getPageData(driver, url)
            self.saveDataP(data)

        threadtool = SuperTaskClass(temp, self.pages, threadnum=threadnum,
                                    getCellArgs=self.getDriver, args_childThreadOver=self.childThreadOver)
        threadtool.run()

    # 运行方法
    def run_d(self, urls, threadnum=5):
        print('详情获取开始...')

        @retryFunc
        def temp(driver, url, ci=self.ci):
            data = self.getDetail(driver, url)
            self.saveDataD(url, data)

        threadtool = SuperTaskClass(temp, urls, threadnum=threadnum,
                                    getCellArgs=self.getDriver, args_childThreadOver=self.childThreadOver)
        threadtool.run()
