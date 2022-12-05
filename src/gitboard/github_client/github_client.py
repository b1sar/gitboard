import re
import requests
from typing import Type, List
from urllib.parse import urlparse

from django.core.cache import cache
from django.contrib.auth.models import User
from gitboard.github_client.definitions import GithubUser, Repository

from gitboard.enums import PageType
from gitboard.github_client.types import Navigation


class GithubClient():
    GITHUB_BASE_URL = "https://api.github.com/"
    GITHUB_REPOS_URL = GITHUB_BASE_URL + "user/repos"
    REDIS_NONE = "KeyDoesNotExistInRedis"

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
        user_cache_key = f"{self.user.username}-user"
        cached_val = cache.get(user_cache_key, self.REDIS_NONE)
        if cached_val != self.REDIS_NONE:
            return GithubUser(cache.get(user_cache_key))

        resp = requests.get(
            self.GITHUB_BASE_URL + "user",
            headers=self._get_headers()
        )
        cache.set(user_cache_key, resp.json(), 300)
        githubUser = GithubUser(resp.json())
        return githubUser
    

    def get_repo(self, repo_name:str) -> Repository:
        repo_cache_key = f"{self.user.username}-{repo_name}"
        cached_value = cache.get(repo_cache_key, self.REDIS_NONE)
        if cached_value != self.REDIS_NONE:
            return Repository(cached_value)

        resp = requests.get(
            self.GITHUB_BASE_URL + "repos/" + self.user.username+ "/" + repo_name,
            headers=self._get_headers(),
        )
        raw_repo = resp.json()
        cache.set(repo_cache_key, raw_repo, 30)
        return Repository(raw_repo)

    def get_repos(self) -> List[Repository]:
        raw_repo_list = None
        paged_repos_key_for_cache = f"{self.user.username}-{self.per_page}-{self.page}"
        cached_val = cache.get(paged_repos_key_for_cache, self.REDIS_NONE)
        
        if cached_val != self.REDIS_NONE:
            print(type(cached_val))
            raw_repo_list = cached_val["raw_repo_list"]
            links = cached_val['links']
            self._update_navigation_params(links)
        else:  
            resp =  requests.get(
                self.GITHUB_REPOS_URL,
                headers=self._get_headers(),
                params= self._get_params(),
            )
            self._update_navigation_params(resp.links)
            raw_repo_list = resp.json()
            links = resp.links
            value_to_cache = {
                "raw_repo_list": raw_repo_list,
                "links": links
            }
            cache.set(paged_repos_key_for_cache, value_to_cache, 30)

        repo_list: List[Repository] = [Repository(repo) for repo in raw_repo_list]
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
    

    def _update_navigation_params(self, links:dict) -> None:
        for val in PageType:
            self._update_navigation_param(links, val)
        self._update_total_num_of_pages()


    def _update_navigation_param(self, links:dict, type: Type[PageType]) -> None:
        link: dict = links.get(type.value)
        if link is None:
            return
        parsed_url = urlparse(link.get('url'))
        setattr(self, type.value, f"?{str(parsed_url.query)}")
    

    def _update_total_num_of_pages(self):
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

    
    