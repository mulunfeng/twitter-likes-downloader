# -*- coding: utf-8 -*-
"""
Twitter/X Likes 视频下载器
主入口程序

功能:
1. 读取指定用户点赞的推文中的视频
2. 下载最高清晰度的视频
3. 支持增量下载（记录已下载的推文）
4. 保存到 download 目录
5. 监控模式：长时间运行，自动下载新增的 likes 视频

用法:
  python main.py              # 单次运行，下载最新50个
  python main.py --watch      # 监控模式，持续运行
  python main.py --watch --interval 10  # 自定义检查间隔（分钟）
"""

import sys
import time
import argparse
from datetime import datetime
from config import TARGET_USER
from twitter_api import TwitterAPI
from video_extractor import VideoExtractor
from downloader import Downloader
from record_manager import RecordManager

# 默认最大检查数量（单次运行模式）
MAX_VIDEOS = 50

# 监控模式默认检查间隔（分钟）
DEFAULT_INTERVAL = 10


def check_new_videos(api, extractor, downloader, record_manager, user_id, max_check=100):
    """
    检查并下载新视频

    Args:
        max_check: 最大检查数量（监控模式下多检查一些）

    Returns:
        (downloaded_count, skipped_count, total_checked)
    """
    downloaded_count = 0
    skipped_count = 0
    total_checked = 0
    stop_flag = False

    def process_tweets(tweets):
        """处理每页获取的推文"""
        nonlocal downloaded_count, skipped_count, total_checked, stop_flag

        for tweet in tweets:
            if total_checked >= max_check:
                stop_flag = True
                return

            total_checked += 1
            tweet_id = tweet.get("tweet_id")

            # 检查是否已下载
            if record_manager.is_downloaded(tweet_id):
                skipped_count += 1
                # 监控模式下，遇到连续多个已下载的就停止（说明没有新视频了）
                if skipped_count >= 10 and downloaded_count == 0:
                    print(f"[监控] 遇到连续已下载视频，无需继续检查")
                    stop_flag = True
                    return
                continue

            # 发现新视频！
            video_info = extractor.extract_video_info(tweet)

            if not video_info:
                print(f"[警告] 无法提取视频信息: {tweet_id}")
                continue

            # 下载视频
            print(f"\n[新视频] 发现新视频: {tweet_id}")
            success = downloader.download_video(video_info)

            if success:
                record_manager.mark_downloaded(tweet_id)
                downloaded_count += 1
                record_manager.save()
                skipped_count = 0  # 重置跳过计数

    # 获取并处理点赞推文
    cursor = None
    page = 1

    while not stop_flag:
        result = api.get_likes(user_id, cursor)

        if not result:
            break

        tweets = result.get("tweets", [])
        if tweets:
            process_tweets(tweets)

        if stop_flag:
            break

        if not result.get("has_more") or not result.get("next_cursor"):
            break

        cursor = result.get("next_cursor")
        page += 1

    return downloaded_count, skipped_count, total_checked


def run_single_mode(api, extractor, downloader, record_manager, user_id):
    """单次运行模式"""
    print(f"\n目标用户: @{TARGET_USER} (ID: {user_id})")

    # 初始化计数
    downloaded_count = 0
    skipped_count = 0
    total_processed = 0
    stop_flag = False

    def process_tweets(tweets):
        nonlocal downloaded_count, skipped_count, total_processed, stop_flag
        for tweet in tweets:
            if total_processed >= MAX_VIDEOS:
                print(f"\n[停止] 已处理 {MAX_VIDEOS} 个视频推文")
                stop_flag = True
                return

            total_processed += 1
            tweet_id = tweet.get("tweet_id")

            if record_manager.is_downloaded(tweet_id):
                print(f"[跳过] 推文 {tweet_id} 已下载 ({total_processed}/{MAX_VIDEOS})")
                skipped_count += 1
                continue

            video_info = extractor.extract_video_info(tweet)
            if not video_info:
                print(f"[警告] 无法提取视频信息: {tweet_id}")
                continue

            print(f"[下载] 推文 {tweet_id} ({total_processed}/{MAX_VIDEOS})")
            success = downloader.download_video(video_info)

            if success:
                record_manager.mark_downloaded(tweet_id)
                downloaded_count += 1
                record_manager.save()

    print("\n[开始] 获取最新的点赞视频推文...")

    cursor = None
    page = 1

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

        if stop_flag:
            break

        if not result.get("has_more") or not result.get("next_cursor"):
            print("[API] 已获取所有数据")
            break

        cursor = result.get("next_cursor")
        page += 1

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

    files = downloader.get_downloaded_files()
    if files:
        print(f"\n已下载文件列表 ({len(files)} 个):")
        for f in files[:10]:
            print(f"  - {f}")
        if len(files) > 10:
            print(f"  ... 还有 {len(files) - 10} 个文件")

    print("=" * 60)


def run_watch_mode(api, extractor, downloader, record_manager, user_id, interval):
    """监控模式 - 持续运行，自动下载新视频"""
    print(f"\n目标用户: @{TARGET_USER} (ID: {user_id})")
    print(f"运行模式: 持续监控，自动下载新视频")
    print("\n提示: 按 Ctrl+C 停止监控")
    print("=" * 60)

    session_count = 0
    total_downloaded = 0

    while True:
        session_count += 1
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"\n{'=' * 60}")
        print(f"[检查 #{session_count}] 时间: {now}")
        print("=" * 60)

        # 检查新视频
        downloaded, skipped, checked = check_new_videos(
            api, extractor, downloader, record_manager, user_id,
            max_check=100  # 监控模式下多检查一些
        )

        total_downloaded += downloaded
        stats = record_manager.get_stats()

        # 显示结果
        print(f"\n[本次检查结果]")
        print(f"  新下载: {downloaded} 个视频")
        print(f"  已存在: {skipped} 个已下载视频")
        print(f"  检查数: {checked} 个视频推文")
        print(f"  历史总计: {stats['unique_tweets']} 个视频")
        print(f"  累计下载: {total_downloaded} 个新视频")

        if downloaded > 0:
            print(f"\n[提示] 发现并下载了 {downloaded} 个新视频！")
        else:
            print(f"\n[提示] 未发现新视频")

        # 等待下次检查
        next_time = datetime.now().strftime("%H:%M:%S")
        print(f"\n[等待] 下次检查: {interval} 分钟后 (约 {next_time})")
        print("[提示] 按 Ctrl+C 停止监控")

        try:
            time.sleep(interval * 60)
        except KeyboardInterrupt:
            print("\n\n" + "=" * 60)
            print("[退出] 用户中断监控")
            print("=" * 60)
            print(f"监控次数: {session_count}")
            print(f"累计下载: {total_downloaded} 个新视频")
            print(f"历史总计: {stats['unique_tweets']} 个视频")
            print("记录已自动保存")
            print("=" * 60)
            break


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Twitter/X Likes 视频下载器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python main.py              单次运行，下载最新50个
  python main.py --watch      监控模式，持续运行
  python main.py --watch --interval 5   每5分钟检查一次
        '''
    )
    parser.add_argument('--watch', action='store_true',
                        help='监控模式，持续运行自动下载新视频')
    parser.add_argument('--interval', type=int, default=DEFAULT_INTERVAL,
                        help=f'监控检查间隔（分钟），默认{DEFAULT_INTERVAL}分钟')
    args = parser.parse_args()

    # 打印标题
    print("\n" + "=" * 60)
    if args.watch:
        print("Twitter/X Likes 视频下载器 - 监控模式")
        print(f"检查间隔: {args.interval} 分钟")
    else:
        print("Twitter/X Likes 视频下载器")
        print(f"最大下载: {MAX_VIDEOS} 个最新视频")
    print("=" * 60)

    # 初始化各模块
    api = TwitterAPI()
    extractor = VideoExtractor()
    downloader = Downloader()
    record_manager = RecordManager()

    # 获取用户 ID
    print("\n[初始化] 获取用户信息...")
    user_id = api.get_user_id(TARGET_USER)

    if not user_id:
        print("[错误] 无法获取用户 ID，请检查:")
        print("  1. 用户名是否正确")
        print("  2. Cookies 是否有效（可能已过期）")
        print("  3. 网络连接是否正常")
        sys.exit(1)

    # 根据模式运行
    if args.watch:
        run_watch_mode(api, extractor, downloader, record_manager, user_id, args.interval)
    else:
        run_single_mode(api, extractor, downloader, record_manager, user_id)


if __name__ == "__main__":
    main()