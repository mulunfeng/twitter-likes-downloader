# -*- coding: utf-8 -*-
"""
Twitter/X Likes 视频下载器
主入口程序

功能:
1. 读取指定用户点赞的推文中的视频
2. 下载最高清晰度的视频
3. 支持增量下载（记录已下载的推文）
4. 保存到 download 目录
5. 只下载最新的50个视频，新增的likes也会自动下载
"""

import sys
from config import TARGET_USER
from twitter_api import TwitterAPI
from video_extractor import VideoExtractor
from downloader import Downloader
from record_manager import RecordManager

# 最大下载数量
MAX_VIDEOS = 50


def main():
    """主函数"""
    print("=" * 60)
    print("Twitter/X Likes 视频下载器")
    print("=" * 60)
    print(f"目标用户: @{TARGET_USER}")
    print(f"最大下载: {MAX_VIDEOS} 个最新视频")
    print("=" * 60)

    # 初始化各模块
    api = TwitterAPI()
    extractor = VideoExtractor()
    downloader = Downloader()
    record_manager = RecordManager()

    # 步骤 1: 获取用户 ID
    print("\n[步骤 1] 获取用户信息...")
    user_id = api.get_user_id(TARGET_USER)

    if not user_id:
        print("[错误] 无法获取用户 ID，请检查:")
        print("  1. 用户名是否正确")
        print("  2. Cookies 是否有效（可能已过期）")
        print("  3. 网络连接是否正常")
        sys.exit(1)

    # 步骤 2: 获取点赞的推文（含视频）
    print("\n[步骤 2] 获取最新的点赞视频推文...")

    downloaded_count = 0
    skipped_count = 0
    total_processed = 0  # 已处理的视频推文总数
    stop_flag = False

    def process_tweets(tweets):
        """处理每页获取的推文"""
        nonlocal downloaded_count, skipped_count, total_processed, stop_flag

        for tweet in tweets:
            # 检查是否达到上限
            if total_processed >= MAX_VIDEOS:
                print(f"\n[停止] 已处理 {MAX_VIDEOS} 个视频推文，停止获取更多")
                stop_flag = True
                return

            total_processed += 1
            tweet_id = tweet.get("tweet_id")

            # 检查是否已下载
            if record_manager.is_downloaded(tweet_id):
                print(f"[跳过] 推文 {tweet_id} 已下载 ({total_processed}/{MAX_VIDEOS})")
                skipped_count += 1
                continue

            # 提取视频信息
            video_info = extractor.extract_video_info(tweet)

            if not video_info:
                print(f"[警告] 无法提取视频信息: {tweet_id}")
                continue

            # 下载视频
            print(f"[下载] 推文 {tweet_id} ({total_processed}/{MAX_VIDEOS})")
            success = downloader.download_video(video_info)

            if success:
                # 记录下载
                record_manager.mark_downloaded(tweet_id)
                downloaded_count += 1
                # 保存记录（每次下载后保存，防止中断丢失）
                record_manager.save()

    # 获取并处理点赞推文（带停止条件）
    page = 1
    cursor = None

    while not stop_flag:
        print(f"\n[API] 正在获取第 {page} 页...")

        result = api.get_likes(user_id, cursor)

        if not result:
            print("[API] 获取失败或无更多数据")
            break

        tweets = result.get("tweets", [])

        if tweets:
            print(f"[API] 本页发现 {len(tweets)} 个视频推文")
            process_tweets(tweets)

        # 检查停止标志或是否有下一页
        if stop_flag:
            break

        if not result.get("has_more") or not result.get("next_cursor"):
            print("[API] 已获取所有数据")
            break

        cursor = result.get("next_cursor")
        page += 1

    # 最终保存记录
    record_manager.save()

    # 输出统计
    print("\n" + "=" * 60)
    print("下载完成!")
    print("=" * 60)
    stats = record_manager.get_stats()
    print(f"本次下载: {downloaded_count} 个视频")
    print(f"本次跳过: {skipped_count} 个已下载视频")
    print(f"本次处理: {total_processed} 个视频推文")
    print(f"历史总计: {stats['unique_tweets']} 个视频")
    print(f"下载目录: {downloader.download_dir}")

    # 列出已下载文件
    files = downloader.get_downloaded_files()
    if files:
        print(f"\n已下载文件列表 ({len(files)} 个):")
        for f in files[:10]:  # 只显示前10个
            print(f"  - {f}")
        if len(files) > 10:
            print(f"  ... 还有 {len(files) - 10} 个文件")

    print("=" * 60)


if __name__ == "__main__":
    main()