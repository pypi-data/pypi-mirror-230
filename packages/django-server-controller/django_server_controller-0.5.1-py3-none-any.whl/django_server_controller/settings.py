from django.conf import settings


WSGI_SERVER_ENGINE = getattr(settings, "WSGI_SERVER_ENGINE", "uwsgi")
WSGI_PROJECT_NAME = getattr(settings, "WSGI_PROJECT_NAME", None)
WSGI_PROJECT_BASE = getattr(settings, "WSGI_PROJECT_BASE", None)
WSGI_LOGS_ROOT = getattr(settings, "WSGI_LOGS_ROOT", None)
WSGI_PIDFILE = getattr(settings, "WSGI_PIDFILE", None)
WSGI_CONFIG_FILE = getattr(settings, "WSGI_CONFIG_FILE", None)
WSGI_BIN = getattr(settings, "WSGI_BIN", None)
KILL_BIN = getattr(settings, "KILL_BIN", None)
