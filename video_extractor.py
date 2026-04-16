# -*- coding: utf-8 -*-
"""
视频提取器
从推文中提取最高清晰度的视频 URL
"""

from typing import Dict, Any, Optional, List


class VideoExtractor:
    """提取推文中的视频信息"""

    def __init__(self):
        pass

    def get_best_video_url(self, variants: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        从视频变体中选择最高清晰度

        Args:
            variants: 视频变体列表

        Returns:
            最佳视频信息（URL, bitrate, resolution 等）
        """
        if not variants:
            return None

        # 只选择 mp4 格式，按 bitrate 排序
        mp4_variants = []

        for variant in variants:
            url = variant.get("url", "")
            content_type = variant.get("content_type", "")

            # 选择 mp4 格式
            if "mp4" in url or content_type == "video/mp4":
                bitrate = variant.get("bitrate", 0)
                mp4_variants.append({
                    "url": url,
                    "bitrate": bitrate,
                    "content_type": content_type
                })

        if not mp4_variants:
            # 如果没有 mp4，尝试 m3u8
            for variant in variants:
                url = variant.get("url", "")
                if "m3u8" in url:
                    return {
                        "url": url,
                        "bitrate": 0,
                        "content_type": "application/x-mpegURL",
                        "is_hls": True
                    }
            return None

        # 按 bitrate 排序，选择最高的
        mp4_variants.sort(key=lambda x: x["bitrate"], reverse=True)
        best = mp4_variants[0]

        # 解析分辨率（从 URL 中提取）
        resolution = self._parse_resolution(best["url"])
        best["resolution"] = resolution
        best["is_hls"] = False

        return best

    def _parse_resolution(self, url: str) -> str:
        """
        从 URL 中解析分辨率

        Twitter 视频 URL 通常包含分辨率信息，如:
        /vid/1080x1920/... 或 /vid/720x1280/...
        """
        import re

        # 尝试匹配分辨率格式
        match = re.search(r'/(\d+)x(\d+)/', url)
        if match:
            return f"{match.group(1)}x{match.group(2)}"

        # 尝试匹配其他格式
        match = re.search(r'-(\d+)x(\d+)-', url)
        if match:
            return f"{match.group(1)}x{match.group(2)}"

        return "unknown"

    def extract_video_info(self, tweet: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        从推文中提取完整的视频信息

        Args:
            tweet: 推文数据

        Returns:
            视频信息字典
        """
        if not tweet:
            return None

        variants = tweet.get("variants", [])
        if not variants:
            return None

        best_video = self.get_best_video_url(variants)

        if not best_video:
            return None

        return {
            "tweet_id": tweet.get("tweet_id"),
            "video_url": best_video["url"],
            "bitrate": best_video["bitrate"],
            "resolution": best_video.get("resolution", "unknown"),
            "is_hls": best_video.get("is_hls", False),
            "created_at": tweet.get("created_at", ""),
            "text": tweet.get("text", "")
        }

    def get_video_filename(self, tweet_id: str, created_at: str = "") -> str:
        """
        生成视频文件名

        格式: {tweet_id}_{timestamp}.mp4
        """
        from datetime import datetime

        timestamp = ""
        if created_at:
            try:
                # Twitter 时间格式: "Wed Oct 10 20:19:24 +0000 2018"
                dt = datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")
                timestamp = dt.strftime("%Y%m%d_%H%M%S")
            except:
                timestamp = ""

        if timestamp:
            return f"{tweet_id}_{timestamp}.mp4"
        else:
            return f"{tweet_id}.mp4"