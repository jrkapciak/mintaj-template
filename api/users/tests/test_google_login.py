import jwt
import pytest

from users.models import SocialAccount, User

GOOGLE_LOGIN_URL = "/api/users/google-login"


def _mock_google_token(mocker, claims: dict) -> None:
    mocker.patch(
        "api.users.router._google_jwks_client.get_signing_key_from_jwt",
        return_value=mocker.Mock(key="fake-key"),
    )
    mocker.patch("api.users.router.jwt.decode", return_value=claims)


@pytest.mark.django_db
def test_google_login_creates_new_user_and_returns_tokens(client, mocker) -> None:
    _mock_google_token(mocker, {"sub": "google-uid-1", "email": "gracz@gmail.com", "email_verified": True})

    response = client.post(
        GOOGLE_LOGIN_URL,
        data={"id_token": "fake-google-id-token"},
        content_type="application/json",
    )

    assert response.status_code == 200
    body = response.json()
    assert "access" in body and "refresh" in body
    assert User.objects.filter(email="gracz@gmail.com").count() == 1
    assert SocialAccount.objects.filter(provider="google", provider_user_id="google-uid-1").exists()


@pytest.mark.django_db
def test_google_login_reuses_existing_user_by_email(client, mocker) -> None:
    existing = User.objects.create_user(username="gracz@gmail.com", email="gracz@gmail.com")
    _mock_google_token(mocker, {"sub": "google-uid-1", "email": "gracz@gmail.com", "email_verified": True})

    response = client.post(
        GOOGLE_LOGIN_URL,
        data={"id_token": "fake-google-id-token"},
        content_type="application/json",
    )

    assert response.status_code == 200
    assert User.objects.count() == 1
    assert User.objects.get().pk == existing.pk


@pytest.mark.django_db
def test_google_login_reuses_existing_social_account(client, mocker) -> None:
    _mock_google_token(mocker, {"sub": "google-uid-1", "email": "gracz@gmail.com", "email_verified": True})

    first = client.post(
        GOOGLE_LOGIN_URL, data={"id_token": "fake-google-id-token"}, content_type="application/json"
    ).json()
    second = client.post(
        GOOGLE_LOGIN_URL, data={"id_token": "fake-google-id-token"}, content_type="application/json"
    ).json()

    assert User.objects.count() == 1
    assert SocialAccount.objects.count() == 1
    assert first["access"] != second["access"]


@pytest.mark.django_db
def test_google_login_rejects_unverified_email(client, mocker) -> None:
    _mock_google_token(mocker, {"sub": "google-uid-1", "email": "gracz@gmail.com", "email_verified": False})

    response = client.post(
        GOOGLE_LOGIN_URL,
        data={"id_token": "fake-google-id-token"},
        content_type="application/json",
    )

    assert response.status_code == 401
    assert not User.objects.exists()


@pytest.mark.django_db
def test_google_login_rejects_invalid_token(client, mocker) -> None:
    mocker.patch(
        "api.users.router._google_jwks_client.get_signing_key_from_jwt",
        side_effect=jwt.PyJWTError("invalid token"),
    )

    response = client.post(
        GOOGLE_LOGIN_URL,
        data={"id_token": "not-a-real-token"},
        content_type="application/json",
    )

    assert response.status_code == 401
    assert not User.objects.exists()
