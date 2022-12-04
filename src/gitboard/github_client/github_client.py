import re
from typing import Type, List
from urllib.parse import urlparse
import requests
from gitboard.enums import PageType
from django.contrib.auth.models import User
from gitboard.github_client.definitions import GithubUser, Repository

from gitboard.github_client.types import Navigation


class GithubClient():
    GITHUB_BASE_URL = "https://api.github.com/"
    GITHUB_REPOS_URL = GITHUB_BASE_URL + "user/repos"

    def __init__(self, user:User, token:str, per_page:int = 5, page:int = 1) -> Type["GithubClient"]:
        self.user:User = user
        self.token:str = token
        self.per_page:int = per_page
        self.page:int = page
        self.prev: str = None
        self.next: str = None
        self.last: str = None
        self.first: str = None
        self.last_page: int = None
    
    def get_user(self) -> GithubUser:
        resp = requests.get(
            self.GITHUB_BASE_URL + "user",
            headers=self._get_headers()
        )
        githubUser = GithubUser(resp.json())
        return githubUser
    
    def get_repo(self, repo_name:str) -> Repository:
        resp = requests.get(
            self.GITHUB_BASE_URL + "repos/" + self.user.username+ "/" + repo_name,
            headers=self._get_headers(),
        )
        raw_repo = resp.json()
        return Repository(raw_repo)

    def get_repos(self, per_page: int = 5, page: int = 1) -> List[Repository]:
        resp =  requests.get(
            self.GITHUB_REPOS_URL,
            headers=self._get_headers(),
            params= self._get_params(),
        )
        self._update_navigation_params(resp)
        raw_repo_list = resp.json()
        repo_list: List[Repository] = []
        for repo in raw_repo_list:
            repo_list.append(Repository(repo))
        return repo_list
    

    def _get_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.token}"
        }
    

    def _get_params(self) -> dict:
        return {
            "per_page": self.per_page,
            "page": self.page
        }
    

    def _update_navigation_params(self, response: Type[requests.Response]) -> None:
        for val in PageType:
            self._update_navigation_param(response, val)
        self._update_total_num_of_pages(response)


    def _update_navigation_param(self, response: Type[requests.Response], type: Type[PageType]) -> None:
        link: dict = response.links.get(type.value)
        if link is None:
            return
        parsed_url = urlparse(link.get('url'))
        setattr(self, type.value, f"?{str(parsed_url.query)}")
    

    def _update_total_num_of_pages(self, response: Type[requests.Response]):
        if not self.last:
            return
        page_pattern = re.compile("&page=(\d{1,4})")
        match = page_pattern.search(self.last)
        if match:
            self.last_page = int(match.group(1))
    

    def get_navigation(self) -> Navigation:
        return {
            "current_page": self.page,
            "prev": self.prev,
            "next": self.next,
            "last": self.last,
            "first": self.first,
            "last_page": self.last_page
        }


    def set_pagination_params(self,request):
        page = request.GET.get('page')
        per_page = request.GET.get('per_page')
        if page and per_page:
            self.page = int(page)
            self.per_page = int(per_page)
    
    
    def get_pagination(self):
        pages = []
        for i in range(1, self.last_page + 1):
            pages.append(
                {
                    "url": self.GITHUB_REPOS_URL,
                    "is_current": True if self.page == i else False
                }
            )

    
    