from time import sleep

from bale_downloader.bale import listen_for_updates, send_message
from bale_downloader.config import ALLOWED_CHAT_IDS
from bale_downloader.downloader import get_url_content
from bale_downloader.google_drive import GoogleDrive
from bale_downloader.utils import save_to_file, load_file_content

GOOGLE_DRIVE_MESSAGE_TEMPLATE = "Google Drive URL: \n{}"
GOT_YOUR_URL_MESSAGE = "📥 Got your url, working on it ..."
OFFSET_FILE_NAME = "bale-offset"

google_drive = GoogleDrive()


def load_stored_offset() -> int:
    offset = load_file_content(OFFSET_FILE_NAME)
    return int(offset) if offset else None

def shutdown(offset: int):
    print("Shutting down")
    if offset:
        save_to_file(OFFSET_FILE_NAME, str(offset))


def is_allowed_chat_id(func):
    def wrapper(msg, chat_id):
        if chat_id not in ALLOWED_CHAT_IDS:
            return
        return func(msg, chat_id)
    return wrapper


@is_allowed_chat_id
def process_message(msg, chat_id):
    try:
        print(f"Proccessing {msg}")
        send_message(chat_id, GOT_YOUR_URL_MESSAGE)
        res_message, high_quality_file_path, file_paths, thumbnail_paths = get_url_content(msg)
        if high_quality_file_path:
            url = google_drive.upload_file_to_drive(high_quality_file_path)
            send_message(chat_id, GOOGLE_DRIVE_MESSAGE_TEMPLATE.format(url))
        send_message(chat_id, res_message, file_paths, thumbnail_paths)
    except KeyboardInterrupt as e:
        raise e
    except Exception as e:
        print(e)
        raise Exception()


def main():
    offset = None
    try:
        offset = load_stored_offset()
        while True:
            messages, offset = listen_for_updates(offset)
            for msg, chat_id in messages:
                process_message(msg, chat_id)
            sleep(5)
    except KeyboardInterrupt:
        shutdown(offset)
    except Exception:
        shutdown(offset)


if __name__ == "__main__":
    main()
