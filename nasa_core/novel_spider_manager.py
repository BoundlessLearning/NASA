import json
from nasa_core.analyzer import KeywordAnalyzer, WordCloudGenerator
from typing import Dict
import os
import yaml
from config.settings import BASE_DIR, CONFIG_DIR, ANALYZER_MODE
from nasa_core.base_spider import BaseSpider
import importlib
from utils.logger import get_logger

# 假设已有以下组件
logger = get_logger()


class NovelSpiderManager:
    """多网站爬虫管理分析器"""

    def __init__(self, keywords_path: str, font_path: str):
        """
        Args:
            keywords_path: 关键词配置文件路径
            font_path: 词云字体文件路径
        """
        self.keyword_dict = self._load_keywords(keywords_path)
        self.novel_spiders_dir = os.path.join(BASE_DIR, "spiders", "novel_sites")
        self.font_path = font_path
        self.spiders: Dict[str, BaseSpider] = {}  # 存储注册的爬虫实例
        self.results = {}  # type: Dict[str, dict]  # 存储分析结果
        self.feature_counts = {}  # type: Dict[str, dict]  # 存储特征统计结果
        self._load_novel_spiders()

    @staticmethod
    def _load_keywords(path: str) -> Dict:
        """加载关键词配置"""
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_novel_spiders(self) -> None:
        """从指定目录动态加载并注册爬虫类
        Args:
            directory: 包含爬虫类的目录路径
        """
        with open(os.path.join(CONFIG_DIR, "spiders_config.yaml"), "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        enabled_novel_spiders = config.get("enabled_novel_spiders", [])

        spider_display_names = {
            spider["name"]: spider["display_name"]
            for spider in enabled_novel_spiders
            if "name" in spider and "display_name" in spider
        }

        for root, _, files in os.walk(self.novel_spiders_dir):
            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    try:
                        module_name = os.path.splitext(file)[0]
                        relative_path = os.path.relpath(root, BASE_DIR).replace(os.sep, ".")
                        full_path = f"{relative_path}.{module_name}"

                        # 动态导入模块
                        module = importlib.import_module(full_path)

                        for name, obj in vars(module).items():
                            if (isinstance(obj, type) and
                                issubclass(obj, BaseSpider) and
                                    obj is not BaseSpider):

                                if name not in spider_display_names:
                                    continue

                                self.spiders[spider_display_names[name]] = obj
                                logger.info(f"已加载爬虫类: {name}")
                    except Exception as e:
                        logger.error(f"加载爬虫类失败: {file} - {str(e)}")

    def run_all(self) -> None:
        """执行所有爬虫并分析数据"""
        if not self.spiders:
            logger.warning("未注册任何爬虫实例")
            return
        self.all_text = {}
        for name, spider_class in self.spiders.items():
            try:
                # 执行爬取
                spider = spider_class()
                processed_text = spider.crawl()
                if not processed_text:
                    logger.error(f"[{name}] 未爬取到有效内容")
                    continue
                self.all_text[name] = processed_text

                # 分析数据
                # analyzer = KeywordAnalyzer(self.keyword_dict)
                # self.feature_counts[name] = analyzer.count_keywords(processed_text, mode=ANALYZER_MODE)
            except Exception as e:
                logger.error(f"[{name}] 执行失败：{e}")
                continue
        # 统计特征
        if self.all_text:
            analyzer = KeywordAnalyzer(self.keyword_dict)
            self.feature_counts = analyzer.count_keywords(self.all_text, mode=ANALYZER_MODE)
            all_frequency = {}
            for freq in self.feature_counts.values():
                for word, count in freq.items():
                    all_frequency[word] = all_frequency.get(word, 0) + count
            self.feature_counts["全部"] = all_frequency
        # 生成词云
        if self.feature_counts:
            word_cloud_generator = WordCloudGenerator(self.font_path)
            wordclouds = word_cloud_generator.generate_wordcloud(self.feature_counts)
            word_cloud_generator.show_wordcloud(wordclouds)
        else:
            logger.info("所有爬虫均未检测到任何关键词。")

    def print_feature_counts(self) -> None:
        """打印特征统计结果"""
        logger.info("关键词统计结果：")
        for feature, count in self.feature_counts.items():
            print(f"{feature}: {count}")
