from typing import Type, Union
from dataclasses import dataclass


@dataclass(init=False)
class GithubUser():
    username: str
    id: str
    avatar_url: str
    html_url: str
    name: str
    company: str
    location: str
    email: str
    bio: str
    public_repos: int
    total_private_repos: int
    owned_private_repos: int

    def __init__(self, raw_user: dict) -> None:
        self.username = raw_user.get("login", None)
        self.id = raw_user.get("id", None)
        self.avatar_url = raw_user.get("avatar_url", None)
        self.html_url = raw_user.get("html_url", None)
        self.name = raw_user.get("name", "No name")
        self.company = raw_user.get("company", None)
        self.location = raw_user.get("location", "No location")
        self.email = raw_user.get("email", "No email")
        self.bio = raw_user.get("bio", None)
        self.public_repos = raw_user.get("public_repos", -1)
        self.total_private_repos = raw_user.get("total_private_repos", -1)
        self.owned_private_repos = raw_user.get("owned_private_repos", -1)


@dataclass(init=False)
class Repository():
    id: int
    node_id: str
    name: str
    full_name: str
    owner: Type[GithubUser]
    private: str
    html_url: str
    description: str
    fork: str
    url: str
    language: Union[str, None]
    stargazers_count: int
    default_branch: str
    has_issues: str
    visibility: str

    def __init__(self, raw_repository: dict) -> Type["Repository"]:
        self.id = raw_repository.get('id', None)
        self.node_id = raw_repository.get('node_id', None)
        self.name = raw_repository.get('name', None)
        self.full_name = raw_repository.get('full_name', None)
        self.owner = raw_repository.get('owner', "No owner")
        self.private = raw_repository.get('private', None)
        self.html_url = raw_repository.get('html_url', None)
        self.description = raw_repository.get('description', "No description")
        self.fork = raw_repository.get('fork', None)
        self.url = raw_repository.get('url', None)
        self.language = raw_repository.get('language', None)
        self.stargazers_count = raw_repository.get('stargazers_count', None)
        self.default_branch = raw_repository.get('default_branch', None)
        self.has_issues = raw_repository.get('has_issues', None)
        self.visibility = raw_repository.get('visibility', None)