class Proxy(object):
    def __init__(self, ip='null', port='null', speed=-1, area='null', url='null', obtain_time='null'):
        """
        :param url: 来源url
        :param obtain_time: 获取时间
        """
        self.ip = ip
        self.port = port
        self.speed = speed
        self.area = area
        self.url = url
        self.obtain_time = obtain_time
