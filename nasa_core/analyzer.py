import matplotlib.pyplot as plt
from wordcloud import WordCloud
from flashtext import KeywordProcessor
from matplotlib.widgets import RadioButtons
from nasa_core.llm_api import LLMAnalyzer
import json
from utils.logger import get_logger

logger = get_logger()


class KeywordAnalyzer:
    def __init__(self, keyword_dict):
        """
        :param keyword_dict: 关键词字典，格式为 { "特征": ["关键词1", "关键词2", ...], ... }
        """
        self.keyword_dict = keyword_dict
        self.llm_analyzer = LLMAnalyzer()

    def count_keywords(self, text, mode='flashtext'):
        """
        根据关键词字典统计文本中各特征关键词出现的次数
        """
        if mode == 'flashtext':
            logger.info("使用 Flashtext 模式进行关键词统计")
            return self.count_keywords_flashtext(text)
        elif mode == 'llm':
            logger.info("使用大语言模型进行关键词统计")
            return self.count_keywords_llm(text)
        else:
            raise ValueError("Unsupported mode. Use 'flashtext' or 'llm'.")

    def count_keywords_flashtext(self, text_list):
        # 构造 KeywordProcessor，并启用最长匹配模式
        kp = KeywordProcessor(case_sensitive=True)
        # 为了区分不同标签，可以分别添加关键词
        for feature, synonyms in self.keyword_dict.items():
            for syn in synonyms:
                kp.add_keyword(syn, feature)

        counts = {}
        # extract_keywords 返回的是标签列表
        for text in text_list:
            features = set(kp.extract_keywords(text, span_info=False))
            for feature in features:
                counts[feature] = counts.get(feature, 0) + 1
        return counts

    def count_keywords_llm(self, text_list):
        """
        使用 LLM 模型统计文本中各特征关键词出现的次数
        """
        content = "\n".join(text_list)
        try:
            response = self.llm_analyzer.analyze(content)
            # 解析 LLM 返回的数据
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            json_str = content.strip('```json\n').strip('```').strip()
            counts = json.loads(json_str)
            if isinstance(counts, dict):
                return counts
        except Exception as e:
            print(f"LLM 分析失败: {e}")
            return {}


class WordCloudGenerator:
    def __init__(self, font_path, width=800, height=600, background_color='white'):
        self.font_path = font_path
        self.width = width
        self.height = height
        self.background_color = background_color

    def generate_wordcloud(self, frequency_dict):
        """
        根据词频数据生成词云
        """
        wordcloud_dict = {}
        for label, freq in frequency_dict.items():
            wc = WordCloud(
                font_path=self.font_path,
                background_color=self.background_color,
                width=self.width,
                height=self.height
            ).generate_from_frequencies(freq)
            wordcloud_dict[label] = wc

        # 合并所有词频数据生成 'all' 词云
        all_freq = {}
        for freq in frequency_dict.values():
            for word, count in freq.items():
                all_freq[word] = all_freq.get(word, 0) + count
        wordcloud_dict['all'] = WordCloud(
            font_path=self.font_path,
            background_color=self.background_color,
            width=self.width,
            height=self.height
        ).generate_from_frequencies(all_freq)

        return wordcloud_dict

    def show_wordcloud(self, wordcloud_dict):
        """
        显示词云图，并使用 RadioButtons 切换显示不同标签的词云。

        :param wordcloud_dict: 键为标签，值为对应的词云对象
        """
        plt.rcParams['font.family'] = "SimHei"  # 设置字体为黑体
        fig, ax = plt.subplots()
        plt.subplots_adjust(left=0.3)  # 给侧边的控件留出空间

        # 默认显示第一个标签对应的词云
        initial_label = list(wordcloud_dict.keys())[0]
        image = ax.imshow(wordcloud_dict[initial_label], interpolation='bilinear')
        ax.axis("off")

        # 在左侧创建 RadioButtons 控件
        ax_radio = plt.axes([0.05, 0.4, 0.15, 0.15])
        radio = RadioButtons(ax_radio, list(wordcloud_dict.keys()))

        def update(label):
            image.set_data(wordcloud_dict[label])
            fig.canvas.draw_idle()

        radio.on_clicked(update)
        plt.show()
