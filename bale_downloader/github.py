from bale_downloader.utils import download_file

from enum import Enum

import re


class Github:
    GITHUB_URL_REGEX = "http(s)?://github.com/(?P<group_name>[\\w_-]+)/(?P<project_name>[\\w_-]+)(/(?P<repo_location>((blob|tree)/(?P<branch>[\\w.]+)/(?P<file_path>[\\w./_-]+)|[\\w./_-]+)))?"
    class GithubURLType(Enum):
        REPO = "repo"
        WEBPAGE = "webpage"
        SINGLE_FILE = "single_file"

    def __init__(self, url) -> None:
        self.url = url
        self._sanitize_url()
        self.group_name, self.project_name, self.repo_location, self.branch, self.file_path = self._parse_url()
        self.url_type = self._get_url_type()

    def _parse_url(self) -> tuple[str, str, str, str | None, str | None]:
        pattern_matching_result = re.search(Github.GITHUB_URL_REGEX, self.url)
        if not pattern_matching_result:
            return None, None, None
        return \
            pattern_matching_result.groupdict()["group_name"], \
            pattern_matching_result.groupdict()["project_name"], \
            pattern_matching_result.groupdict()["repo_location"], \
            pattern_matching_result.groupdict().get("branch"), \
            pattern_matching_result.groupdict().get("file_path")

    def _sanitize_url(self):
        self.url = self.url.replace("/refs/heads", "")

    def _get_url_type(self) -> GithubURLType:
        if self.repo_location:
            if "issues" in self.repo_location or \
                "tree" in self.repo_location:
                # Issues page or project dir
                return Github.GithubURLType.WEBPAGE
            if "blob" in self.repo_location:
                # An specific file in the repo
                return Github.GithubURLType.SINGLE_FILE
            return Github.GithubURLType.WEBPAGE
        return Github.GithubURLType.REPO

    def get_content(self) -> tuple[str, str, list[str], list[str]]:
        if self.url_type == Github.GithubURLType.REPO:
            print("Clone the whole repo")
            return self._clone_repo()
        if self.url_type == Github.GithubURLType.WEBPAGE:
            print("Export like a webpage")
            return self._export_webpage()
        if self.url_type == Github.GithubURLType.SINGLE_FILE:
            print("Download single file")
            return self.file_path, None, [self._donwload_single_file()], []

    def _clone_repo(self):
        pass

    def _export_webpage(self):
        pass

    def _donwload_single_file(self):
        file_path = self._get_file_name_to_save()
        download_file(
            self._generate_single_file_download_url(),
            file_path
        )
        return file_path

    def _get_file_name_to_save(self) -> str:
        return self.file_path.replace("/", "-")

    def _generate_single_file_download_url(self):
        return f"https://github.com/{self.group_name}/{self.project_name}/raw/refs/heads/{self.branch}/{self.file_path}"
