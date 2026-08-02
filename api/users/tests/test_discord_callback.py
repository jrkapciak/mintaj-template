import io
import json
from contextlib import contextmanager
from urllib.error import HTTPError

import pytest

from users.models import SocialAccount, User

DISCORD_CALLBACK_URL = "/api/users/discord-callback"


def _mock_discord_responses(mocker, token_response: dict, user_response: dict) -> None:
    @contextmanager
    def fake_urlopen(request, *args, **kwargs):
        body = token_response if "oauth2/token" in request.full_url else user_response
        yield mocker.Mock(read=lambda: json.dumps(body).encode())

    mocker.patch("api.users.router.urllib.request.urlopen", side_effect=fake_urlopen)


@pytest.mark.django_db
def test_discord_callback_creates_new_user_and_redirects_with_tokens(client, mocker) -> None:
    _mock_discord_responses(
        mocker,
        token_response={"access_token": "fake-discord-access-token"},
        user_response={"id": "123", "email": "gracz@discord.com", "verified": True},
    )

    response = client.get(DISCORD_CALLBACK_URL, {"code": "fake-code"})

    assert response.status_code == 302
    assert response.url.startswith("/demo/register/?")
    assert "access=" in response.url and "refresh=" in response.url
    assert User.objects.filter(email="gracz@discord.com").count() == 1
    assert SocialAccount.objects.filter(provider="discord", provider_user_id="123").exists()


@pytest.mark.django_db
def test_discord_callback_reuses_existing_user_by_email(client, mocker) -> None:
    existing = User.objects.create_user(username="gracz@discord.com", email="gracz@discord.com")
    _mock_discord_responses(
        mocker,
        token_response={"access_token": "fake-discord-access-token"},
        user_response={"id": "123", "email": "gracz@discord.com", "verified": True},
    )

    response = client.get(DISCORD_CALLBACK_URL, {"code": "fake-code"})

    assert response.status_code == 302
    assert User.objects.count() == 1
    assert User.objects.get().pk == existing.pk


@pytest.mark.django_db
def test_discord_callback_reuses_existing_social_account(client, mocker) -> None:
    _mock_discord_responses(
        mocker,
        token_response={"access_token": "fake-discord-access-token"},
        user_response={"id": "123", "email": "gracz@discord.com", "verified": True},
    )

    client.get(DISCORD_CALLBACK_URL, {"code": "code-1"})
    client.get(DISCORD_CALLBACK_URL, {"code": "code-2"})

    assert User.objects.count() == 1
    assert SocialAccount.objects.count() == 1


@pytest.mark.django_db
def test_discord_callback_rejects_unverified_email(client, mocker) -> None:
    _mock_discord_responses(
        mocker,
        token_response={"access_token": "fake-discord-access-token"},
        user_response={"id": "123", "email": "gracz@discord.com", "verified": False},
    )

    response = client.get(DISCORD_CALLBACK_URL, {"code": "fake-code"})

    assert response.status_code == 401
    assert not User.objects.exists()


@pytest.mark.django_db
def test_discord_callback_rejects_failed_token_exchange(client, mocker) -> None:
    mocker.patch(
        "api.users.router.urllib.request.urlopen",
        side_effect=HTTPError("url", 400, "Bad Request", {}, io.BytesIO(b"{}")),
    )

    response = client.get(DISCORD_CALLBACK_URL, {"code": "invalid-code"})

    assert response.status_code == 401
    assert not User.objects.exists()
