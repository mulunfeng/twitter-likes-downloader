# -*- coding: utf-8 -*-
"""
视频下载器
下载视频文件到本地
"""

import os
import time
import requests
from typing import Dict, Any, Optional
from config import DOWNLOAD_DIR, REQUEST_DELAY, PROXY


class Downloader:
    """视频下载器"""

    def __init__(self, download_dir: str = DOWNLOAD_DIR):
        self.download_dir = download_dir
        self._ensure_dir()

    def _ensure_dir(self) -> None:
        """确保下载目录存在"""
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            print(f"[下载] 创建下载目录: {self.download_dir}")

    def download_video(self, video_info: Dict[str, Any]) -> bool:
        """
        下载视频

        Args:
            video_info: 视频信息（包含 URL, tweet_id 等）

        Returns:
            是否下载成功
        """
        url = video_info.get("video_url")
        tweet_id = video_info.get("tweet_id")

        if not url or not tweet_id:
            print("[下载] 缺少必要的视频信息")
            return False

        # 生成文件名
        filename = self._generate_filename(video_info)
        filepath = os.path.join(self.download_dir, filename)

        # 检查文件是否已存在
        if os.path.exists(filepath):
            print(f"[下载] 文件已存在: {filename}")
            return True

        # 检查是否是 HLS (m3u8) 流
        if video_info.get("is_hls"):
            return self._download_hls(url, filepath, video_info)

        # 下载普通 mp4
        return self._download_mp4(url, filepath, video_info)

    def _download_mp4(self, url: str, filepath: str, video_info: Dict[str, Any]) -> bool:
        """下载 mp4 文件"""
        tweet_id = video_info.get("tweet_id")
        bitrate = video_info.get("bitrate", 0)
        resolution = video_info.get("resolution", "unknown")

        print(f"[下载] 开始下载: {tweet_id}")
        print(f"       清晰度: {resolution}, bitrate: {bitrate}")

        try:
            # 使用流式下载
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "https://x.com/"
            }

            # 设置代理
            proxies = None
            if PROXY:
                proxies = {"http": PROXY, "https": PROXY}

            response = requests.get(url, headers=headers, stream=True, timeout=60, proxies=proxies)

            if response.status_code != 200:
                print(f"[下载] HTTP 错误: {response.status_code}")
                return False

            # 获取文件大小
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            # 写入文件
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        # 显示进度
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            if downloaded % (1024 * 1024) < 8192:  # 每MB显示一次
                                size_mb = downloaded / (1024 * 1024)
                                print(f"       进度: {progress:.1f}% ({size_mb:.1f} MB)")

            file_size = os.path.getsize(filepath)
            print(f"[下载] 完成: {filepath} ({file_size / (1024*1024):.1f} MB)")

            # 请求间隔
            time.sleep(REQUEST_DELAY)
            return True

        except requests.RequestException as e:
            print(f"[下载] 下载失败: {e}")
            # 删除不完整的文件
            if os.path.exists(filepath):
                os.remove(filepath)
            return False
        except Exception as e:
            print(f"[下载] 错误: {e}")
            if os.path.exists(filepath):
                os.remove(filepath)
            return False

    def _download_hls(self, url: str, filepath: str, video_info: Dict[str, Any]) -> bool:
        """
        下载 HLS (m3u8) 流

        注意: HLS 流需要 ffmpeg 来处理
        """
        tweet_id = video_info.get("tweet_id")
        print(f"[下载] HLS 流需要 ffmpeg: {tweet_id}")

        # 检查 ffmpeg 是否可用
        import subprocess

        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        except:
            print("[下载] ffmpeg 未安装，无法下载 HLS 流")
            print("       请安装 ffmpeg: https://ffmpeg.org/download.html")
            return False

        # 使用 ffmpeg 下载
        try:
            cmd = [
                "ffmpeg",
                "-i", url,
                "-c", "copy",  # 直接复制流，不重新编码
                "-bsf:a", "aac_adtstoasc",  # 修复 AAC 格式
                filepath
            ]

            print(f"[下载] 使用 ffmpeg 下载 HLS...")
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"[下载] ffmpeg 错误: {result.stderr}")
                return False

            print(f"[下载] HLS 完成: {filepath}")
            return True

        except Exception as e:
            print(f"[下载] HLS 下载失败: {e}")
            return False

    def _generate_filename(self, video_info: Dict[str, Any]) -> str:
        """生成文件名"""
        tweet_id = video_info.get("tweet_id", "unknown")
        created_at = video_info.get("created_at", "")
        resolution = video_info.get("resolution", "unknown")

        from datetime import datetime

        timestamp = ""
        if created_at:
            try:
                dt = datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")
                timestamp = dt.strftime("%Y%m%d_%H%M%S")
            except:
                pass

        # 文件名格式: tweet_id_timestamp_resolution.mp4
        parts = [tweet_id]
        if timestamp:
            parts.append(timestamp)
        if resolution and resolution != "unknown":
            parts.append(resolution.replace("x", "_"))

        filename = "_".join(parts) + ".mp4"
        # 清理无效字符
        filename = filename.replace("/", "_").replace("\\", "_")

        return filename

    def get_downloaded_files(self) -> list:
        """获取已下载的文件列表"""
        if not os.path.exists(self.download_dir):
            return []

        files = []
        for f in os.listdir(self.download_dir):
            if f.endswith(".mp4"):
                files.append(f)

        return files