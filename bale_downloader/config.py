import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]
FILE_PASSWORD = os.environ["FILE_PASSWORD"]
GOOGLE_DRIVE_FOLDER_ID = os.environ["GOOGLE_DRIVE_FOLDER_ID"]
ALLOWED_CHAT_IDS = [int(x) for x in os.environ["ALLOWED_CHAT_IDS"].split(",")]
COOKIE_PATH = os.environ.get("COOKIE_PATH", "cookies.txt")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "yt-output")
TARGET_SIZE_MB = int(os.environ.get("TARGET_SIZE_MB", "20"))
GOOD_QUALITY_SIZE_LIMIT_MB = int(os.environ.get("GOOD_QUALITY_SIZE_LIMIT_MB", "1000"))
