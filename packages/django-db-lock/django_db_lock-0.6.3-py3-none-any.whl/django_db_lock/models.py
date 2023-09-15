from django.db import models
from django.utils.translation import ugettext_lazy as _
from . import settings



class LockBase(models.Model):
    lock_name = models.CharField(max_length=128, unique=True, verbose_name=_("Lock Name"))
    worker_name = models.CharField(max_length=128, verbose_name=_("Worker(Locker) Name"))
    lock_time = models.DateTimeField(verbose_name=_("Lock Time"))
    expire_time = models.DateTimeField(verbose_name=_("Expired Time"))

    class Meta:
        abstract = True

    def __str__(self):
        return self.lock_name

if settings.DJANGO_DB_LOCK_AUTO_REGISTER_MODEL:

    class Lock(LockBase):

        class Meta:
            app_label = settings.DJANGO_DB_LOCK_APP_LABEL
            verbose_name = _("Lock")
            verbose_name_plural = _("Locks")
