# 目标爬取的 URL
FANQIE_URL = {
    '男频阅读榜·科幻末世': 'https://fanqienovel.com/rank/1_2_8',
    '男频阅读榜·都市日常': 'https://fanqienovel.com/rank/1_2_261',
    '男频阅读榜·都市修真': 'https://fanqienovel.com/rank/1_2_124',
    '男频阅读榜·都市高武': 'https://fanqienovel.com/rank/1_2_1014',
    '男频阅读榜·奇幻仙侠': 'https://fanqienovel.com/rank/1_2_259',
    '男频阅读榜·历史古代': 'https://fanqienovel.com/rank/1_2_273',
    '男频阅读榜·战神赘婿': 'https://fanqienovel.com/rank/1_2_27',
    '男频阅读榜·都市种田': 'https://fanqienovel.com/rank/1_2_263',
    '男频阅读榜·传统玄幻': 'https://fanqienovel.com/rank/1_2_258',
    '男频阅读榜·历史脑洞': 'https://fanqienovel.com/rank/1_2_272',
    '男频阅读榜·悬疑脑洞': 'https://fanqienovel.com/rank/1_2_539',
    '男频阅读榜·都市脑洞': 'https://fanqienovel.com/rank/1_2_262',
    '男频阅读榜·玄幻脑洞': 'https://fanqienovel.com/rank/1_2_257',
    '男频阅读榜·悬疑灵异': 'https://fanqienovel.com/rank/1_2_751',
    '男频阅读榜·抗战谍战': 'https://fanqienovel.com/rank/1_2_504',
    '男频阅读榜·游戏体育': 'https://fanqienovel.com/rank/1_2_746',
    '男频阅读榜·动漫衍生': 'https://fanqienovel.com/rank/1_2_718',
    '男频阅读榜·男频衍生': 'https://fanqienovel.com/rank/1_2_1016'
}

BASE_URL = 'https://fanqienovel.com'

# 爬取规则
# SIMPLE-只爬取书籍标题和简介、不爬取标签
# FULL-爬取书籍标题、简介和标签，爬取标签需要遍历书籍详情页

CRAWL_RULE = "SIMPLE"
