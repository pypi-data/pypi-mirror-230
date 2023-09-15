
import os
from posixpath import expandvars
import time

import click
import psutil
from fastutils import fsutils
from magic_import import import_from_string

from django.conf import settings


class ControllerBase(object):

    server_bin_name = None
    config_file_name = None

    def get_default_bin(self, bin_name):
        return fsutils.first_exists_file(
            "./{0}".format(bin_name),
            "~/bin/{0}".format(bin_name),
            "~/.bin/{0}".format(bin_name),
            "./bin/{0}".format(bin_name),
            "/usr/local/bin/{0}".format(bin_name),
            "/usr/bin/{0}".format(bin_name),
            "/bin/{0}".format(bin_name),
            default="{0}".format(bin_name),
        )

    def get_default_config_paths(self, ):
        if not self.config_file_name:
            raise RuntimeError("The controller doesn't have default config file name, so you must give config_file parameter...")
        application_init_filepath = import_from_string(settings.SETTINGS_MODULE.split(".")[0]).__file__
        application_base = os.path.dirname(application_init_filepath)
        paths = []
        for path in [
                "{project_base}/etc/{config_file_name}".format(config_file_name=self.config_file_name, project_base=self.project_base),
                "{project_base}/{config_file_name}".format(config_file_name=self.config_file_name, project_base=self.project_base),
                "./etc/{config_file_name}".format(config_file_name=self.config_file_name),
                "./{config_file_name}".format(config_file_name=self.config_file_name),
                "~/etc/{config_file_name}".format(config_file_name=self.config_file_name),
                "~/{config_file_name}".format(config_file_name=self.config_file_name),
                "{application_base}/{config_file_name}".format(config_file_name=self.config_file_name, application_base=application_base),
                self.config_file_name,
            ]:
            path = os.path.abspath(os.path.expanduser(os.path.expandvars(path)))
            if not path in paths:
                paths.append(path)
        return paths

    def get_default_config_file(self):
        paths = self.get_default_config_paths()
        return fsutils.first_exists_file(*paths)

    def __init__(self, project_name=None, project_base=None, config_file=None, logs_root=None, pidfile=None, server_bin=None, **kwargs):
        self.project_name = project_name or self.get_default_project_name()
        self.project_base = os.path.abspath(project_base or self.get_default_project_base())
        self.config_file = config_file or self.get_default_config_file()
        self.logs_root = logs_root or self.get_default_logs_root()
        self.pidfile = pidfile or self.get_default_pidfile()
        self.server_bin = server_bin or self.get_default_server_bin()
        self.application = self.get_application()

    def get_default_project_base(self):
        return os.getcwd()

    def get_default_project_name(self):
        return settings.SETTINGS_MODULE.split(".")[0]

    def get_default_logs_root(self):
        return os.path.abspath(os.path.join(self.project_base, "./logs/"))

    def get_default_pidfile(self):
        return os.path.abspath(os.path.join(self.project_base, "./{}.pid".format(self.project_name)))

    def get_application(self):
        return settings.SETTINGS_MODULE.split(".")[0] + ".wsgi:application"

    def get_default_server_bin(self):
        if not self.server_bin_name:
            raise NotImplementedError()

        return self.get_default_bin(self.server_bin_name)

    def get_server_pid(self):
        if not os.path.isfile(self.pidfile):
            return 0
        with open(self.pidfile, "r", encoding="utf-8") as fobj:
            return int(fobj.read().strip())

    def get_running_server_pid(self):
        pid = self.get_server_pid()
        if not pid:
            return 0
        if psutil.pid_exists(pid):
            return pid
        else:
            return 0

    def get_start_command(self):
        raise NotImplementedError()

    def get_stop_command(self):
        raise NotImplementedError()
    
    def get_reload_command(self):
        raise NotImplementedError()

    def get_stop_force_command(self):
        pid = self.get_running_server_pid()
        return f"kill -9 {pid}"

    def start(self):
        """Start server.
        """
        if not os.path.exists(self.logs_root):
            os.makedirs(self.logs_root, exist_ok=True)
        pid = self.get_running_server_pid()
        if pid:
            pid = self.get_server_pid()
            print("service is running: {}...".format(pid))
            os.sys.exit(1)
        else:
            print("Start server...")
            cmd = self.get_start_command()
            print("command:", cmd)
            os.system(cmd)
            print("server started!")

    def stop(self, timeout=60, force=False):
        """Stop server.
        """
        pid = self.get_running_server_pid()
        if pid:
            print("Stop server...")
            cmd = self.get_stop_command()
            print(cmd)
            os.system(cmd)
            # waiting for server stop
            try:
                p = psutil.Process(pid=pid)
                p.wait(timeout)
                print("server stopped!")
            except psutil.NoSuchProcess:
                print("server stopped!")
            except psutil.TimeoutExpired:
                print(f"server NOT stopped after {timeout} seconds...")
                if force:
                    print("Tring to kill the server by force...")
                    cmd = self.get_stop_force_command()
                    os.system(cmd)
                    try:
                        p = psutil.Process(pid=pid)
                        p.wait(timeout=5)
                        print("server stopped!")
                    except psutil.NoSuchProcess:
                        print("server stopped!")
                    except psutil.TimeoutExpired:
                        print("Kill by force still failed to stop the server!!!")
        else:
            print("service is NOT running!")

    def reload(self):
        """Reload server.
        """
        pid = self.get_running_server_pid()
        if pid:
            print("Reload server...")
            cmd = self.get_reload_command()
            print(cmd)
            os.system(cmd)
            print("server reloaded!")
        else:
            print("service is NOT running, try to start it!")
            self.start()

    def restart(self, wait_seconds=0, timeout=60, force=False):
        """Restart server.
        """
        self.stop(timeout=timeout, force=force)
        if wait_seconds:
            time.sleep(wait_seconds)
        self.start()

    def status(self):
        """Get server status.
        """
        pid = self.get_running_server_pid()
        if pid:
            print("server is running: {0}.".format(pid))
        else:
            print("server is NOT running.")
 
    def make_controller(self, main, click_lib):

        @main.command()
        def reload():
            """Reload server.
            """
            self.reload()

        @main.command()
        @click_lib.option("-w", "--wait-seconds", type=int, default=0, help="Wait some seconds after stop and before start the server. Default to 0.")
        @click.option("--timeout", type=float, default=60, help="Gracefull-stopping timeout seconds. Default to 60.")
        @click.option("--force", is_flag=True, help="Kill server by force if gracefull-stopping timeout. Default to False.")
        def restart(wait_seconds, timeout, force):
            """Restart server.
            """
            self.restart(wait_seconds, timeout=timeout, force=force)

        @main.command()
        def start():
            """Start server.
            """
            self.start()

        @main.command()
        @click.option("--timeout", type=float, default=60, help="Gracefull-stopping timeout seconds. Default to 60.")
        @click.option("--force", is_flag=True, help="Kill server by force if gracefull-stopping timeout. Default to False.")
        def stop(timeout, force):
            """Stop server.
            """
            self.stop(timeout=timeout, force=force)

        @main.command()
        def status():
            """Get server's status.
            """
            self.status()

        @main.command(name="show-wsgi-config-file")
        def show_wsgi_config_file():
            """Show current wsgi.conf.py path.
            """
            print(self.config_file)

        @main.command(name="show-wsgi-config-file-paths")
        def show_wsgi_config_file_paths():
            """Show wsgi.conf.py searching paths.
            """
            for path in self.get_default_config_paths():
                print(path)

        return main

class UwsgiController(ControllerBase):

    server_bin_name = "uwsgi"
    config_file_name = "wsgi.ini"

    def get_start_command(self):
        return "{server_bin} {config_file} --pythonpath={project_base} --pidfile={pidfile} --wsgi={application}".format(
            server_bin=self.server_bin,
            config_file=self.config_file,
            pidfile=self.pidfile,
            application=self.application,
            project_base=self.project_base,
            )

    def get_stop_command(self):
        return "{server_bin} --stop {pidfile}".format(
            server_bin=self.server_bin,
            pidfile=self.pidfile,
            )
    
    def get_reload_command(self):
        return "{server_bin} --reload {pidfile}".format(
            server_bin=self.server_bin,
            pidfile=self.pidfile,
            )


class GunicornController(ControllerBase):
    
    server_bin_name = "gunicorn"
    config_file_name = "wsgi.conf.py"

    def get_default_kill_bin(self):
        return self.get_default_bin("kill")

    def __init__(self, kill_bin=None, **kwargs):
        super().__init__(**kwargs)
        self.kill_bin = kill_bin or self.get_default_kill_bin()

    def get_start_command(self):
        return "{server_bin} --pythonpath={project_base} --config={config_file} --pid={pidfile} {application}".format(
            server_bin=self.server_bin,
            config_file=self.config_file,
            pidfile=self.pidfile,
            application=self.application,
            project_base=self.project_base,
        )

    def get_stop_command(self):
        pid = self.get_running_server_pid()
        if pid:
            return "{kill_bin} -TERM {pid}".format(kill_bin=self.kill_bin, pid=pid)
        else:
            return "echo NOT RUNNING..."

    def get_reload_command(self):
        pid = self.get_running_server_pid()
        if pid:
            return "{kill_bin} -HUP {pid}".format(kill_bin=self.kill_bin, pid=pid)
        else:
            return "echo NOT RUNNING..."
