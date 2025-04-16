import requests
from utils.logger import get_logger
from config.settings import MAX_RETRY
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

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
        new_proxy = None
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
                if attempt < retries - 1:
                    if self.with_proxy:
                        logger.debug(f"正在使用新的代理：{proxy}")
                        new_proxy = self.Proxy_manager.get_proxies()
                if attempt == retries - 1:
                    logger.error(f"请求 {url} 失败，已达到最大重试次数")
                    return None
            finally:
                if proxy:
                    self.Proxy_manager.release_proxies(proxy)
                if new_proxy:
                    proxy = new_proxy

    def selenium_fetch(self, url):
        proxy = None
        new_proxy = None
        options = Options()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
        # options.add_argument('--headless')  # 无头模式
        options.add_argument("--disable-logging")  # 禁用日志
        if self.with_proxy:
            proxy = self.Proxy_manager.get_proxies()
            options.add_argument(f"--proxy-server={proxy['http']}" if proxy else "")
        retries = MAX_RETRY
        for attempt in range(retries):
            try:
                driver = webdriver.Chrome(options=options)
                driver.get(url)
                html = driver.page_source
                if html:
                    return html
            except Exception as e:
                logger.debug(f"使用 Selenium 爬取 {url} 时出错，（尝试 {attempt + 1}/{retries}）：{e}")
                if attempt < retries - 1:
                    if self.with_proxy:
                        logger.debug(f"正在使用新的代理：{proxy}")
                        new_proxy = self.Proxy_manager.get_proxies()
            finally:
                if proxy:
                    self.Proxy_manager.release_proxies(proxy)
                if new_proxy:
                    proxy = new_proxy
                if driver:
                    driver.quit()
        return None

    def parse(self, html):
        raise NotImplementedError("子类必须实现 parse 方法")
