
import djclick as click
from django_server_controller import settings
from django_server_controller import controllers


@click.group()
def main():
    pass

if settings.WSGI_SERVER_ENGINE.lower() == "gunicorn":
    controllers.GunicornController(
        project_name=settings.WSGI_PROJECT_NAME,
        project_base=settings.WSGI_PROJECT_BASE,
        config_file=settings.WSGI_CONFIG_FILE,
        logs_root=settings.WSGI_LOGS_ROOT,
        pidfile=settings.WSGI_PIDFILE,
        uwsgi_bin=settings.WSGI_BIN,
    ).make_controller(main, click)

elif settings.WSGI_SERVER_ENGINE.lower() == "uwsgi":
    controllers.UwsgiController(
        project_name=settings.WSGI_PROJECT_NAME,
        project_base=settings.WSGI_PROJECT_BASE,
        config_file=settings.WSGI_CONFIG_FILE,
        logs_root=settings.WSGI_LOGS_ROOT,
        pidfile=settings.WSGI_PIDFILE,
        uwsgi_bin=settings.WSGI_BIN,
        kill_bin=settings.KILL_BIN
    ).make_controller(main, click)

else:
    raise RuntimeError("WSGI_SERVER_ENGINE in pro/settings.py choices are: uwsgi (default), gunicorn...")


