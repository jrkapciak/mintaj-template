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

from api.auth import JWTAuth
from users.services import UserService

logger = logging.getLogger(__name__)

router = Router(tags=["Users & Authentication"])

_google_jwks_client = jwt.PyJWKClient("https://www.googleapis.com/oauth2/v3/certs")


class GoogleLoginIn(Schema):
    id_token: str


class TokenOut(Schema):
    access: str
    refresh: str


def _issue_tokens(provider: str, provider_user_id: str, email: str) -> dict[str, str]:
    user, created = UserService.register_or_login_social_user(provider, provider_user_id, email)
    logger.info("%s: %s user %s", provider, "registered new" if created else "logged in existing", email)

    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


@router.post(
    "/google-login",
    response=TokenOut,
    summary="Register/login via Google account",
)
def google_login(request: HttpRequest, payload: GoogleLoginIn) -> dict[str, str]:
    logger.info("google_login: received id_token (%d chars)", len(payload.id_token))

    try:
        signing_key = _google_jwks_client.get_signing_key_from_jwt(payload.id_token)
        claims = jwt.decode(
            payload.id_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=settings.GOOGLE_CLIENT_ID,
            issuer=["https://accounts.google.com", "accounts.google.com"],
        )
    except jwt.PyJWTError as e:
        logger.warning("google_login: token rejected — %s", e)
        raise HttpError(401, f"Invalid Google token: {e}")

    if not claims.get("email_verified"):
        logger.warning("google_login: unverified email for %s", claims.get("email"))
        raise HttpError(401, "Google account email is not verified.")

    return _issue_tokens("google", claims["sub"], claims["email"])


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