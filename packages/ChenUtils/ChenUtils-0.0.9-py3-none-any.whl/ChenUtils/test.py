from ChenUtils.LatestValidProxies.BaseSpider import BaseSpider


class MySpider(BaseSpider):
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


if __name__ == '__main__':
    spider = MySpider(show_logs=True)
    proxy = spider.get_one_useful_proxy()
    print(proxy.ip, proxy.port, proxy.speed, proxy.obtain_time)
