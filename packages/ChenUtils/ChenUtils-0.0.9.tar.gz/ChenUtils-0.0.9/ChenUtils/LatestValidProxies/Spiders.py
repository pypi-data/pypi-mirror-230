from .BaseSpider import BaseSpider
from fake_useragent import UserAgent
from lxml import etree
import requests


class BeesProxySpider(BaseSpider):
    def __init__(self, show_logs=False, max_pages=10, encoding=None,
                 max_worker=5, datetime_format='%Y-%m-%d %H:%M:%S', highest_latency=5):
        urls = [f'https://www.beesproxy.com/free/page/{page}' for page in range(1, max_pages + 1)]
        group_xpath = '//*[@id="article-copyright"]/figure/table/tbody/tr'
        detail_xpath = {
            'ip': './td[1]/text()',
            'port': './td[2]/text()',
            'area': './td[3]/text()'
        }
        super().__init__(urls=urls, group_xpath=group_xpath, detail_xpath=detail_xpath,
                         show_logs=show_logs, max_pages=max_pages, encoding=encoding,
                         max_worker=max_worker, datetime_format=datetime_format, highest_latency=highest_latency)


class Ip89Spider(BaseSpider):
    def __init__(self, show_logs=False, max_pages=10, encoding=None,
                 max_worker=5, datetime_format='%Y-%m-%d %H:%M:%S', highest_latency=5):
        urls = [f'https://www.89ip.cn/index_{page}.html' for page in range(1, max_pages + 1)]
        group_xpath = "//*[name()='tbody']/tr"
        detail_xpath = {
            'ip': './td[1]/text()',
            'port': './td[2]/text()',
            'area': './td[3]/text()'
        }
        super().__init__(urls=urls, group_xpath=group_xpath, detail_xpath=detail_xpath,
                         show_logs=show_logs, max_pages=max_pages, encoding=encoding,
                         max_worker=max_worker, datetime_format=datetime_format, highest_latency=highest_latency)


class KuaidailiSpider(BaseSpider):
    def __init__(self, show_logs=False, max_pages=10, encoding=None,
                 max_worker=5, datetime_format='%Y-%m-%d %H:%M:%S', highest_latency=5):
        urls = [f'https://www.kuaidaili.com/free/intr/{page}' for page in range(1, max_pages + 1)]
        group_xpath = "//*[name()='tbody']/tr"
        detail_xpath = {
            'ip': './td[1]/text()',
            'port': './td[2]/text()',
            'area': './td[5]/text()'
        }
        super().__init__(urls=urls, group_xpath=group_xpath, detail_xpath=detail_xpath,
                         show_logs=show_logs, max_pages=max_pages, encoding=encoding,
                         max_worker=max_worker, datetime_format=datetime_format, highest_latency=highest_latency)


class Ip66Spider(BaseSpider):
    def __init__(self, show_logs=False, max_pages=10, encoding=None,
                 max_worker=5, datetime_format='%Y-%m-%d %H:%M:%S', highest_latency=5):
        urls = [f'http://www.66ip.cn/{page}.html' for page in range(1, max_pages + 1)]
        group_xpath = "//*[name()='table']/tr[position()>1]"
        detail_xpath = {
            'ip': './td[1]/text()',
            'port': './td[2]/text()',
            'area': './td[3]/text()'
        }
        super().__init__(urls=urls, group_xpath=group_xpath, detail_xpath=detail_xpath,
                         show_logs=show_logs, max_pages=max_pages, encoding=encoding,
                         max_worker=max_worker, datetime_format=datetime_format, highest_latency=highest_latency)


class IhuanSpider(BaseSpider):
    def __init__(self, show_logs=False, max_pages=10, encoding=None,
                 max_worker=5, datetime_format='%Y-%m-%d %H:%M:%S', highest_latency=5):
        self.ihuan_pages = (self.get_ihuan_pages('https://ip.ihuan.me/?page=b97827cc') +
                            self.get_ihuan_pages('https://ip.ihuan.me/?page=eas7a436'))
        urls = [f'https://ip.ihuan.me/{page}' for page in self.ihuan_pages]
        group_xpath = "//*[name()='tbody']/tr"
        detail_xpath = {
            'ip': './td[1]/a/text()',
            'port': './td[2]/text()',
            'area': './td[3]/a/text()'
        }
        super().__init__(urls=urls, group_xpath=group_xpath, detail_xpath=detail_xpath,
                         show_logs=show_logs, max_pages=max_pages, encoding=encoding,
                         max_worker=max_worker, datetime_format=datetime_format, highest_latency=highest_latency)

    def get_ihuan_pages(self, url):
        response = requests.get(url, headers={'User-Agent': UserAgent().random})
        html = etree.HTML(response.content)
        pages = html.xpath("//*[name()='ul']/li[position()>1]/a/@href")[4:10]
        return pages


if __name__ == '__main__':
    beesproxy_spider = BeesProxySpider(show_logs=True)
    proxy = beesproxy_spider.get_one_useful_proxy()
    print(proxy.ip, proxy.port)
