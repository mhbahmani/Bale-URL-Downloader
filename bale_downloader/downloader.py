from enum import Enum

from bale_downloader.youtube import Youtube


class Site(Enum):
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    GITHUB = "github"


def get_url_content(url: str) -> tuple[str, str, list[str], list[str]]:
    site = get_url_site(url)
    if site == Site.YOUTUBE:
        return get_youtube_content(url)
    raise ValueError(f"Unsupported site: {site}")


def get_youtube_content(url: str):
    return Youtube().get_content(url)


def get_url_site(url: str):
    if "youtube.com" in url:
        return Site.YOUTUBE
    elif "twitter.com" in url or "x.com" in url:
        return Site.TWITTER
    elif "instagram.com" in url:
        return Site.INSTAGRAM
    elif "github.com" in url:
        return Site.GITHUB
    else:
        return None
