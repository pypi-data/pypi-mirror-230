from django.conf import settings
from django.contrib import admin
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.humanize.templatetags import humanize

from .models import Lock
from . import settings

class LockAdmin(admin.ModelAdmin):
    list_display = ["lock_name", "worker_name", "lock_time", "expire_time", "time_remaining"]
    search_fields = ["lock_name", "worker_name"]

    def time_remaining(self, obj):
        expire_time = timezone.make_naive(obj.expire_time)
        return humanize.naturaltime(expire_time)
    time_remaining.short_description = _("Time Remaining")
    time_remaining.admin_order_field = "expire_time"

if settings.DJANGO_DB_LOCK_AUTO_REGISTER_ADMIN and settings.DJANGO_DB_LOCK_AUTO_REGISTER_MODEL:
    admin.site.register(Lock, LockAdmin)
