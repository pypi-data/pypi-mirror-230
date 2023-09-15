from . import settings

if settings.DJANGO_DB_LOCK_AUTO_REGISTER_SERVICES and settings.DJANGO_DB_LOCK_AUTO_REGISTER_MODEL:
    from .server import django_db_lock_default_server
    urlpatterns = django_db_lock_default_server.get_urls()
else:
    urlpatterns = []
