

import os
import time
import signal
import logging

from daemon_application import daemon_start
from fastutils import sysutils

logger = logging.getLogger(__name__)


class DjangoCommandServer(object):

    stop_signal = signal.SIGINT

    def get_pidfile(self):
        if hasattr(self, "pidfile"):
            return self.pidfile
        else:
            return self.__class__.__name__.lower() + ".pid"

    def get_workspace(self):
        if hasattr(self, "workspace"):
            return self.workspace
        else:
            return os.getcwd()
    
    def get_daemon_application_pid(self):
        pidfile = self.get_pidfile()
        pid = sysutils.get_daemon_application_pid(pidfile)
        return pid

    def start(self, daemon):
        logger.info("{} server starting...".format(self.__class__.__name__))
        pidfile = self.get_pidfile()
        workspace = self.get_workspace()
        daemon_start(self._main, pidfile=pidfile, daemon=daemon, workspace=workspace)

    def stop(self):
        logger.info("{} server stopping...".format(self.__class__.__name__))
        pid = self.get_daemon_application_pid()
        if pid:
            os.kill(pid, self.stop_signal)
            logger.info("{} server stopped.".format(self.__class__.__name__))
        else:
            logger.info("{} server already stopped, did nothing.".format(self.__class__.__name__))

    def restart(self, daemon=True, wait=5):
        self.stop()
        logger.info("{} wait {} seconds to start...".format(self.__class__.__name__, wait))
        time.sleep(wait)
        self.start(daemon)

    def _main(self):
        logger.info("{} server started.".format(self.__class__.__name__))
        return self.main()

    def main(self):
        raise NotImplementedError()

    def setup(self, group):
        import djclick as click
    
        @group.command(name="start")
        @click.option("-f", "--foreground", is_flag=True, help="Run server in foreground mode.")
        def cmd_start(foreground):
            daemon = not foreground
            self.start(daemon)

        @group.command(name="stop")
        def cmd_stop():
            self.stop()

        @group.command(name="restart")
        @click.option("-f", "--foreground", is_flag=True, help="Run server in foreground mode.")
        @click.option("-w", "--wait", type=int, default=5, help="Seconds to sleep after stop and before start.")
        def cmd_restart(foreground, wait):
            daemon = not foreground
            self.restart(daemon, wait)

        return group

