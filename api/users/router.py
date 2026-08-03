import json
import logging
import urllib.error
import urllib.parse
import urllib.request

import jwt
from django.conf import settings
from django.http import HttpRequest, HttpResponseRedirect
from ninja import Router, Schema
from ninja.errors import HttpError
from ninja_jwt.tokens import RefreshToken
from urllib.parse import urlencode

from api.auth import JWTAuth
from users.services import UserService

logger = logging.getLogger(__name__)

router = Router(tags=["Users & Authentication"])

class TokenOut(Schema):
    access: str
    refresh: str


def _issue_tokens(provider: str, provider_user_id: str, email: str) -> dict[str, str]:
    user, created = UserService.register_or_login_social_user(provider, provider_user_id, email)
    logger.info("%s: %s user %s", provider, "registered new" if created else "logged in existing", email)

    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


@router.get("/google/login", auth=None)
def google_auth(request: HttpRequest):

    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
    }

    return HttpResponseRedirect(
        "https://accounts.google.com/o/oauth2/v2/auth?"
        + urlencode(params)
    )

@router.get(
    "/google-callback",
    auth=None,
    summary="Google OAuth callback",
)
def google_oauth_callback(
    request: HttpRequest,
    code: str,
):
    token_data = urllib.parse.urlencode(
        {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
            "code": code,
        }
    ).encode()

    token_request = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=token_data,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )

    try:
        with urllib.request.urlopen(token_request) as response:
            token_response = json.loads(response.read())
    except urllib.error.HTTPError as e:
        raise HttpError(400, e.read().decode())

    access_token = token_response["access_token"]

    user_request = urllib.request.Request(
        "https://openidconnect.googleapis.com/v1/userinfo",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    with urllib.request.urlopen(user_request) as response:
        profile = json.loads(response.read())

    if not profile.get("email_verified"):
        raise HttpError(401, "Email not verified")

    tokens = _issue_tokens(
        "google",
        profile["sub"],
        profile["email"],
    )

    redirect_url = "/demo/register/?" + urllib.parse.urlencode(tokens)
    return HttpResponseRedirect(redirect_url)

@router.get(
    "/discord-callback",
    summary="Discord OAuth2 callback — exchanges code for tokens, registers/logs in and redirects back",
)
def discord_callback(request: HttpRequest, code: str) -> HttpResponseRedirect:
    logger.info("discord_callback: received code")

    token_body = urllib.parse.urlencode(
        {
            "client_id": settings.DISCORD_CLIENT_ID,
            "client_secret": settings.DISCORD_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.DISCORD_REDIRECT_URI,
        }
    ).encode()

    try:
        token_req = urllib.request.Request(
            settings.DISCORD_TOKEN_URL,
            data=token_body,
            headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": settings.DISCORD_USER_AGENT},
        )
        with urllib.request.urlopen(token_req) as resp:
            access_token = json.loads(resp.read())["access_token"]

        user_req = urllib.request.Request(
            settings.DISCORD_USER_URL,
            headers={"Authorization": f"Bearer {access_token}", "User-Agent": settings.DISCORD_USER_AGENT},
        )
        with urllib.request.urlopen(user_req) as resp:
            discord_user = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        logger.warning("discord_callback: code exchange/profile fetch failed — %s: %s", e, e.read())
        raise HttpError(401, "Failed to log in via Discord.")

    email = discord_user.get("email")
    if not email or not discord_user.get("verified"):
        logger.warning("discord_callback: no verified email for Discord account %s", discord_user.get("id"))
        raise HttpError(401, "Discord account does not have a verified email address.")

    tokens = _issue_tokens("discord", discord_user["id"], email)

    redirect_url = "/demo/register/?" + urllib.parse.urlencode(tokens)
    return HttpResponseRedirect(redirect_url)


@router.get(
    "/me",
    response=str,
    auth=JWTAuth(),
    summary="Returns a simple text status message"
)
def get_status_text(request):
    return "Server is running fine and the client is connected."
