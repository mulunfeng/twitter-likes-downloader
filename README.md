# Twitter/X Likes Video Downloader

English | [中文](README_CN.md)

Automatically download videos from a user's liked tweets with the highest quality.

## Features

- ✅ **Highest Quality** - Automatically selects the video with the highest bitrate
- ✅ **Incremental Download** - Records downloaded tweets, skips on next run
- ✅ **Watch Mode** - Continuously monitors for new likes and auto-downloads
- ✅ **Resume Support** - Saves progress after each download

## Installation

```bash
pip install requests
```

## Configuration

### 1. Get Twitter Cookies

1. Open browser and login to [x.com](https://x.com)
2. Press `F12` to open Developer Tools
3. Go to `Application` → `Cookies` → `https://x.com`
4. Copy these values:
   - `auth_token`
   - `ct0`

**Note**: Cookies expire after ~2-4 weeks. You'll need to refresh them when you see HTTP 401 errors.

### 2. Create config.py

Copy `config.example.py` to `config.py` and fill in:

```python
COOKIES = {
    "auth_token": "your_auth_token",
    "ct0": "your_ct0_value"
}

TARGET_USER = "username"
PROXY = "http://127.0.0.1:10808"  # or None if not needed
```

## Usage

### Single Run Mode

```bash
python main.py
```

Downloads the latest 50 videos and exits.

### Watch Mode (Recommended for Continuous Monitoring)

```bash
python main.py --watch
```

- **Continuously monitors** for new likes
- **Auto-downloads** when new videos are detected
- **Default interval**: 10 minutes
- **Press Ctrl+C** to stop

### Custom Interval

```bash
python main.py --watch --interval 5
```

Checks every 5 minutes.

## Watch Mode Details

| Feature | Description |
|---------|-------------|
| Continuous | Runs indefinitely until Ctrl+C |
| Auto-detect | Checks latest 100 videos each scan |
| Smart stop | Stops checking when no new videos found |
| Safe | Records saved after each download |

**How it works**:
1. Every interval, scans the latest likes
2. Skips already downloaded videos
3. Downloads any new videos found
4. Waits for next interval

## File Naming

`{tweet_id}_{timestamp}_{resolution}.mp4`

Example: `2043251055568560435_20260412_1080_1440.mp4`

## Common Issues

### HTTP 401 - Authentication Failed

Cookies expired. Re-login to Twitter and update `config.py`.

### HTTP 404 - Query Not Found

Run `python extract_ids.py` to update Query IDs.

### Connection Failed

Check proxy configuration.

## Directory Structure

```
twitter-likes-downloader/
├── main.py              # Main program
├── config.py            # Your configuration
├── config.example.py    # Configuration template
├── twitter_api.py       # Twitter API wrapper
├── video_extractor.py   # Video extraction
├── downloader.py        # Video downloader
├── record_manager.py    # Download history
├── extract_ids.py       # Update Query IDs
├── download/            # Video files
└── download_record.json # History
```

## Notes

- Cookies expire after ~2-4 weeks
- Follow Twitter's terms of service
- Videos are for personal use only

## License

MIT License