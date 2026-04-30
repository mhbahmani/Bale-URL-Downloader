from enum import Enum

import re


class Github:
    GITHUB_URL_REGEX = "http(s)?://github.com/(?P<group_name>\\w+)/(?P<project_name>\\w+)(/(?P<repo_location>[\\w/-]+))?"
    class GithubURLType(Enum):
        REPO = "repo"
        WEBPAGE = "webpage"
        SINGLE_FILE = "single_file"

    def __init__(self, url) -> None:
        self.url = url
        self.group_name, self.project_name, self.repo_location = self._parse_url()
        self.url_type = self._get_url_type()

    def _parse_url(self) -> GithubURLType:
        pattern_matching_result = re.search(Github.GITHUB_URL_REGEX, self.url)
        if not pattern_matching_result:
            return None, None, None
        return \
            pattern_matching_result.groupdict["group_name"], \
            pattern_matching_result.groupdict["project_name"], \
            pattern_matching_result.groupdict["repo_location"]

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
            return self._clone_repo()
        if self.url_type == Github.GithubURLType.WEBPAGE:
            return self._export_webpage()
        if self.url_type == Github.GithubURLType.SINGLE_FILE:
            return self._donwload_single_file()

    def _clone_repo(self):
        pass

    def _export_webpage(self):
        pass

    def _donwload_single_file(self):
        pass
