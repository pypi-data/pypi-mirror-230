from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class DjangoDbLockConfig(AppConfig):
    name = 'django_db_lock'
    verbose_name = _("Django Db Lock")
