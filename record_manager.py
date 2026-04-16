# -*- coding: utf-8 -*-
"""
下载记录管理模块
支持增量下载，记录已下载的推文 ID
"""

import json
import os
from typing import Set, Optional
from config import RECORD_FILE


class RecordManager:
    """管理下载记录，支持增量下载"""

    def __init__(self, record_file: str = RECORD_FILE):
        self.record_file = record_file
        self.downloaded_tweets: Set[str] = set()
        self.last_cursor: Optional[str] = None
        self.total_downloaded: int = 0
        self._load()

    def _load(self) -> None:
        """从文件加载记录"""
        if os.path.exists(self.record_file):
            try:
                with open(self.record_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.downloaded_tweets = set(data.get('downloaded_tweets', []))
                    self.last_cursor = data.get('last_cursor')
                    self.total_downloaded = data.get('total_downloaded', 0)
                print(f"[记录] 加载完成: 已下载 {len(self.downloaded_tweets)} 个视频")
            except (json.JSONDecodeError, IOError) as e:
                print(f"[记录] 加载失败，将创建新记录: {e}")
                self.downloaded_tweets = set()
        else:
            print("[记录] 未找到记录文件，将创建新记录")

    def save(self) -> None:
        """保存记录到文件"""
        data = {
            'downloaded_tweets': list(self.downloaded_tweets),
            'last_cursor': self.last_cursor,
            'total_downloaded': self.total_downloaded
        }
        with open(self.record_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def is_downloaded(self, tweet_id: str) -> bool:
        """检查推文是否已下载"""
        return tweet_id in self.downloaded_tweets

    def mark_downloaded(self, tweet_id: str) -> None:
        """标记推文为已下载"""
        self.downloaded_tweets.add(tweet_id)
        self.total_downloaded += 1

    def set_cursor(self, cursor: str) -> None:
        """设置分页游标"""
        self.last_cursor = cursor

    def get_cursor(self) -> Optional[str]:
        """获取上次分页游标"""
        return self.last_cursor

    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            'total_downloaded': self.total_downloaded,
            'unique_tweets': len(self.downloaded_tweets)
        }