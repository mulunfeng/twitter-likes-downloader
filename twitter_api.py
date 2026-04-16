# -*- coding: utf-8 -*-
"""
Twitter GraphQL API 封装
使用 cookies 认证访问 Twitter 内部 API
"""

import time
import json
import requests
from typing import Optional, Dict, Any, List
from config import (
    COOKIES, HEADERS, BEARER_TOKEN, API_BASE_URL,
    QUERY_ID_USER_BY_SCREEN_NAME, QUERY_ID_LIKES,
    REQUEST_DELAY, MAX_RETRIES, RETRY_DELAY, PAGE_SIZE, PROXY
)


class TwitterAPI:
    """Twitter GraphQL API 封装"""

    def __init__(self):
        self.session = requests.Session()
        self._setup_session()

    def _setup_session(self) -> None:
        """配置会话"""
        # 设置代理
        if PROXY:
            self.session.proxies = {
                "http": PROXY,
                "https": PROXY
            }
            print(f"[API] 使用代理: {PROXY}")

        # 设置 cookies
        for name, value in COOKIES.items():
            self.session.cookies.set(name, value)

        # 设置请求头
        self.session.headers.update(HEADERS)
        self.session.headers["Authorization"] = BEARER_TOKEN

        # 从 cookies 设置 CSRF token
        if "ct0" in COOKIES:
            self.session.headers["X-Csrf-Token"] = COOKIES["ct0"]

    def _request(self, url: str, params: Dict = None) -> Optional[Dict[str, Any]]:
        """发送 API 请求"""
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(url, params=params)

                # 检查速率限制
                if response.status_code == 429:
                    print(f"[API] 速率限制，等待 {RETRY_DELAY} 秒后重试...")
                    time.sleep(RETRY_DELAY)
                    continue

                # 检查认证错误
                if response.status_code == 401:
                    print("[API] 认证失败，请检查 cookies 是否有效")
                    return None

                # 检查其他错误
                if response.status_code != 200:
                    print(f"[API] 请求失败: HTTP {response.status_code}")
                    print(f"[API] 响应: {response.text[:500]}")
                    return None

                # 请求间隔
                time.sleep(REQUEST_DELAY)
                return response.json()

            except requests.RequestException as e:
                print(f"[API] 请求异常: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                return None

        return None

    def get_user_id(self, screen_name: str) -> Optional[str]:
        """
        通过用户名获取用户 ID

        Args:
            screen_name: Twitter 用户名（不含 @）

        Returns:
            用户 ID 或 None
        """
        url = f"{API_BASE_URL}/{QUERY_ID_USER_BY_SCREEN_NAME}/UserByScreenName"

        variables = {
            "screen_name": screen_name,
            "withSafetyModeUserFields": True
        }

        features = {
            "hidden_profile_likes_enabled": True,
            "hidden_profile_subscriptions_enabled": True,
            "creator_subscriptions_tweet_preview_api_enabled": True,
            "highlights_tweets_tab_ui_enabled": True,
            "profile_label_improvements_pcf_label_in_post_enabled": True,
        }

        params = {
            "variables": json.dumps(variables),
            "features": json.dumps(features)
        }

        print(f"[API] 获取用户 ID: @{screen_name}")
        data = self._request(url, params)

        if data and "data" in data:
            user = data["data"].get("user", {}).get("result", {})
            user_id = user.get("rest_id")
            if user_id:
                print(f"[API] 用户 ID: {user_id}")
                return user_id

        print("[API] 未能获取用户 ID")
        return None

    def get_likes(self, user_id: str, cursor: str = None) -> Optional[Dict[str, Any]]:
        """
        获取用户点赞的推文

        Args:
            user_id: 用户 ID
            cursor: 分页游标（可选）

        Returns:
            包含推文列表和下一页游标的字典，或 None
        """
        url = f"{API_BASE_URL}/{QUERY_ID_LIKES}/Likes"

        variables = {
            "userId": user_id,
            "count": PAGE_SIZE,
            "includePromotedContent": False,
            "withClientEventToken": False,
            "withBirdwatchNotes": False,
            "withVoice": True,
            "withV2Timeline": True
        }

        if cursor:
            variables["cursor"] = cursor

        features = {
            "profile_label_improvements_pcf_label_in_post_enabled": True,
            "rweb_tipjar_consumption_enabled": True,
            "responsive_web_graphql_exclude_directive_enabled": True,
            "verified_phone_label_enabled": False,
            "creator_subscriptions_tweet_preview_api_enabled": True,
            "responsive_web_graphql_timeline_navigation_enabled": True,
            "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
            "communities_web_enable_tweet_community_results_fetch": True,
            "c9s_tweet_anatomy_moderator_badge_enabled": True,
            "articles_preview_enabled": True,
            "responsive_web_edit_tweet_api_enabled": True,
            "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
            "view_counts_everywhere_api_enabled": True,
            "longform_notetweets_consumption_enabled": True,
            "responsive_web_twitter_article_tweet_consumption_enabled": True,
            "tweet_awards_web_tipping_enabled": False,
            "creator_subscriptions_quote_tweet_preview_enabled": False,
            "freedom_of_speech_not_reach_fetch_enabled": True,
            "standardized_nudges_misinfo": True,
            "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
            "rweb_video_timestamps_enabled": True,
            "longform_notetweets_rich_text_read_enabled": True,
            "longform_notetweets_inline_media_enabled": True,
            "responsive_web_enhance_cards_enabled": False
        }

        params = {
            "variables": json.dumps(variables),
            "features": json.dumps(features)
        }

        print(f"[API] 获取 Likes... (cursor: {cursor[:20] if cursor else 'None'}...)" )
        data = self._request(url, params)

        if data and "data" in data:
            return self._parse_likes_response(data)

        return None

    def _parse_likes_response(self, data: Dict) -> Dict[str, Any]:
        """解析 Likes API 响应"""
        result = {
            "tweets": [],
            "next_cursor": None,
            "has_more": False
        }

        try:
            # 导航到推文列表 - 新结构使用 timeline 而不是 timeline_v2
            user = data.get("data", {}).get("user", {}).get("result", {})

            # 尝试两种结构
            timeline_data = user.get("timeline", {})
            if timeline_data:
                timeline = timeline_data.get("timeline", {})
            else:
                timeline = user.get("timeline_v2", {}).get("timeline", {})

            instructions = timeline.get("instructions", [])

            entries = []
            for instruction in instructions:
                # 新结构: entries 直接在 instruction 中
                if "entries" in instruction:
                    entries.extend(instruction.get("entries", []))
                # 老结构: type 为 TimelineAddEntries
                elif instruction.get("type") == "TimelineAddEntries":
                    entries.extend(instruction.get("entries", []))

            for entry in entries:
                entry_id = entry.get("entryId", "")

                # 提取分页游标 - 多种格式
                if "cursor-bottom" in entry_id or "cursor" in entry_id.lower():
                    content = entry.get("content", {})
                    # 新结构可能使用 itemContent
                    if "itemContent" in content:
                        result["next_cursor"] = content.get("itemContent", {}).get("value")
                    else:
                        result["next_cursor"] = content.get("value")
                    result["has_more"] = True

                # 提取推文 - entryId 可能以 tweet- 开头，或者直接包含 ID
                elif entry_id.startswith("tweet-") or entry_id.isdigit():
                    content = entry.get("content", {})

                    # 新结构: itemContent
                    item_content = content.get("itemContent", content)
                    tweet_data = item_content.get("tweet_results", {}).get("result", {})

                    if tweet_data:
                        # 检查是否有视频
                        tweet_id = tweet_data.get("rest_id")
                        legacy = tweet_data.get("legacy", {})

                        # 检查 extended_entities 中的视频
                        extended_entities = legacy.get("extended_entities", {})
                        media = extended_entities.get("media", [])

                        for m in media:
                            if m.get("type") == "video":
                                video_info = m.get("video_info", {})
                                variants = video_info.get("variants", [])

                                if variants:
                                    # 获取推文创建时间
                                    created_at = legacy.get("created_at", "")

                                    result["tweets"].append({
                                        "tweet_id": tweet_id,
                                        "created_at": created_at,
                                        "video_info": video_info,
                                        "variants": variants,
                                        "text": legacy.get("full_text", "")
                                    })
                                    break

        except Exception as e:
            print(f"[API] 解析响应失败: {e}")
            import traceback
            traceback.print_exc()

        return result

    def get_all_likes_with_videos(self, user_id: str, callback=None) -> List[Dict[str, Any]]:
        """
        获取所有包含视频的点赞推文

        Args:
            user_id: 用户 ID
            callback: 每页处理回调函数，用于增量处理

        Returns:
            包含视频的推文列表
        """
        all_tweets = []
        cursor = None
        page = 1

        while True:
            print(f"[API] 正在获取第 {page} 页...")

            result = self.get_likes(user_id, cursor)

            if not result:
                print("[API] 获取失败或无更多数据")
                break

            tweets = result.get("tweets", [])

            if tweets:
                all_tweets.extend(tweets)
                print(f"[API] 本页发现 {len(tweets)} 个视频推文")

                # 调用回调函数
                if callback:
                    callback(tweets)

            # 检查是否有下一页
            if not result.get("has_more") or not result.get("next_cursor"):
                print("[API] 已获取所有数据")
                break

            cursor = result.get("next_cursor")
            page += 1

        print(f"[API] 总计发现 {len(all_tweets)} 个视频推文")
        return all_tweets