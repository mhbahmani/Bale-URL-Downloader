from time import sleep

from bale_downloader.bot import listen_for_updates, send_message
from bale_downloader.config import ALLOWED_CHAT_IDS
from bale_downloader.downloader import get_url_content
from bale_downloader.google_drive import GoogleDrive

GOOGLE_DRIVE_MESSAGE_TEMPLATE = "File Urls:\n{}"

google_drive = GoogleDrive()


def is_allowed_chat_id(func):
    def wrapper(msg, chat_id):
        if chat_id not in ALLOWED_CHAT_IDS:
            return
        return func(msg, chat_id)
    return wrapper


@is_allowed_chat_id
def process_message(msg, chat_id):
    try:
        res_message, high_quality_file_path, file_paths, thumbnail_paths = get_url_content(msg)
        url = google_drive.upload_files_to_drive(high_quality_file_path)
        send_message(chat_id, GOOGLE_DRIVE_MESSAGE_TEMPLATE.format(url))
        send_message(chat_id, res_message, file_paths, thumbnail_paths)
    except Exception as e:
        print(e)


def main():
    offset = None
    while True:
        messages, offset = listen_for_updates(offset)
        for msg, chat_id in messages:
            process_message(msg, chat_id)
        sleep(5)
        break


if __name__ == "__main__":
    main()
