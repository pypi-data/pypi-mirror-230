class SpiderConfiger(object):
    def __init__(self, encoding=None, max_worker=5, datetime_format='%Y-%m-%d %H:%M:%S', test_timeout=5, max_pages=10):
        self.encoding = encoding  # 当具体爬虫类获取的代理地址显示为中文乱码在此修改解码方式
        self.max_worker = max_worker  # 设置最大线程数
        self.datetime_format = datetime_format  # 设置代理ip时间保持的格式
        self.test_timeout = test_timeout  # 设置为代理ip测速时的超时时间
        self.max_pages = max_pages  # 设置爬取代理ip网站的页数
