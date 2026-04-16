# -*- coding: utf-8 -*-
"""
提取 Twitter GraphQL Query IDs
"""

import re
import requests

PROXY = "http://127.0.0.1:10808"

def get_all_query_ids():
    """提取所有 query IDs"""

    session = requests.Session()
    session.proxies = {"http": PROXY, "https": PROXY}

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    js_url = "https://abs.twimg.com/responsive-web/client-web/main.9994910a.js"

    print(f"[获取] {js_url}")
    response = session.get(js_url, headers=headers, timeout=30)
    js_content = response.text

    # 提取所有 queryId 和 operationName
    pattern = r'queryId:"([^"]+)",operationName:"([^"]+)"'
    matches = re.findall(pattern, js_content)

    print(f"\n[结果] 找到 {len(matches)} 个 GraphQL operations:")
    print("=" * 60)

    operations = {}
    for qid, op_name in matches:
        operations[op_name] = qid
        print(f"  {op_name}: {qid}")

    print("=" * 60)

    # 特别显示我们需要的 IDs
    print("\n[关键] 需要的 Query IDs:")
    if "UserByScreenName" in operations:
        print(f'  QUERY_ID_USER_BY_SCREEN_NAME = "{operations["UserByScreenName"]}"')

    # Likes 可能叫 GetUserLikes 或其他名字
    likes_ops = [k for k in operations.keys() if "Like" in k or "likes" in k.lower()]
    if likes_ops:
        for op in likes_ops:
            print(f'  # {op} = "{operations[op]}"')

    return operations

if __name__ == "__main__":
    ops = get_all_query_ids()