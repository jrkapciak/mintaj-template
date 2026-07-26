from django.contrib.auth.models import AbstractUser

from common.models import TimeStampedUUIDModel


class User(AbstractUser, TimeStampedUUIDModel):  # type: ignore[django-manager-missing]
    pass
