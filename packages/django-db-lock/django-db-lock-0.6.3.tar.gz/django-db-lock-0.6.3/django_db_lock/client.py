
import uuid
import json
import urllib
import logging
import requests

from . import settings


logger = logging.getLogger(__name__)


class DjangoDbLock(object):
    default_timeout = 60

    def __init__(self, server, lock_name, worker_name=None, timeout=None):
        self.server = server
        self.lock_name = lock_name
        self.worker_name = worker_name or str(uuid.uuid4())
        self.timeout = timeout or self.default_timeout
        self.locked = None

    def __enter__(self):
        self.locked = self.server.acquire_lock(self.lock_name, self.worker_name, self.timeout)
        return self.locked
    
    def __exit__(self, type, value, traceback):
        if self.locked:
            self.server.release_lock(self.lock_name, self.worker_name)


class HttpclientServer(object):

    def __init__(self, api_server_url, acquire_lock_path="acquireLock", release_lock_path="releaseLock"):
        """api_server_url likes "http://127.0.0.1:8000/dblock/", always add the last slash.
        """
        self.api_server_url = api_server_url
        self.acquire_lock_path = acquire_lock_path
        self.release_lock_path = release_lock_path
        self.api_acquire_lock_url = urllib.parse.urljoin(api_server_url, acquire_lock_path)
        self.api_release_lock_url = urllib.parse.urljoin(api_server_url, release_lock_path)


    def acquire_lock(self, lock_name, worker_name, timeout):
        try:
            params = {
                "lockName": lock_name,
                "workerName": worker_name,
                "timeout": timeout,
            }
            response = requests.get(self.api_acquire_lock_url, params=params)
            data = json.loads(response.content)
            return data["result"]
        except Exception:
            logger.exception("acquire lock via http failed...")
            return False

    def release_lock(self, lock_name, worker_name):
        try:
            params = {
                "lockName": lock_name,
                "workerName": worker_name,
            }
            response = requests.get(self.api_release_lock_url, params=params)
            data = json.loads(response.content)
            return data["result"]
        except Exception:
            logger.exception("release lock via http failed...")
            return False


def get_default_lock_service():
    if settings.DJANGO_DB_LOCK_AUTO_REGISTER_MODEL:
        from .server import django_db_lock_default_server
        return django_db_lock_default_server
    else:
        if not settings.DJANGO_DB_LOCK_API_SERVER:
            raise RuntimeError("You must set DJANGO_DB_LOCK_API_SERVER in settings.py...")
        return HttpclientServer(settings.DJANGO_DB_LOCK_API_SERVER, settings.DJANGO_DB_LOCK_ACQUIRE_LOCK_PATH, settings.DJANGO_DB_LOCK_RELEASE_LOCK_PATH)
