from django.contrib.auth.models import AbstractUser
from django.db import models

from common.models import TimeStampedUUIDModel


class User(AbstractUser, TimeStampedUUIDModel):  # type: ignore[django-manager-missing]
    pass


class SocialAccount(TimeStampedUUIDModel):
    class Provider(models.TextChoices):
        GOOGLE = "google", "Google"
        DISCORD = "discord", "Discord"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="social_accounts")
    provider = models.CharField(max_length=20, choices=Provider.choices)
    provider_user_id = models.CharField(max_length=255)
    email = models.EmailField()

    class Meta:
        unique_together = ("provider", "provider_user_id")

    def __str__(self) -> str:
        return f"{self.provider}:{self.provider_user_id} -> {self.user_id}"
