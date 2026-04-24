import json
import math
import os
import subprocess
from time import sleep

import yt_dlp

from bale_downloader.config import (
    COOKIE_PATH,
    GOOD_QUALITY_SIZE_LIMIT_MB,
    OUTPUT_DIR,
    TARGET_SIZE_MB,
)

NUM_RETRY = 3
GOOD_QUALITY_SIZE_LIMIT_BYTES = GOOD_QUALITY_SIZE_LIMIT_MB * 1024 * 1024
TARGET_SIZE_BYTES = TARGET_SIZE_MB * 1024 * 1024

os.makedirs(OUTPUT_DIR, exist_ok=True)


def _get_duration(file_path):
    output = subprocess.check_output([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]).decode().strip()
    return float(output)


def _split_once(file_path, num_parts):
    duration = _get_duration(file_path)
    segment_duration = duration / num_parts
    base, ext = os.path.splitext(file_path)

    parts = []
    for i in range(num_parts):
        start = i * segment_duration
        part_path = f"{base}_p{i + 1}{ext}"
        subprocess.run([
            "ffmpeg", "-y",
            "-ss", str(start),
            "-i", file_path,
            "-t", str(segment_duration),
            "-c", "copy",
            "-avoid_negative_ts", "make_zero",
            part_path
        ], check=True)
        parts.append(part_path)

    os.remove(file_path)
    return parts


def split_video(file_path, max_size_bytes=TARGET_SIZE_BYTES):
    file_size = os.path.getsize(file_path)
    if file_size <= max_size_bytes:
        return [file_path]

    num_parts = math.ceil(file_size / max_size_bytes)
    pending = _split_once(file_path, num_parts)

    final = []
    while pending:
        part = pending.pop(0)
        if os.path.getsize(part) <= max_size_bytes:
            final.append(part)
        else:
            final.extend(split_video(part, max_size_bytes))

    return final


class Youtube:
    def _get_video_high_quality_format_id(self, url: str, formats: list[dict] = None) -> str:
        if not formats:
            print("Formats are not provided")
            formats = self._get_video_available_formats(url)
        valid_formats = []
        for f in formats:
            size = f.get("filesize") or f.get("filesize_approx")
            if size and size <= GOOD_QUALITY_SIZE_LIMIT_BYTES:
                valid_formats.append(f)

        filtered_valid_formats = []
        if valid_formats:
            print("yeessss")
            for i in valid_formats:
                if i.get("height", 0):
                    filtered_valid_formats.append(i)

            best = max(filtered_valid_formats, key=lambda x: x.get("height", 0), default=None)
            if best:
                return best["format_id"]
        print("NOOOOO")
        return None

    def _get_video_low_quality_format_id(self, url: str, formats: list[dict] = None) -> str:
        if not formats:
            print("Formats are not provided")
            formats = self._get_video_available_formats(url)
        valid_formats = []
        for f in formats:
            size = f.get("filesize") or f.get("filesize_approx")
            if (
                size and size <= TARGET_SIZE_BYTES
                and f.get("ext") == "mp4"
                and f.get("acodec") != "none"
                and f.get("vcodec") != "none"
            ):
                valid_formats.append(f)

        if valid_formats:
            print("Some valid formats found")
            best = max(valid_formats, key=lambda x: x.get("height", 0), default=None)
            if best:
                return best["format_id"]
        print("No valid formats")
        return None

    def _run_download_command(self, url: str, format_id: str):
        result = subprocess.run([
            "yt-dlp",
            url,
            "-f", format_id,
            "-o", f"{OUTPUT_DIR}/%(title)s.%(ext)s",
            "--write-thumbnail",
            "--convert-thumbnails", "jpg",
            "--cookies", COOKIE_PATH,
            "--print", "filename"
        ], capture_output=True, text=True)
        if result.returncode == 0:
            downloaded_file_path = result.stdout.strip()
            return downloaded_file_path

    def _download_video(self, url: str, format_id: str) -> str:
        ydl_opts = {
            'format': format_id,
            'outtmpl': f'{OUTPUT_DIR}/%(title)s-High-Quality-Version.%(ext)s',
            'writethumbnail': True,
            'postprocessors': [{'key': 'FFmpegThumbnailsConvertor', 'format': 'jpg'}],
            'cookiefile': COOKIE_PATH,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info_dict)

    def get_content(self, url: str) -> tuple[str, str, list[str], list[str]]:
        print("URLLLLL " + url)
        Youtube.clear_output_dir()
        counter = 0
        print("Goint in")

        while True:
            if counter >= NUM_RETRY:
                return f"Download failed after {NUM_RETRY} retries", None, None, None

            info = self._get_video_info(url)
            formats = info.get("formats", [])
            if formats:
                print("Formats downloaded")
            else:
                print("Formats not available")
            high_quality_file_path = low_quality_file_path = None
            high_quality_format_id = self._get_video_high_quality_format_id(url, formats)
            print(f"High quality: {high_quality_format_id}")
            if high_quality_format_id:
                print("Best high quality format found")
                high_quality_file_path = self._download_video(url, high_quality_format_id)

            low_quality_format_id = self._get_video_low_quality_format_id(url, formats)
            print(f"Low quality: {low_quality_format_id}")
            if low_quality_format_id:
                print("Best low quality format found, downloading without compression")
                download, low_quality_file_path = self._run_download_command(url, low_quality_format_id)
            else:
                print("No best format found, falling back to compression")
                duration = float(info.get("duration", 0))
                if duration == 0:
                    raise Exception("Could not determine duration")

                audio_bitrate = 128

                total_bitrate = int((TARGET_SIZE_MB * 8192) / duration)
                video_bitrate = max(total_bitrate - audio_bitrate, 100)
                download = subprocess.run([
                    "yt-dlp",
                    url,
                    "-o", f"{OUTPUT_DIR}/%(title)s.%(ext)s",

                    "--format", "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]",
                    "--merge-output-format", "mp4",

                    "--write-thumbnail",
                    "--convert-thumbnails", "jpg",

                    "--cookies", COOKIE_PATH,

                    "--postprocessor-args",
                    f"ffmpeg:-b:v {video_bitrate}k -b:a {audio_bitrate}k",
                ])

            if download.returncode != 0:
                sleep(5)
                counter += 1
                continue

            break

        files = os.listdir(OUTPUT_DIR)

        video_path = None
        thumb_full_path = None

        for f in files:
            if f.endswith(".jpg"):
                thumb_full_path = os.path.join(OUTPUT_DIR, f)
            elif "High-Quality-Version" not in f:
                video_path = os.path.join(OUTPUT_DIR, f)

        video_paths = split_video(video_path) if video_path else []

        return "", high_quality_file_path, video_paths, [thumb_full_path]

    @staticmethod
    def clear_output_dir():
        for f in os.listdir(OUTPUT_DIR):
            os.remove(os.path.join(OUTPUT_DIR, f))

    def _get_video_info(self, url: str) -> dict:
        return json.loads(subprocess.check_output([
            "yt-dlp",
            "--dump-json",
            url,
            "--cookies", COOKIE_PATH,
        ]).decode())
