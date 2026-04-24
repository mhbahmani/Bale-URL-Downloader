import hashlib
import json
import os
import subprocess
import tempfile
import time
import requests

from bale_downloader.config import BOT_TOKEN, FILE_PASSWORD

VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}

MEDIA_GROUP_LIMIT = 10

BASE_URL = f'https://tapi.bale.ai/bot{BOT_TOKEN}'


def send_message(chat_id, text, file_paths=None, thumbnail_paths=None, protected=False):
    if not file_paths:
        url = f'{BASE_URL}/sendMessage'
        data = {'chat_id': chat_id, 'text': text}
        response = requests.post(url, json=data)
        if response.status_code // 100 != 2:
            print("Sending message to bale failed with status code ", response.status_code)
            return False
        # print(response.json(), response.status_code)
        return True

    if file_paths:
        if protected:
            for i, file_path in enumerate(file_paths):
                send_file_as_zip(file_path, chat_id, text, i)
        else:
            send_files(file_paths, chat_id, text)
            # for file_path in file_paths:
            #     send_file(file_path, chat_id, text)
            return True

def send_file(file_path, chat_id, caption=None):
    ext = os.path.splitext(file_path)[1].lower()
    is_video = ext in VIDEO_EXTENSIONS

    endpoint = 'sendVideo' if is_video else 'sendDocument'
    field = 'video' if is_video else 'document'
    url = f'{BASE_URL}/{endpoint}'

    data = {'chat_id': chat_id}
    if caption:
        data['caption'] = caption
    print(file_path)
    with open(file_path, 'rb') as f:
        files = {field: f}
        response = requests.post(url, data=data, files=files)
        if response.status_code == 413:
            print("File too large, skipping")
        return response.status_code // 100 == 2


def send_files(file_paths, chat_id, caption=None):
    if len(file_paths) <= 10:
        return send_media_group(file_paths, chat_id, caption)

    results = []
    for file_path in file_paths:
        results.append(send_single_file(file_path, chat_id, caption))
    return all(results)


def send_single_file(file_path, chat_id, caption=None):
    ext = os.path.splitext(file_path)[1].lower()

    if ext in IMAGE_EXTENSIONS:
        endpoint = 'sendPhoto'
        field = 'photo'
    elif ext in VIDEO_EXTENSIONS:
        endpoint = 'sendVideo'
        field = 'video'
    else:
        endpoint = 'sendDocument'
        field = 'document'

    url = f'{BASE_URL}/{endpoint}'

    data = {'chat_id': chat_id}
    if caption:
        data['caption'] = caption

    with open(file_path, 'rb') as f:
        files = {field: f}
        response = requests.post(url, data=data, files=files)

    if response.status_code == 413:
        print("File too large, skipping")

    return response.status_code // 100 == 2


def send_media_group(file_paths, chat_id, caption=None):
    url = f'{BASE_URL}/sendMediaGroup'

    media = []
    files = {}

    for i, path in enumerate(file_paths):
        ext = os.path.splitext(path)[1].lower()

        if ext in IMAGE_EXTENSIONS:
            mtype = "photo"
        elif ext in VIDEO_EXTENSIONS:
            mtype = "video"
        else:
            mtype = "document"

        attach_name = f"file{i}"
        media_item = {
            "type": mtype,
            "media": f"attach://{attach_name}"
        }

        # Telegram allows caption only on first item in group
        if i == 0 and caption:
            media_item["caption"] = caption

        media.append(media_item)
        files[attach_name] = open(path, "rb")

    data = {
        "chat_id": chat_id,
        "media": json.dumps(media)
    }

    response = requests.post(url, data=data, files=files)

    for f in files.values():
        f.close()

    if response.status_code == 413:
        print("Group too large")

    return response.status_code // 100 == 2


def send_file_as_zip(file_path, chat_id, caption=None, index=None):
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    base_name_hash = hashlib.sha256(base_name.encode()).hexdigest()
    zip_path = os.path.join(tempfile.gettempdir(), f"{base_name_hash}_{index}.zip")

    subprocess.run([
        "zip", "-j", "--password", FILE_PASSWORD, zip_path, file_path
    ], check=True)

    try:
        result = send_file(zip_path, chat_id, caption)
        return result
    finally:
        os.remove(zip_path)


def get_updates(offset=None):
    url = f'{BASE_URL}/getUpdates'
    params = {'offset': offset} if offset else {}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()['result']
    return []


def get_latest_offset(mode):
    updates = get_updates()

    if updates:
        return updates[-1]['update_id'] + 1
    return None


def listen_for_updates(offset=None):
    while True:
        updates = get_updates(offset)
        messages = []
        if not updates:
            time.sleep(0.2)
            print("No updates found, waiting...")
            continue

        for update in updates:
            offset = update['update_id'] + 1
            if update.get('message', {}).get('text'):
                messages.append((update['message']['text'], update['message']['chat']['id']))

        if messages:
            return messages, offset
        time.sleep(2)
