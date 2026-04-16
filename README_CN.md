# Twitter/X Likes 视频下载器

[English](README.md) | 中文

自动下载指定用户点赞的视频推文，支持增量更新。

## 功能特点

- ✅ **最高清晰度** - 自动选择 bitrate 最高的视频版本
- ✅ **增量下载** - 记录已下载的推文，下次运行自动跳过
- ✅ **监控模式** - 持续监控新增 likes，自动下载新视频
- ✅ **断点续传** - 每次下载后保存记录，中断后可继续

## 安装依赖

```bash
pip install requests
```

## 配置

### 1. 获取 Twitter Cookies

1. 打开浏览器，登录 [x.com](https://x.com)
2. 按 `F12` 打开开发者工具
3. 切换到 `Application` → `Cookies` → `https://x.com`
4. 复制以下值：
   - `auth_token`
   - `ct0`

**注意**：Cookies 有效期约 2-4 周。遇到 HTTP 401 错误时需要重新获取。

### 2. 创建 config.py

复制 `config.example.py` 为 `config.py` 并填入：

```python
COOKIES = {
    "auth_token": "你的auth_token值",
    "ct0": "你的ct0值"
}

TARGET_USER = "用户名"
PROXY = "http://127.0.0.1:10808"  # 不需要则设为 None
```

## 使用方法

### 单次运行模式

```bash
python main.py
```

下载最新 50 个视频后退出。

### 监控模式（推荐长时间运行）

```bash
python main.py --watch
```

- **持续监控** 新增的 likes 视频
- **自动下载** 发现新视频时立即下载
- **默认间隔** 10 分钟检查一次
- **按 Ctrl+C** 停止监控

### 自定义检查间隔

```bash
python main.py --watch --interval 5
```

每 5 分钟检查一次。

## 监控模式详解

| 功能 | 说明 |
|------|------|
| 持续运行 | 无限运行直到按 Ctrl+C |
| 自动检测 | 每次扫描最新 100 个视频 |
| 智能停止 | 发现无新视频时停止扫描 |
| 安全保存 | 每次下载后自动保存记录 |

**工作原理**：
1. 每隔设定时间，扫描最新 likes
2. 跳过已下载的视频
3. 发现新视频时自动下载
4. 等待下一次检查

**输出示例**：
```
============================================================
[检查 #5] 时间: 2026-04-16 12:30:00
============================================================

[新视频] 发现新视频: 204xxx
       清晰度: 1080x1440, bitrate: 10368000
       进度: 100% (24.7 MB)
[下载] 完成: download/xxx.mp4

[本次检查结果]
  新下载: 2 个视频
  已存在: 48 个已下载视频
  检查数: 50 个视频推文
  历史总计: 52 个视频

[等待] 下次检查: 10 分钟后
[提示] 按 Ctrl+C 停止监控
```

## 文件命名规则

`{推文ID}_{发布时间}_{分辨率}.mp4`

示例：`2043251055568560435_20260412_1080_1440.mp4`

## 常见问题

### HTTP 401 - 认证失败

Cookies 已过期。重新登录 Twitter 并更新 `config.py`。

### HTTP 404 - Query Not Found

运行 `python extract_ids.py` 更新 Query IDs。

### 连接失败

检查代理配置是否正确。

## 目录结构

```
twitter-likes-downloader/
├── main.py              # 主程序
├── config.py            # 你的配置
├── config.example.py    # 配置模板
├── twitter_api.py       # Twitter API 封装
├── video_extractor.py   # 视频提取
├── downloader.py        # 下载器
├── record_manager.py    # 下载记录
├── extract_ids.py       # 更新 Query IDs
├── download/            # 视频文件
└── download_record.json # 历史记录
```

## 注意事项

- Cookies 有效期约 2-4 周
- 请遵守 Twitter 使用条款
- 下载的视频仅供个人收藏

## 许可证

MIT License