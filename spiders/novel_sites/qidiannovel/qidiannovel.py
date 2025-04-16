from parsel import Selector
from nasa_core.base_spider import BaseSpider
from utils.logger import get_logger
from nasa_core.proxies_manager import ProxiesManager
from spiders.novel_sites.qidiannovel.settings import QIDIAN_URL, CRAWL_PAGE
from concurrent.futures import ThreadPoolExecutor

logger = get_logger()


class QidianNovelSpider(BaseSpider):
    def __init__(self, headers=None, with_proxy=False):
        super().__init__(headers, with_proxy)
        self.urls = {}
        for i in range(1, CRAWL_PAGE + 1):
            self.urls[f"第{i}页"] = f"{QIDIAN_URL}page{i}/"

    def crawl(self) -> list:
        decoded_text_list = []
        max_workers = ProxiesManager().get_proxies_count() or 1
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for name, url in self.urls.items():
                # 提交任务到线程池
                future = executor.submit(
                    self.crawl_task,
                    url=url,
                    task_name=name,
                )
                futures.append(future)

            # 收集结果
            for future in futures:
                result = future.result()
                if result:
                    decoded_text_list.extend(result)
        if decoded_text_list:
            return decoded_text_list
        return None

    def crawl_task(self, url, task_name):
        logger.info(f"🚀 正在爬取榜单{task_name}")
        html = self.selenium_fetch(url)
        if html:
            content_list = self.parse(html)
            # 番茄小说网站的内容经过了字符映射转换，需要解密
            return content_list
        return None

    def parse(self, html):
        content_list = []
        selector = Selector(html)
        # 根据实际页面结构提取目标文本

        book_titles = selector.css('div.book-mid-info h2 a::text').getall()
        book_abstracts = selector.css('div.book-mid-info p.intro::text').getall()
        for title, abstract in zip(book_titles, book_abstracts):
            book_content = title + " " + abstract
            content_list.append(book_content)

        if content_list:
            return content_list
        if not content_list:
            logger.warning("页面中未提取到内容，请检查选择器或页面结构。")
        return content_list


if __name__ == "__main__":
    spider = QidianNovelSpider()
    result = spider.crawl()
    if result:
        for i, content in enumerate(result):
            print(f"内容 {i + 1}: {content}")
    else:
        print("未爬取到任何内容。")
