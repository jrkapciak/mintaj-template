from urllib.parse import urlencode

from django.conf import settings
from django.shortcuts import render
from django.urls import include, path

from .urls import urlpatterns


def auth_start_demo(request):
    return render(request, "auth_start_demo.html")


def auth_demo(request, mode):
    discord_authorize_url = "https://discord.com/oauth2/authorize?" + urlencode(
        {
            "client_id": settings.DISCORD_CLIENT_ID,
            "redirect_uri": settings.DISCORD_REDIRECT_URI,
            "response_type": "code",
            "scope": "identify email",
        }
    )
    return render(
        request,
        "google_login_demo.html",
        {
            "google_client_id": settings.GOOGLE_CLIENT_ID,
            "discord_authorize_url": discord_authorize_url,
            "mode": mode,
        },
    )


urlpatterns += [
    path("__debug__/", include("debug_toolbar.urls")),
    path("demo/", auth_start_demo),
    path("demo/login/", auth_demo, {"mode": "login"}),
    path("demo/register/", auth_demo, {"mode": "register"}),
]
