# -*- coding: utf-8 -*-
"""
Twitter/X Likes 视频下载器 - 配置文件模板
请复制此文件为 config.py 并填入你的实际配置
"""

# Twitter Cookies 认证信息
# 获取方法：登录 x.com → F12 → Application → Cookies
# 复制 auth_token 和 ct0 的值
COOKIES = {
    "auth_token": "你的auth_token",
    "ct0": "你的ct0值"
}

# 目标用户 screen_name（不含 @）
TARGET_USER = "your_target_username"

# 下载目录
DOWNLOAD_DIR = "download"

# 下载记录文件
RECORD_FILE = "download_record.json"

# Twitter API 相关配置
API_BASE_URL = "https://x.com/i/api/graphql"

# Twitter GraphQL Query IDs（可能需要定期更新）
# 运行 py extract_ids.py 获取最新值
QUERY_ID_USER_BY_SCREEN_NAME = "IGgvgiOx4QZndDHuD3x9TQ"
QUERY_ID_LIKES = "KPuet6dGbC8LB2sOLx7tZQ"

# Bearer Token（Twitter 公开值）
BEARER_TOKEN = "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"

# 请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Origin": "https://x.com",
    "Referer": "https://x.com/",
    "X-Twitter-Auth-Type": "OAuth2Session",
    "X-Twitter-Active-User": "yes",
    "X-Twitter-Client-Language": "zh-cn",
}

# 请求配置
REQUEST_DELAY = 1.5  # 请求间隔（秒）
MAX_RETRIES = 3      # 最大重试次数
RETRY_DELAY = 30     # 重试间隔（秒）
PAGE_SIZE = 20       # 每页获取数量

# 代理设置（如需要访问 Twitter）
# 格式: "http://127.0.0.1:端口" 或 "socks5://127.0.0.1:端口"
# 不需要代理则设为 None
PROXY = "http://127.0.0.1:10808"