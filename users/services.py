from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from users.exceptions import EmailAlreadyTakenError
from users.models import SocialAccount, User

UserModel: type[User] = get_user_model()


class UserService:
    @staticmethod
    def register_user(email: str, password: str) -> User:
        """Creates a user with an email+password login. Username == email (USERNAME_FIELD is `username`)."""
        if UserModel.objects.filter(username=email).exists():
            raise EmailAlreadyTakenError(email)
        return UserModel.objects.create_user(username=email, email=email, password=password)

    @staticmethod
    def login_social_user(provider: str, provider_user_id: str) -> User | None:
        """Returns the existing user linked to this social account, or None if there is no link."""
        social_account = (
            SocialAccount.objects.select_related("user")
            .filter(provider=provider, provider_user_id=provider_user_id)
            .first()
        )
        return social_account.user if social_account else None

    @staticmethod
    def register_social_user(provider: str, provider_user_id: str, email: str) -> User:
        """Creates a user (or links to an existing one found by email) and stores the social account link."""
        user, _ = UserModel.objects.get_or_create(
            email=email,
            defaults={"username": email, "password": make_password(None)},
        )
        SocialAccount.objects.create(user=user, provider=provider, provider_user_id=provider_user_id, email=email)
        return user

    @staticmethod
    def register_or_login_social_user(provider: str, provider_user_id: str, email: str) -> tuple[User, bool]:
        """Returns (user, created). created=True when this is the first link of this social account to a user."""
        user = UserService.login_social_user(provider, provider_user_id)
        if user:
            return user, False
        return UserService.register_social_user(provider, provider_user_id, email), True
