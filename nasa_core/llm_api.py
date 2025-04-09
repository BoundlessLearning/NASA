import requests
from config.settings import LLM_API_CONFIG


class LLMAnalyzer:
    def __init__(self):
        self.api_url = LLM_API_CONFIG["api_url"]
        self.api_key = LLM_API_CONFIG["api_key"]
        self.model = LLM_API_CONFIG["model"]

    def analyze(self, text):
        payload = {
            "model": self.model,
            "stream": False,
            "max_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.7,
            "top_k": 50,
            "frequency_penalty": 0.5,
            "n": 1,
            "messages": [
                {
                    "content": "你是一个小说题材分析大师，我提供给你几份小说的简介，你需要提炼出小说的特征和分类，并且统计每个特征的频率。返回格式应为一个json类似[“关键词1”:次数,“关键词2\":次数]，请\
                        确保返回的json格式正确，并且包含所有特征的频率。请注意，返回的json字符串中不能有任何多余的空格和换行符，json最后的键值对后不能有逗号。",
                    "role": "system"
                },
                {
                    "content": text,
                    "role": "user"
                }
            ],
            "stop": []
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        response = requests.post(self.api_url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
