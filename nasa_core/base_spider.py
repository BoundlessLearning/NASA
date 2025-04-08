import requests
from utils.logger import get_logger
from config.settings import MAX_RETRY

logger = get_logger()


class BaseSpider:
    def __init__(self, headers=None, with_proxy=False):
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.with_proxy = with_proxy
        from nasa_core.proxies_manager import ProxiesManager
        self.Proxy_manager = ProxiesManager()

    def fetch(self, url
              ):
        proxy = None
        if self.with_proxy:
            proxy = self.Proxy_manager.get_proxies()
        retries = MAX_RETRY
        for attempt in range(retries):
            try:
                response = requests.get(url, headers=self.headers, proxies=proxy, timeout=10)
                response.raise_for_status()
                return response.text
            except Exception as e:
                logger.debug(f"请求 {url} 时出错，（尝试 {attempt + 1}/{retries}）：{e}")
                if proxy:
                    self.Proxy_manager.release_proxies(proxy)
                if attempt < retries - 1:
                    if self.with_proxy:
                        logger.debug(f"正在使用新的代理：{proxy}")
                        proxy = self.Proxy_manager.get_proxies()
                if attempt == retries - 1:
                    logger.error(f"请求 {url} 失败，已达到最大重试次数")
                    return None
            finally:
                if proxy:
                    self.Proxy_manager.release_proxies(proxy)

    def parse(self, html):
        raise NotImplementedError("子类必须实现 parse 方法")
