import os

# 项目根目录（假设 config 文件夹位于项目根目录下）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG_DIR = os.path.join(BASE_DIR, 'config')

# 中文字体文件路径（生成词云需要支持中文的字体）
FONT_PATH = 'simhei.ttf'  # 替换为你的字体文件路径

# 请求失败时，最大重试次数
MAX_RETRY = 3

# 代理池配置
PROXY_POOL_CONFIG = {
    "enabled": True,
    "update_interval": 60,  # 更新间隔（秒）
    "cache_file": os.path.join(BASE_DIR, 'proxies.json'),  # 缓存文件路径
}
