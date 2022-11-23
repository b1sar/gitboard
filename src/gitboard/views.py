import requests

from django.conf import settings
from django.shortcuts import render
from django.http import FileResponse, HttpRequest, HttpResponse
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET

from allauth.socialaccount.models import SocialAccount

@require_GET
@cache_control(max_age=60 * 60 * 24, immutable=True, public=True)  # one day
def favicon(request: HttpRequest) -> HttpResponse:
    file = (settings.BASE_DIR / "static" / "favicon.ico").open("rb")
    return FileResponse(file)

def index(request, *args, **kwargs):
    account:SocialAccount = None
    try:
        account:SocialAccount = SocialAccount.objects.get(user=request.user)
    except Exception as ex:
        print(ex)
        return render(request, "gitboard/index.html", {})
    
    data = account.extra_data
    repos_url = account.extra_data['repos_url']
    repo_list = get_repos(repos_url)
    num_of_pages = 1 if len(repo_list) <=5 else len(repo_list)//5

    context = {
        "avatar_url": data['avatar_url'],
        "name": data['name'],
        "location": data['location'],
        "email": data['email'],
        "public_repos": data['public_repos'],
        "private_repos": data['owned_private_repos'],
        "repos_url": repos_url,
        "login": data['login'],
        "repo_list": repo_list,
        "num_of_repos": len(repo_list),
        "num_of_pages": num_of_pages,
    }

    rendered = render(request, "gitboard/index.html", context)
    return rendered


def modal(request, name, *args, **kwargs):
    repo_data = get_repo(name)
    context = {
        "repo_data": repo_data
    }
    return render(request, "gitboard/hx/modal.html", context)

def get_repo(name):
    response = requests.get("https://api.github.com/repos/b1sar/" + name)
    data = response.json()
    print(data)
    return data

def get_repos(repos_url):
    response = requests.get(repos_url)
    data = response.json()
    repo_list = []
    for entry in data:
        repo = {}
        repo['name'] = entry['name']
        repo['language'] = entry['language']
        repo['url'] = entry['url']
        repo_list.append(repo)
    return repo_list