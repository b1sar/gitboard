from django.conf import settings
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET
from django.contrib.auth.models import AnonymousUser
from django.views.decorators.cache import cache_control
from django.http import FileResponse, HttpRequest, HttpResponse

from allauth.socialaccount.models import SocialToken

from gitboard.github_client.github_client import GithubClient


@require_GET
@cache_control(max_age=60 * 60 * 24, immutable=True, public=True)  # one day
def favicon(request: HttpRequest) -> HttpResponse:
    file = (settings.BASE_DIR / "static" / "favicon.ico").open("rb")
    return FileResponse(file)


def index(request, *args, **kwargs):
    # if user is not logged in return to login page
    if not request.user.is_authenticated:
        request.session.flush()
        return redirect("github_login")

    token = None
    token_cache_key = f"{request.user.username}-token"
    token_is_cached = token_cache_key in request.session
    if token_is_cached:
        token = request.session.get(token_cache_key)
    else:
        tokens = SocialToken.objects.filter(account__user=request.user)
        # handle the case where the logged in user is admin and does not have a token
        if tokens.count() <= 0:
            request.session.flush()
            return redirect("github_login")
        token = tokens.first().token
        request.session[token_cache_key] = token

    github = GithubClient(request.user, token)
    github.set_pagination_params(request)

    context = {
        "repo_list": github.get_repos(),
        "github_user": github.get_user(),
        "navigation": github.get_navigation()
    }
    return render(request, "gitboard/index.html", context)


def modal(request, name, *args, **kwargs):
    token = request.session[f"{request.user}-token"]
    git = GithubClient(user=request.user, token=token)
    context = {
        "repo_data": git.get_repo(name)
    }
    return render(request, "gitboard/hx/modal.html", context)
