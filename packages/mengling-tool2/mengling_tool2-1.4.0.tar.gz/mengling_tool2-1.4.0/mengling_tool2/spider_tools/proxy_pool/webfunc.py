import re, time
import base64
import requests
from scrapy import Selector

__proxies__ = {'https': 'http://172.20.26.113:4010', 'http': 'http://172.20.26.113:4010'}


def freeProxy01():
    """
    米扑代理 https://proxy.mimvp.com/
    :return:
    """
    url_list = [
        'https://proxy.mimvp.com/freeopen?proxy=in_hp',
        'https://proxy.mimvp.com/freeopen?proxy=out_hp'
    ]
    port_img_map = {'DMxMjg': '3128', 'Dgw': '80', 'DgwODA': '8080',
                    'DgwOA': '808', 'DgwMDA': '8000', 'Dg4ODg': '8888',
                    'DgwODE': '8081', 'Dk5OTk': '9999'}
    dts = []
    for url in url_list:
        html_tree = Selector(text=requests.get(url).text)
        for tr in html_tree.xpath(".//table[@class='mimvp-tbl free-proxylist-tbl']/tbody/tr"):
            try:
                ip = ''.join(tr.xpath('./td[2]/text()').extract())
                port_img = ''.join(tr.xpath('./td[3]/img/@src').extract()).split("port=")[-1]
                port = port_img_map.get(port_img[14:].replace('O0O', ''))
                if port:
                    dts.append({'host': '%s:%s' % (ip, port)})
            except Exception as e:
                pass
    return dts


def freeProxy02():
    """
    代理66 http://www.66ip.cn/
    :return:
    """
    url = "http://www.66ip.cn/mo.php"

    resp = requests.get(url, timeout=10)
    proxies = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5})', resp.text)
    return [{'host': proxy} for proxy in proxies]


def freeProxy03():
    """
    pzzqz https://pzzqz.com/
    """
    from requests import Session
    from lxml import etree
    session = Session()
    dts = list()
    try:
        index_resp = session.get("https://pzzqz.com/", timeout=20, verify=False).text
        x_csrf_token = re.findall('X-CSRFToken": "(.*?)"', index_resp)
        if x_csrf_token:
            data = {"http": "on", "ping": "3000", "country": "cn", "ports": ""}
            proxy_resp = session.post("https://pzzqz.com/", verify=False,
                                      headers={"X-CSRFToken": x_csrf_token[0]}, json=data).json()
            tree = etree.HTML(proxy_resp["proxy_html"])
            for tr in tree.xpath("//tr"):
                ip = "".join(tr.xpath("./td[1]/text()"))
                port = "".join(tr.xpath("./td[2]/text()"))
                dts.append({'host': "%s:%s" % (ip, port)})
    except Exception as e:
        pass
    return dts


def freeProxy04():
    """
    神鸡代理 http://www.shenjidaili.com/
    :return:
    """
    url = "http://www.shenjidaili.com/product/open/"
    tree = Selector(text=requests.get(url).text)
    dts = []
    for table in tree.xpath("//table[@class='table table-hover text-white text-center table-borderless']"):
        for tr in table.xpath("./tr")[1:]:
            proxy = ''.join(tr.xpath("./td[1]/text()").extract())
            dts.append({'host': proxy.strip()})
    return dts


def freeProxy05(page_count=1):
    """
    快代理 https://www.kuaidaili.com
    """
    url_pattern = [
        'https://www.kuaidaili.com/free/inha/{}/',
    ]
    url_list = []
    for page_index in range(1, page_count + 1):
        for pattern in url_pattern:
            url_list.append(pattern.format(page_index))
    dts = []
    for url in url_list:
        tree = Selector(text=requests.get(url).text)
        proxy_list = tree.xpath('.//table//tr')
        time.sleep(1)  # 必须sleep 不然第二条请求不到数据
        for tr in proxy_list[1:]:
            dts.append({'host': ':'.join(tr.xpath('./td/text()').extract()[0:2])})
    return dts


def freeProxy06(page=2):
    """
    极速代理 https://www.superfastip.com/
    :return:
    """
    url = "https://api.superfastip.com/ip/freeip?page={page}"
    dts = []
    for i in range(page):
        page_url = url.format(page=i + 1)
        try:
            resp_json = requests.get(page_url).json()
            for each in resp_json.get("freeips", []):
                dts.append({'host': "%s:%s" % (each.get("ip", ""), each.get("port", ""))})
        except Exception as e:
            pass
    return dts


def freeProxy07():
    """
    云代理 http://www.ip3366.net/free/
    :return:
    """
    urls = ['http://www.ip3366.net/free/?stype=1', ]
    dts = []
    for url in urls:
        r = requests.get(url, timeout=10)
        proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
        for proxy in proxies:
            dts.append({'host': ":".join(proxy)})
    return dts


def freeProxy08():
    """
    小幻代理 https://ip.ihuan.me/
    :return:
    """
    urls = [
        'https://ip.ihuan.me/address/5Lit5Zu9.html',
        'https://ip.ihuan.me/address/576O5Zu9.html',
        'https://ip.ihuan.me/address/6aaZ5riv.html'
    ]
    dts = []
    for url in urls:
        r = requests.get(url, timeout=10)
        proxies = re.findall(r'>\s*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*?</a></td><td>(\d+)</td>',
                             r.text)
        for proxy in proxies:
            dts.append({'host': ":".join(proxy)})
    return dts


def freeProxy10():
    """
    墙外网站 cn-proxy
    :return:
    """
    urls = ['http://cn-proxy.com/']
    dts = []
    for url in urls:
        r = requests.get(url, timeout=10, proxies=__proxies__, headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'})
        proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\w\W]<td>(\d+)</td>', r.text)
        for proxy in proxies:
            dts.append({'host': ':'.join(proxy)})
    return dts


def freeProxy12():
    urls = ['https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1']
    dts = []
    for url in urls:
        r = requests.get(url, timeout=10, proxies=__proxies__, headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'})
        proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
        for proxy in proxies:
            dts.append({'host': ':'.join(proxy)})
    return dts


def freeProxy13(max_page=2):
    """
    http://www.89ip.cn/index.html
    89免费代理
    :param max_page:
    :return:
    """
    base_url = 'http://www.89ip.cn/index_{}.html'
    dts = []
    for page in range(1, max_page + 1):
        url = base_url.format(page)
        r = requests.get(url, timeout=10)
        proxies = re.findall(
            r'<td.*?>[\s\S]*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[\s\S]*?</td>[\s\S]*?<td.*?>[\s\S]*?(\d+)[\s\S]*?</td>',
            r.text)
        for proxy in proxies:
            dts.append({'host': ':'.join(proxy)})
    return dts


def freeProxy14():
    """
    http://www.xiladaili.com/
    西拉代理
    :return:
    """
    urls = ['http://www.xiladaili.com/']
    dts = []
    for url in urls:
        r = requests.get(url, timeout=10)
        ips = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}", r.text)
        for ip in ips:
            dts.append({'host': ip.strip()})
    return dts


def my_dl01():
    """
    https://hidemy.name/en/proxy-list/#list
    国外代理
    :return:
    """
    urls = ['https://hidemy.name/en/proxy-list/#list',
            'https://hidemy.name/en/proxy-list/?start=64#list',
            'https://hidemy.name/en/proxy-list/?start=128#list',
            'https://hidemy.name/en/proxy-list/?start=192#list',
            'https://hidemy.name/en/proxy-list/?start=256#list',
            ]
    dts = []
    for url in urls:
        r = requests.get(url, timeout=10, proxies=__proxies__, headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'})
        for tr in Selector(text=r.text).xpath('//tbody/tr'):
            if 'HTTP' in tr.xpath('./td[5]').xpath('string(.)').get(''):
                dts.append(
                    {'host': f'{tr.xpath("./td[1]/text()").get("1.1.1.1")}:{tr.xpath("./td[2]/text()").get(888)}'})
    return dts

    # proxies = re.findall(
    #     r'<td.*?>[\s\S]*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[\s\S]*?</td>[\s\S]*?<td.*?>[\s\S]*?(\d+)[\s\S]*?</td>',
    #     r.text)


def my_dl02():
    """
    http://free-proxy.cz/zh/proxylist/country/US/http/ping/all
    国外代理
    :return:
    """
    urls = ['http://free-proxy.cz/zh/proxylist/country/US/http/ping/all',
            'http://free-proxy.cz/zh/proxylist/country/US/https/ping/all',
            ]
    dts = []
    for url in urls:
        r = requests.get(url, timeout=10, proxies=__proxies__, headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'})
        proxies = re.findall(
            'Base64\.decode\("([a-zA-Z0-9=]+)"\)\)</script></td><td style=""><span class="fport" style=\'\'>(\d+)</span>'
            , r.text)
        for code, port in proxies:
            ip = base64.b64decode(code).decode()
            dts.append({'host': f'{ip}:{port}'})
    return dts


def my_dl03():
    """
    https://ip.ihuan.me/
    国外代理
    :return:
    """
    urls = ['https://ip.ihuan.me/', ]
    dts = []
    for url in urls:
        r = requests.get(url, timeout=10, proxies=__proxies__, verify=False, headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'})
        proxies = re.findall(
            '>([0-9.]+)</a></td><td>(\d+)</td>'
            , r.text)
        for proxy in proxies:
            dts.append({'host': ':'.join(proxy)})
    return dts


# 蜻蜓代理
def qtdl():
    txt = requests.get(
        'https://proxyapi.horocn.com/api/v2/proxies?order_id=EFZP1704226103117766&num=10&format=text&line_separator=unix&can_repeat=no&user_token=6b167963764d620d1e259982f0a48a0d').text
    print(txt)
    ips = txt.split('\n')
    if len(ips) == 10:
        dts = [{'host': ip} for ip in ips]
    else:
        time.sleep(5)
        assert False, txt
    return dts


if __name__ == '__main__':
    dts = qtdl()
    [print(dt) for dt in dts]
