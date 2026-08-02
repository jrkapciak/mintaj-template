import pytest

from users.models import SocialAccount, User
from users.services import UserService


@pytest.mark.django_db
def test_login_social_user_returns_none_when_no_account_linked() -> None:
    assert UserService.login_social_user("google", "google-uid-1") is None


@pytest.mark.django_db
def test_login_social_user_returns_linked_user() -> None:
    registered = UserService.register_social_user("google", "google-uid-1", "gracz@gmail.com")

    found = UserService.login_social_user("google", "google-uid-1")

    assert found is not None
    assert found.pk == registered.pk


@pytest.mark.django_db
def test_register_social_user_creates_user_and_social_account() -> None:
    user = UserService.register_social_user("google", "google-uid-1", "gracz@gmail.com")

    assert user.email == "gracz@gmail.com"
    assert SocialAccount.objects.filter(provider="google", provider_user_id="google-uid-1", user=user).exists()


@pytest.mark.django_db
def test_register_social_user_links_to_existing_user_found_by_email() -> None:
    existing = User.objects.create_user(username="gracz@gmail.com", email="gracz@gmail.com")

    user = UserService.register_social_user("discord", "discord-uid-1", "gracz@gmail.com")

    assert user.pk == existing.pk


@pytest.mark.django_db
def test_creates_new_user_and_social_account() -> None:
    user, created = UserService.register_or_login_social_user("google", "google-uid-1", "gracz@gmail.com")

    assert created is True
    assert user.email == "gracz@gmail.com"
    assert SocialAccount.objects.filter(provider="google", provider_user_id="google-uid-1", user=user).exists()


@pytest.mark.django_db
def test_reuses_existing_social_account() -> None:
    first_user, _ = UserService.register_or_login_social_user("google", "google-uid-1", "gracz@gmail.com")

    second_user, created = UserService.register_or_login_social_user("google", "google-uid-1", "gracz@gmail.com")

    assert created is False
    assert second_user.pk == first_user.pk
    assert User.objects.count() == 1
    assert SocialAccount.objects.count() == 1


@pytest.mark.django_db
def test_links_social_account_to_existing_user_found_by_email() -> None:
    existing = User.objects.create_user(username="gracz@gmail.com", email="gracz@gmail.com")

    user, created = UserService.register_or_login_social_user("discord", "discord-uid-1", "gracz@gmail.com")

    assert created is True
    assert user.pk == existing.pk
    assert SocialAccount.objects.filter(provider="discord", provider_user_id="discord-uid-1", user=existing).exists()


@pytest.mark.django_db
def test_same_email_different_providers_creates_separate_social_accounts() -> None:
    google_user, _ = UserService.register_or_login_social_user("google", "google-uid-1", "gracz@example.com")
    discord_user, _ = UserService.register_or_login_social_user("discord", "discord-uid-1", "gracz@example.com")

    assert google_user.pk == discord_user.pk
    assert SocialAccount.objects.count() == 2
