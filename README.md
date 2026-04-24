# Bale Downloader

A [Bale](https://bale.ai) messenger bot that downloads YouTube videos via `yt-dlp`, uploads the high-quality version to Google Drive, and sends a smaller chat-friendly version (with thumbnails) back through Bale.

## How It Works

1. The bot long-polls the Bale Bot API for new messages.
2. Only messages from allow-listed chat IDs are processed.
3. When a YouTube URL is received, the bot:
   - Downloads a **high-quality** version and a **lower-quality** chat-sized version using `yt-dlp`.
   - Uploads the high-quality file to a Google Drive folder and shares the link.
   - Sends the Google Drive link and the smaller file(s) + thumbnail(s) back in the Bale chat.
4. Large videos can optionally be split into parts or re-encoded to fit within size limits.

## Prerequisites

- **Python 3.12+**
- **ffmpeg** and **ffprobe** (used for splitting/re-encoding videos)
- **Google Cloud OAuth credentials** (`credentials.json`) for Drive uploads — see [Google Drive Setup](#google-drive-setup)
- A **Bale Bot Token** (obtain from [BotFather](https://ble.ir/BotFather) on Bale)

## Installation

```bash
git clone <repo-url>
cd bale-downloader
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Copy the sample environment file and fill in your values:

```bash
cp .env.sample .env
```

| Variable | Required | Description |
|---|---|---|
| `BOT_TOKEN` | Yes | Bale bot API token |
| `ALLOWED_CHAT_IDS` | Yes | Comma-separated list of Bale chat IDs allowed to use the bot |
| `GOOGLE_DRIVE_FOLDER_ID` | Yes | ID of the Google Drive folder to upload files to |
| `FILE_PASSWORD` | Yes | Password used when sending files as encrypted zip archives |
| `COOKIE_PATH` | No | Path to a browser cookie file for `yt-dlp` (default: `firefox-cookies`) |
| `OUTPUT_DIR` | No | Directory for temporary downloads (default: `yt-output`) |
| `TARGET_SIZE_MB` | No | Max file size in MB for the chat-friendly version |
| `GOOD_QUALITY_SIZE_LIMIT_MB` | No | Max file size in MB for the high-quality version |
| `SPLIT_VIDEO_IF_ITS_TOO_LARGE` | No | Set to `true` to split large videos into parts instead of skipping them |

## Google Drive Setup

1. Create a project in the [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **Google Drive API**.
3. Create **OAuth 2.0 Client ID** credentials (Desktop application).
4. Download the credentials file and save it as `credentials.json` in the project root.
5. On first run, a browser window will open for OAuth consent. After authorization, a `token.json` file is saved for subsequent runs.

## Usage

```bash
source venv/bin/activate
python -m bale_downloader
```

The bot will start polling for messages. Send a YouTube URL in an allowed Bale chat and the bot will process it automatically.

Press `Ctrl+C` to gracefully shut down — the current polling offset is saved so no messages are re-processed on restart.

