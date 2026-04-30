from enum import Enum

from bale_downloader.youtube import Youtube
from bale_downloader.twitter import Twitter
from bale_downloader.github import Github
# from bale_downloader.webpage import Webpage


class Site(Enum):
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    GITHUB = "github"


def get_url_content(url: str) -> tuple[str, str, list[str], list[str]]:
    site = get_url_site(url)
    if site == Site.YOUTUBE:
        return get_youtube_content(url)
    if site == Site.TWITTER:
        return Twitter().get_content(url)
    if site == Site.GITHUB:
        return Github(url).get_content()
    # if site is Site.Webpage:
    #     return Webpage().get_content(url)
    raise ValueError(f"Unsupported site: {site}")


def get_youtube_content(url: str):
    return Youtube().get_content(url)


def get_url_site(url: str):
    if "youtube.com" in url:
        return Site.YOUTUBE
    elif "twitter.com" in url or "x.com" in url or "mobile.twitter.com" in url or "vxtwitter.com" in url:
        return Site.TWITTER
    elif "instagram.com" in url:
        return Site.INSTAGRAM
    elif "github.com" in url:
        return Site.GITHUB
    else:
        return None
