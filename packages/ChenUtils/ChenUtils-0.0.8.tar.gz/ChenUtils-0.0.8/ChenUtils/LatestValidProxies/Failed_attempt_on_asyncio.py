# from concurrent.futures import ThreadPoolExecutor, as_completed
from .SpiderConfiger import SpiderConfiger
import requests
from fake_useragent import UserAgent
from lxml import etree
from datetime import datetime
from .Proxy import Proxy
import time
import json
from .log import logger
import asyncio
import aiohttp


class Spider(object):
    def __init__(self, urls, group_xpath, detail_xpath, spider_configer=SpiderConfiger()):
        self.urls = urls
        self.group_xpath = group_xpath
        self.detail_xpath = detail_xpath
        self.spider_configer = spider_configer
        self.loop = asyncio.get_event_loop()
        self.semaphore = asyncio.Semaphore(5)

    def get_proxies_from_one_page(self, url):
        headers = {
            'User-Agent': UserAgent().random
        }
        response = requests.get(url, headers=headers)
        page = response.content
        parser = etree.HTMLParser(encoding=self.spider_configer.encoding)
        html = etree.HTML(page, parser=parser)
        trs = html.xpath(self.group_xpath)
        proxies = []
        for tr in trs:
            ip = tr.xpath(self.detail_xpath['ip'])[0].strip()
            port = tr.xpath(self.detail_xpath['port'])[0].strip()
            area = tr.xpath(self.detail_xpath['area'])[0].strip()
            obtain_time = datetime.now().strftime(self.spider_configer.datetime_format)
            proxies.append(Proxy(ip, port, -1, area, url, obtain_time))
        return proxies

    async def test(self, test_url, proxy):
        headers = {
            'User-Agent': UserAgent().random
        }
        start = time.time()
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(test_url, headers=headers, proxy=f'http://{proxy.ip}:{proxy.port}',
                                       timeout=self.spider_configer.test_timeout) as response:
                    proxy.speed = round(time.time() - start, 2)
                    content = await response.text()
                    content_dic = json.loads(content)
                    origin = content_dic['origin']
                    if ',' not in origin:
                        return True, proxy
            except Exception:
                return False, Proxy()
        return False, Proxy()

    async def test_proxy(self, proxy, is_get_all=False):
        async with self.semaphore:
            logger.info(f'正在检测代理ip: {proxy.ip}:{proxy.port}')
            https_check, https_proxy = await self.test('https://httpbin.org/get', proxy)
            if https_check:
                return https_proxy
            http_check, http_proxy = await self.test('http://httpbin.org/get', proxy)
            if http_check:
                return http_proxy
            return Proxy()

    def get_one_useful_proxy(self):
        for url in self.urls:
            proxies = self.get_proxies_from_one_page(url)
            # logger.info(f'正在检测来自 {url} 的代理ip')
            tasks = [self.loop.create_task(self.test_proxy(proxy)) for proxy in proxies]
            self.loop.run_until_complete(asyncio.wait(tasks))
            for task in tasks:
                proxy = task.result()
                if proxy.speed != -1:
                    logger.info(f'找到有效的匿名代理ip: {proxy.ip}:{proxy.port}')
                    return proxy
        logger.warning('无法找到有效的匿名代理ip')
        return Proxy()

    def get_useful_proxies(self, count=-1):
        valid_proxies = []
        for url in self.urls:
            proxies = self.get_proxies_from_one_page(url)
            # logger.info(f'正在检测来自 {url} 的代理ip')
            tasks = [self.loop.create_task(self.test_proxy(proxy)) for proxy in proxies]
            self.loop.run_until_complete(asyncio.wait(tasks))
            for task in tasks:
                proxy = task.result()
                if proxy.speed != -1:
                    logger.info(f'找到有效的匿名代理ip: {proxy.ip}:{proxy.port}')
                    valid_proxies.append(proxy)
        if len(valid_proxies):
            return valid_proxies
        logger.warning('无法找到有效的匿名代理ip')
        return []


if __name__ == '__main__':
    # start = time.time()
    #
    # cost = round(time.time() - start, 2)
    # print(f'本次调用用时: {cost} s')

    # rsp = requests.get(
    #     url='http://httpbin.org/get',
    #     headers={'User-Agent': UserAgent().random},
    #     proxies={
    #         'http': 'http://202.110.67.141:9091',
    #         'https': 'http://202.110.67.141:9091',
    #     }
    # )
    # print(rsp.content.decode())
    pass
