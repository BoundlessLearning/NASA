from nasa_core.base_spider import BaseSpider
from utils.logger import get_logger
import json

logger = get_logger()

PROXIES_URL = "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&country=cn&proxy_format=protocolipport&format=json&timeout=20000"


class proxyscrapeSpider(BaseSpider):
    def __init__(self, headers=None, with_proxy=False):
        super().__init__(headers, with_proxy)
        self.url = PROXIES_URL
        self.enabled = True

    def crawl(self):
        for url in self.url:
            proxies_json = self.fetch(url)
            if proxies_json:
                return self.parse(proxies_json)

    def parse(self, proxies_json):
        proxies_json = json.loads(proxies_json)
        proxies = proxies_json["proxies"]
        proxy_list = []
        for proxy in proxies:
            ip = proxy.get("ip")
            port = proxy.get("port")
            type = proxy.get("protocol")
            if ip and port:
                if type == "http":
                    proxy_list.append({"http": f"http://{ip}:{port}", "https": f"http://{ip}:{port}"})
                elif type == "socks4":
                    proxy_list.append({"http": f"socks4://{ip}:{port}", "https": f"socks4://{ip}:{port}"})
        return proxy_list
