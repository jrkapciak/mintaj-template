import uuid
from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedUUIDModel(models.Model):
    """
    An abstract base class model that provides a time-sortable UUID7 primary key and self updating
    ``created_at`` and ``updated_at``.
    """

    id = models.UUIDField(db_index=True, default=uuid.uuid7, editable=False, primary_key=True)
    created_at = models.DateTimeField(verbose_name=_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_("updated at"), auto_now=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return f"{self.id}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        if "update_fields" in kwargs:
            kwargs["update_fields"] = list(set(list(kwargs["update_fields"]) + ["updated_at"]))

        self.full_clean()
        return super().save(*args, **kwargs)

    def save_without_validation(self, *args: Any, **kwargs: Any):
        """
        Use caution! Omits full_clean() validation.
        """
        if "update_fields" in kwargs:
            kwargs["update_fields"] = list(set(list(kwargs["update_fields"]) + ["updated_at"]))
        return super().save(*args, **kwargs)
