from parsel import Selector
from nasa_core.base_spider import BaseSpider
from utils.logger import get_logger

logger = get_logger()

PROXIES_URL = "https://www.socks-proxy.net/"


class socksproxySpider(BaseSpider):
    def __init__(self, headers=None, with_proxy=False):
        super().__init__(headers, with_proxy)
        self.url = PROXIES_URL

    def crawl(self):
        for url in self.url:
            html = self.fetch(url)
            if html:
                return self.parse(html)

    def parse(self, html):
        selector = Selector(html)
        proxy_list = []
        for row in selector.css("#list > div > div.table-responsive > div > table > tbody > tr"):
            ip = row.css("td:nth-child(1)::text").get("").strip()
            port = row.css("td:nth-child(2)::text").get("").strip()
            type = row.css("td:nth-child(5)::text").get("").strip()
            if ip and port:
                if type == "elite proxy":
                    proxy_list.append({"http": f"http://{ip}:{port}", "https": f"http://{ip}:{port}"})
                elif type == "Socks4":
                    proxy_list.append({"http": f"socks4://{ip}:{port}", "https": f"socks4://{ip}:{port}"})
        return proxy_list
