# main.py
import json
import os
from config.settings import FONT_PATH, PROXY_POOL_CONFIG
from utils.logger import get_logger
from nasa_core.proxies_manager import ProxiesManager
from nasa_core.novel_spider_manager import NovelSpiderManager

logger = get_logger()


def load_keywords(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    logger.info("启动小说趋势雷达...")

    if PROXY_POOL_CONFIG.get("enabled", False):
        logger.info("代理池已启用，正在初始化...")
        # 初始化代理池
        proxies_manager = ProxiesManager()
        proxies_manager.init_proxies()

    # 实例化爬虫并爬取数据

    novel_spider_manager = NovelSpiderManager(keywords_path=os.path.join(os.path.dirname(__file__), "config", "keywords.json"), font_path=FONT_PATH)

    novel_spider_manager.run_all()

    novel_spider_manager.print_feature_counts()


if __name__ == "__main__":
    main()
