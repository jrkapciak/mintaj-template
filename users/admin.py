from django.contrib import admin

from common.admin import TimeStampedUUIDAdmin

from .models import User

admin.site.register(User, TimeStampedUUIDAdmin)
