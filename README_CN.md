# Twitter/X Likes 视频下载器

[English](README.md) | 中文

自动下载指定用户点赞的视频推文，支持增量更新。

## 功能特点

- ✅ **最高清晰度** - 自动选择 bitrate 最高的视频版本
- ✅ **增量下载** - 记录已下载的推文，下次运行自动跳过
- ✅ **限制数量** - 只下载最新的 50 个视频，不下载更早期的
- ✅ **自动更新** - 有新的 likes 视频时自动发现并下载
- ✅ **断点续传** - 每次下载后保存记录，中断后可继续

## 目录结构

```
twitter-likes-downloader/
├── main.py              # 主程序入口
├── config.py            # 配置文件（cookies、代理等）
├── twitter_api.py       # Twitter API 封装
├── video_extractor.py   # 视频信息提取
├── downloader.py        # 视频下载器
├── record_manager.py    # 下载记录管理
├── extract_ids.py       # 更新 Twitter Query IDs
├── requirements.txt     # 依赖列表
├── download/            # 视频保存目录
│   └── *.mp4
└── download_record.json # 下载记录
```

## 安装依赖

```bash
pip install requests
```

或：

```bash
pip install -r requirements.txt
```

## 配置

### 1. 获取 Twitter Cookies

1. 打开浏览器，登录 [x.com](https://x.com)
2. 按 `F12` 打开开发者工具
3. 切换到 `Application` → `Cookies` → `https://x.com`
4. 复制以下两个值：
   - `auth_token`
   - `ct0`

### 2. 创建 config.py

复制 `config.example.py` 为 `config.py` 并填入配置：

```python
# Twitter Cookies
COOKIES = {
    "auth_token": "你的auth_token值",
    "ct0": "你的ct0值"
}

# 目标用户 screen_name（不含 @）
TARGET_USER = "用户名"

# 代理设置（如需要）
PROXY = "http://127.0.0.1:10808"  # 不需要则设为 None
```

### 3. 更新 Query IDs（如果 API 失效）

Twitter 会定期更新 GraphQL Query IDs，如果遇到 "Query not found" 错误：

```bash
python extract_ids.py
```

然后将输出的 ID 更新到 `config.py` 中：

```python
QUERY_ID_USER_BY_SCREEN_NAME = "新的ID"
QUERY_ID_LIKES = "新的ID"
```

## 使用方法

### 运行下载

```bash
python main.py
```

### 输出示例

```
============================================================
Twitter/X Likes 视频下载器
============================================================
目标用户: @用户名
最大下载: 50 个最新视频
============================================================

[步骤 1] 获取用户信息...
[API] 用户 ID: 1601427259302158337

[步骤 2] 获取最新的点赞视频推文...
[API] 正在获取第 1 页...
[API] 本页发现 15 个视频推文
[跳过] 推文 2043251055568560435 已下载 (1/50)
[下载] 推文 204xxx (2/50)
       清晰度: 1080x1440, bitrate: 10368000
       进度: 25.0% (6.0 MB)
       ...
[下载] 完成: download/xxx.mp4 (24.7 MB)

============================================================
下载完成!
============================================================
本次下载: 3 个视频
本次跳过: 47 个已下载视频
本次处理: 50 个视频推文
历史总计: 50 个视频
下载目录: download
============================================================
```

## 文件命名规则

视频文件命名格式：`{推文ID}_{发布时间}_{分辨率}.mp4`

示例：`2043251055568560435_20260412_085308_1080_1440.mp4`

## 增量下载说明

- **首次运行**：下载最新的 50 个视频推文
- **再次运行**：跳过已下载的，只下载新的 likes 视频
- **有新 likes**：如果点赞了新视频，下次运行会自动下载（仍在前 50 个限制内）

## 常见问题

### HTTP 404 / Query not found

Twitter API Query IDs 已过期，运行 `python extract_ids.py` 更新。

### 认证失败 (HTTP 401)

Cookies 已过期，需要重新登录 Twitter 获取新的 `auth_token` 和 `ct0`。

### 连接失败 / SSL 错误

检查代理配置是否正确，或尝试更换代理。

### 下载中断

记录会自动保存，再次运行 `python main.py` 即可继续。

## 注意事项

- 请遵守 Twitter 使用条款，不要过度频繁请求
- Cookies 可能会过期，需要定期更新
- 代理必须支持 HTTPS
- 下载的视频仅供个人收藏，请勿用于商业用途

## 许可证

MIT License