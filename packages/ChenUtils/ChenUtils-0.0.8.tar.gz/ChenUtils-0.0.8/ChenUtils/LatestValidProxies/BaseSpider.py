from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from fake_useragent import UserAgent
from lxml import etree
from datetime import datetime
from .Proxy import Proxy
import time
import json
from .log import logger
import sys
import random


class BaseSpider(object):
    def __init__(self, urls, group_xpath, detail_xpath, show_logs, max_pages,
                 encoding, max_worker, datetime_format, highest_latency):
        self.urls = urls
        self.group_xpath = group_xpath
        self.detail_xpath = detail_xpath
        self._to_end = False
        self.show_logs = show_logs
        self.max_pages = max_pages
        self.encoding = encoding
        self.max_worker = max_worker
        self.datetime_format = datetime_format
        self.test_timeout = highest_latency

    def get_proxies_from_one_page(self, url):
        if self.show_logs:
            logger.info(f'Trying to establish a connection with {url}')
        headers = {
            'User-Agent': UserAgent().random
        }
        proxies = []
        try:
            response = requests.get(url, headers=headers)
            page = response.content
            parser = etree.HTMLParser(encoding=self.encoding)
            html = etree.HTML(page, parser=parser)
            trs = html.xpath(self.group_xpath)
            if self.show_logs:
                logger.info('Collecting web proxy IP information')
            for tr in trs:
                ip = tr.xpath(self.detail_xpath['ip'])[0].strip()
                port = tr.xpath(self.detail_xpath['port'])[0].strip()
                area = tr.xpath(self.detail_xpath['area'])[0].strip()
                obtain_time = datetime.now().strftime(self.datetime_format)
                proxies.append(Proxy(ip, port, -1, area, url, obtain_time))
        except Exception:
            logger.warning(f'[Connection failed]Unable to connect to {url}')
        return proxies

    def _test(self, test_url, proxy):
        headers = {
            'User-Agent': UserAgent().random
        }
        proxies = {
            'http': f'http://{proxy.ip}:{proxy.port}',
            'https': f'http://{proxy.ip}:{proxy.port}'
        }
        start = time.time()
        try:
            if self._to_end:
                return False, Proxy()
            response = requests.get(
                url=test_url,
                headers=headers,
                proxies=proxies,
                timeout=self.test_timeout
            )
            if response.ok:
                proxy.speed = round(time.time() - start, 2)
                content = response.text
                content_dic = json.loads(content)
                origin = content_dic['origin']
                if ',' not in origin:
                    return True, proxy
        except Exception:
            return False, Proxy()
        return False, Proxy()

    def _test_proxy(self, proxy):
        if self._to_end:
            return Proxy()
        if self.show_logs:
            logger.info(f'Detecting proxy ip: {proxy.ip}:{proxy.port}')
        http_check, http_proxy = self._test('http://httpbin.org/get', proxy)
        https_check, https_proxy = self._test('https://httpbin.org/get', proxy)
        if https_check:
            return https_proxy
        if http_check:
            return http_proxy
        return Proxy()

    def get_one_useful_proxy(self, is_random=False):
        start = time.time()
        self._to_end = False
        urls = self.urls
        if is_random:
            urls = random.sample(self.urls, len(self.urls))
        for url in urls:
            proxies = self.get_proxies_from_one_page(url)
            with ThreadPoolExecutor(max_workers=self.max_worker) as pool:
                futures = [pool.submit(self._test_proxy, proxy) for proxy in proxies]
                for future in as_completed(futures):
                    proxy = future.result()
                    if proxy.speed != -1:
                        if self.show_logs:
                            logger.info(f'Found a valid anonymous proxy ip: {proxy.ip}:{proxy.port}')
                        self._to_end = True
                        end = time.time()
                        if self.show_logs:
                            logger.info(
                                f'This crawling proxy IP takes: {round(end - start, 2)} s, '
                                f'waiting for the end of other threads, '
                                f'estimated time consuming 0~{self.test_timeout} s'
                            )
                        return proxy
        if self.show_logs:
            logger.warning('Could not be found a valid anonymous proxy IP')
        end = time.time()
        if self.show_logs:
            logger.info(
                f'This crawling proxy IP takes: {round(end - start, 2)} s, '
                f'waiting for the end of other threads, '
                f'estimated time consuming 0~{self.test_timeout} s'
            )
        return Proxy

    def get_useful_proxies(self, count=sys.maxsize, is_random=False):
        start = time.time()
        self._to_end = False
        valid_proxies = []
        urls = self.urls
        if is_random:
            urls = random.sample(self.urls, len(self.urls))
        for url in urls:
            proxies = self.get_proxies_from_one_page(url)
            with ThreadPoolExecutor(max_workers=self.max_worker) as pool:
                futures = [pool.submit(self._test_proxy, proxy) for proxy in proxies]
                for future in as_completed(futures):
                    proxy = future.result()
                    if proxy.speed != -1:
                        if self.show_logs:
                            logger.info(f'Found a valid anonymous proxy ip: {proxy.ip}:{proxy.port}')
                        valid_proxies.append(proxy)
                        if len(valid_proxies) >= count:
                            self._to_end = True
        end = time.time()
        if len(valid_proxies):
            if self.show_logs:
                logger.info(
                    f'This crawling proxy IP takes: {round(end - start, 2)} s, '
                    f'waiting for the end of other threads, '
                    f'estimated time consuming 0~{self.test_timeout} s'
                )
            return valid_proxies
        if self.show_logs:
            logger.warning('Could not be found a valid anonymous proxy IP')
            logger.info(
                f'This crawling proxy IP takes: {round(end - start, 2)} s, '
                f'waiting for the end of other threads, '
                f'estimated time consuming 0~{self.test_timeout} s'
            )
        return []
