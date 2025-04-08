from utils.logger import get_logger
from nasa_core.base_spider import BaseSpider
from config.settings import BASE_DIR, CONFIG_DIR, PROXY_POOL_CONFIG
import requests
import threading
import json
import os
from datetime import datetime
import queue
import importlib
import yaml
from typing import Dict

logger = get_logger()


class ProxiesManager():
    """ 爬虫管理"""

    _instance = None
    _initialized = False
    _lock = threading.Lock()
    # 自动初始化时加载缓存

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
            return cls._instance

    def __init__(self):
        if not self._initialized:
            self.headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            self.proxy_spiders: Dict[str, BaseSpider] = {}
            self.proxy_spiders_dir = os.path.join(BASE_DIR, "spiders", "proxy")
            self.proxy_pool = []
            self.proxy_pool_queue = queue.Queue()
            self._crawl_executed = False
            self._initialized = True
            self.cache_file = PROXY_POOL_CONFIG.get("cache_file", os.path.join(BASE_DIR, "cache", "proxies_cache.json"))
            self._load_proxy_spiders()

    def _load_proxy_spiders(self):
        """加载爬虫类"""
        with open(os.path.join(CONFIG_DIR, "spiders_config.yaml"), "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        enabled_proxy_spiders = config.get("enabled_proxy_spiders", [])

        spider_display_names = {
            spider["name"]: spider["display_name"]
            for spider in enabled_proxy_spiders
            if "name" in spider and "display_name" in spider
        }

        for filename in os.listdir(self.proxy_spiders_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                try:
                    module_name = filename[:-3]
                    full_path = f"spiders.proxy.{module_name}"

                    # 动态导入模块
                    module = importlib.import_module(full_path)

                    for name, obj in vars(module).items():
                        if (isinstance(obj, type) and
                            issubclass(obj, BaseSpider) and
                                obj is not BaseSpider):

                            if name not in spider_display_names:
                                continue

                            self.proxy_spiders[spider_display_names[name]] = obj
                            logger.info(f"已加载爬虫类: {name}")
                except Exception as e:
                    logger.error(f"加载爬虫类失败: {filename} - {str(e)}")

    def _load_cache(self):
        """加载本地缓存文件"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    # self.proxy_pool = data['proxies']
                    self.last_update = datetime.fromisoformat(data['last_update'])
                    now = datetime.now()
                    if (now - self.last_update).seconds < PROXY_POOL_CONFIG.get("update_interval", 60):
                        self.proxy_pool = data['proxies']
                        logger.info(f"✅ 已加载缓存代理 ({len(self.proxy_pool)}) 上次更新: {self.last_update}")
                    else:
                        logger.info("⚠️ 缓存代理已过期，重新爬取...")
                        self._refresh_proxies()
            except Exception as e:
                logger.warning(f"⚠️ 缓存加载失败，重建缓存: {str(e)}")
                self._refresh_proxies()
        else:
            self._refresh_proxies()
        for proxy in self.proxy_pool:
            self.proxy_pool_queue.put(proxy)

    def init_proxies(self):
        self._load_cache()
        if not self.proxy_pool:
            without_proxy = input("代理池为空,是否不使用代理继续？(y/n)")
            if without_proxy == "n":
                logger.error("代理池为空，无法获取代理")
                exit(0)

    def fetch(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"请求 {url} 时出错：{e}")
            return None

    def _refresh_proxies(self):
        """自动爬取机制"""
        logger.info("🔄 正在爬取新代理...")
        self.crawl()

        if self.proxy_pool:
            logger.info("🔎 开始检查代理可用性...")
            self.check_proxies()
            logger.info(f"🔎 共爬取到 {len(self.proxy_pool)} 个可用代理")
            self.last_update = datetime.now()
            self._save_cache()

    def _save_cache(self):
        """保存缓存到文件"""
        data = {
            'last_update': datetime.now().isoformat(),
            'proxies': self.proxy_pool
        }
        with open(self.cache_file, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"💾 代理池已缓存 ({len(self.proxy_pool)}个代理)")

    def get_proxies(self):
        if not self.proxy_pool:
            logger.warning("代理池为空")
            return None
        return self.proxy_pool_queue.get()

    def release_proxies(self, proxy):
        self.proxy_pool_queue.put(proxy)

    def get_proxies_count(self):
        return len(self.proxy_pool)

    def crawl(self):
        for name, spider_class in self.proxy_spiders.items():
            try:
                spider = spider_class(self.headers, with_proxy=False)
                html = spider.fetch(spider.url)
                if html:
                    proxies = spider.parse(html)
                    logger.info(f"🔎 代理网站 {name} 共爬取到 {len(proxies)} 个代理")
                    if proxies:
                        self.proxy_pool.extend(proxies)
            except Exception as e:
                logger.error(f"爬取代理失败: {name} - {str(e)}")
                continue

    def check_proxies(self):
        threads = []
        for proxy in self.proxy_pool:
            thread = threading.Thread(target=self._check_proxy, args=(proxy,))
            threads.append(thread)
            thread.start()
        for t in threads:
            t.join()

    def _check_proxy(self, proxy):
        try:
            response = requests.get("https://httpbin.org/ip", proxies=proxy, timeout=10)
            response.raise_for_status()
            logger.debug(f"代理 {proxy} 可用。")
        except Exception as e:
            logger.debug(f"代理 {proxy} 不可用：{e}")
            self.proxy_pool.remove(proxy)
