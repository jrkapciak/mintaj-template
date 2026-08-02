from django.contrib import admin

from common.admin import TimeStampedUUIDAdmin

from .models import SocialAccount, User

admin.site.register(User, TimeStampedUUIDAdmin)
admin.site.register(SocialAccount, TimeStampedUUIDAdmin)
