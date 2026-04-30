import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]
FILE_PASSWORD = os.environ["FILE_PASSWORD"]
GOOGLE_DRIVE_FOLDER_ID = os.environ["GOOGLE_DRIVE_FOLDER_ID"]
ALLOWED_CHAT_IDS = [int(x) for x in os.environ["ALLOWED_CHAT_IDS"].split(",")]
COOKIE_PATH = os.environ.get("COOKIE_PATH", "firefox-cookies")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "yt-output")
TWITTER_OUTPUT_DIR = os.environ.get("TWITTER_OUTPUT_DIR", "twitter-output")
TARGET_SIZE_MB = int(os.environ.get("TARGET_SIZE_MB", "20"))
GOOD_QUALITY_SIZE_LIMIT_MB = int(os.environ.get("GOOD_QUALITY_SIZE_LIMIT_MB", "1000"))
SPLIT_VIDEO_IF_ITS_TOO_LARGE = bool(os.environ.get("SPLIT_VIDEO_IF_ITS_TOO_LARGE", False))
WEBPAGE_OUTPUT_DIR = os.environ.get("WEBPAGE_OUTPUT_DIR", "webpage-output")
WEBPAGE_PDF_TIMEOUT_MS = int(os.environ.get("WEBPAGE_PDF_TIMEOUT_MS", "30000"))
GITHUB_OUTPUT_DIR = os.environ.get("GITHUB_OUTPUT_DIR", "github-output")
