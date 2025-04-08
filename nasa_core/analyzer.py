import matplotlib.pyplot as plt
from wordcloud import WordCloud
from flashtext import KeywordProcessor
from matplotlib.widgets import RadioButtons


class Analyzer:
    def __init__(self, keyword_dict):
        """
        :param keyword_dict: 关键词字典，格式为 { "特征": ["关键词1", "关键词2", ...], ... }
        """
        self.keyword_dict = keyword_dict

    def count_keywords(self, text):
        """
        根据关键词字典统计文本中各特征关键词出现的次数
        """
        feature_counts = {}
        for feature, synonyms in self.keyword_dict.items():
            count = sum(text.count(syn) for syn in synonyms)
            if count > 0:
                feature_counts[feature] = count
        return feature_counts

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

    def generate_wordclouds(self, frequency_dict, font_path, width=800, height=600, background_color='white'):
        """
        根据每个词频数据生成对应的词云，同时合并所有词频数据生成一个'all'词云。

        :param frequency_list: 词频字典列表，每个字典格式为 {词: 词频, ...}
        :param labels: 与词频数据一一对应的标签列表
        :param font_path: 字体文件路径（用于支持中文）
        :param width: 词云宽度
        :param height: 词云高度
        :param background_color: 背景色
        :return: 一个字典，键为各标签（包括'all'），值为对应的词云对象
        """
        wordcloud_dict = {}

        # 为每个单独的词频数据生成词云
        for label, freq in frequency_dict.items():
            wc = WordCloud(
                font_path=font_path,
                background_color=background_color,
                width=width,
                height=height
            ).generate_from_frequencies(freq)
            wordcloud_dict[label] = wc

        # 合并所有词频数据生成'all'词云
        all_freq = {}
        for freq in frequency_dict.values():
            for word, count in freq.items():
                all_freq[word] = all_freq.get(word, 0) + count
        wc_all = WordCloud(
            font_path=font_path,
            background_color=background_color,
            width=width,
            height=height
        ).generate_from_frequencies(all_freq)
        wordcloud_dict['all'] = wc_all

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
