# Bale Downloader

A [Bale](https://bale.ai) messenger bot that downloads content from YouTube, Twitter/X, and **any web page** (saved as PDF), optionally uploads to Google Drive, and sends chat-friendly versions back through Bale.

## How It Works

1. The bot long-polls the Bale Bot API for new messages.
2. Only messages from allow-listed chat IDs are processed.
3. When a **YouTube** URL is received, the bot:
   - Downloads a **high-quality** version and a **lower-quality** chat-sized version using `yt-dlp`.
   - Uploads the high-quality file to a Google Drive folder and shares the link.
   - Sends the Google Drive link and the smaller file(s) + thumbnail(s) back in the Bale chat.
4. When a **Twitter/X** URL is received, the bot downloads media (videos/images) and sends them back.
5. When a **Github** URL is received, the bot downloads a single file, or the whole repo, or exports the webpage based on the the url.
6. When **any other URL** is received, the bot renders the page using a headless Chromium browser and sends a **PDF snapshot** back in the chat.
6. Large videos can optionally be split into parts or re-encoded to fit within size limits.

## Prerequisites

- **Python 3.12+**
- **ffmpeg** and **ffprobe** (used for splitting/re-encoding videos)
- **Playwright + Chromium** (used for web page PDF generation) — see [Playwright Setup](#playwright-setup)
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

### Playwright Setup

Playwright needs a Chromium browser binary. After installing the Python package:

```bash
playwright install chromium
```

On a fresh Ubuntu server you may also need OS-level dependencies:

```bash
playwright install --with-deps chromium
```

This installs Chromium **and** all required shared libraries (`libnss3`, `libatk1.0`, `libgbm1`, etc.) in one command.

If you prefer to install the system dependencies manually:

```bash
sudo apt-get update && sudo apt-get install -y \
    libnss3 libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 \
    libxcomposite1 libxrandr2 libxdamage1 libpango-1.0-0 \
    libgbm1 libasound2t64 libxshmfence1 libx11-xcb1 libxcb1
playwright install chromium
```

## Docker

A `Dockerfile` is provided for container deployment:

```bash
docker build -t bale-downloader .
docker run --env-file .env \
    -v $(pwd)/bale-offset:/app/bale-offset \
    bale-downloader
```

The `bale-offset` bind mount persists the polling offset across container restarts so no messages are re-processed.

If you use Google Drive uploads, also mount your credentials:

```bash
docker run --env-file .env \
    -v $(pwd)/bale-offset:/app/bale-offset \
    -v $(pwd)/credentials.json:/app/credentials.json \
    -v $(pwd)/token.json:/app/token.json \
    bale-downloader
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
| `TWITTER_OUTPUT_DIR` | No | Directory for Twitter media downloads (default: `twitter-output`) |
| `TARGET_SIZE_MB` | No | Max file size in MB for the chat-friendly version |
| `GOOD_QUALITY_SIZE_LIMIT_MB` | No | Max file size in MB for the high-quality version |
| `SPLIT_VIDEO_IF_ITS_TOO_LARGE` | No | Set to `true` to split large videos into parts instead of skipping them |
| `WEBPAGE_OUTPUT_DIR` | No | Directory for webpage PDF output (default: `webpage-output`) |
| `WEBPAGE_PDF_TIMEOUT_MS` | No | Timeout in ms for loading a web page before generating PDF (default: `30000`) |
| `GITHUB_OUTPUT_DIR` | No | Directory for github downloaded files (default: `github-output`) |


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

The bot will start polling for messages. Send a YouTube URL, a Twitter/X URL, or any web page URL in an allowed Bale chat and the bot will process it automatically.

Press `Ctrl+C` to gracefully shut down — the current polling offset is saved so no messages are re-processed on restart.

