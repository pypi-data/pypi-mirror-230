from scrapy import Selector


# 获取解析对象
def getSelector(txt: str) -> Selector:
    return Selector(text=txt)


# 获取元素下全部文本,排除非空
def getAllTexts(e: Selector, e_xpath: str, if_remove_null=True) -> list:
    txts = e.xpath(e_xpath + '//text()').extract()
    return [txt.strip() for txt in txts if not if_remove_null or len(txt.strip()) > 0]
