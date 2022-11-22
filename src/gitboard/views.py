
from django.conf import settings
from django.shortcuts import render
from django.http import FileResponse, HttpRequest, HttpResponse
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET


@require_GET
@cache_control(max_age=60 * 60 * 24, immutable=True, public=True)  # one day
def favicon(request: HttpRequest) -> HttpResponse:
    file = (settings.BASE_DIR / "static" / "favicon.ico").open("rb")
    return FileResponse(file)

def index(request, *args, **kwargs):
    return render(request, "gitboard/index.html")

