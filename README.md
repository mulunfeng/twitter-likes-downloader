# Twitter/X Likes Video Downloader

English | [中文](README_CN.md)

Automatically download videos from a user's liked tweets with the highest quality.

## Features

- ✅ **Highest Quality** - Automatically selects the video with the highest bitrate
- ✅ **Incremental Download** - Records downloaded tweets, skips on next run
- ✅ **Limit Count** - Only downloads the latest 50 videos
- ✅ **Auto Update** - New likes are automatically discovered and downloaded
- ✅ **Resume Support** - Saves progress after each download

## Directory Structure

```
twitter-likes-downloader/
├── main.py              # Main entry point
├── config.py            # Configuration (cookies, proxy, etc.)
├── twitter_api.py       # Twitter API wrapper
├── video_extractor.py   # Video info extraction
├── downloader.py        # Video downloader
├── record_manager.py    # Download record management
├── extract_ids.py       # Update Twitter Query IDs
├── requirements.txt     # Dependencies
├── download/            # Video save directory
│   └── *.mp4
└── download_record.json # Download history
```

## Installation

```bash
pip install requests
```

Or:

```bash
pip install -r requirements.txt
```

## Configuration

### 1. Get Twitter Cookies

1. Open browser and login to [x.com](https://x.com)
2. Press `F12` to open Developer Tools
3. Go to `Application` → `Cookies` → `https://x.com`
4. Copy these two values:
   - `auth_token`
   - `ct0`

### 2. Create config.py

Copy `config.example.py` to `config.py` and fill in your configuration:

```python
# Twitter Cookies
COOKIES = {
    "auth_token": "your_auth_token",
    "ct0": "your_ct0_value"
}

# Target user screen_name (without @)
TARGET_USER = "username"

# Proxy (if needed)
PROXY = "http://127.0.0.1:10808"  # Set to None if not needed
```

### 3. Update Query IDs (if API fails)

Twitter periodically updates GraphQL Query IDs. If you get "Query not found" error:

```bash
python extract_ids.py
```

Then update the IDs in `config.py`:

```python
QUERY_ID_USER_BY_SCREEN_NAME = "new_id"
QUERY_ID_LIKES = "new_id"
```

## Usage

### Run the downloader

```bash
python main.py
```

### Example output

```
============================================================
Twitter/X Likes Video Downloader
============================================================
Target user: @username
Max download: 50 latest videos
============================================================

[Step 1] Getting user info...
[API] User ID: 1601427259302158337

[Step 2] Fetching latest liked video tweets...
[API] Getting page 1...
[API] Found 15 video tweets on this page
[Skip] Tweet 2043251055568560435 already downloaded (1/50)
[Download] Tweet 204xxx (2/50)
       Resolution: 1080x1440, bitrate: 10368000
       Progress: 25.0% (6.0 MB)
       ...
[Download] Complete: download/xxx.mp4 (24.7 MB)

============================================================
Download complete!
============================================================
Downloads this run: 3 videos
Skipped this run: 47 already downloaded videos
Processed this run: 50 video tweets
Total history: 50 videos
Download directory: download
============================================================
```

## File Naming

Video files are named as: `{tweet_id}_{timestamp}_{resolution}.mp4`

Example: `2043251055568560435_20260412_085308_1080_1440.mp4`

## Incremental Download

- **First run**: Downloads the latest 50 video tweets
- **Next run**: Skips already downloaded, only downloads new likes
- **New likes**: Automatically downloads if within the top 50

## Common Issues

### HTTP 404 / Query not found

Twitter API Query IDs expired. Run `python extract_ids.py` to update.

### Authentication failed (HTTP 401)

Cookies expired. Re-login to Twitter and get new `auth_token` and `ct0`.

### Connection failed / SSL error

Check proxy configuration or try a different proxy.

### Download interrupted

Progress is saved automatically. Run `python main.py` again to continue.

## Notes

- Please follow Twitter's terms of service, avoid excessive requests
- Cookies may expire, need to update periodically
- Proxy must support HTTPS
- Downloaded videos are for personal use only, do not use commercially

## License

MIT License