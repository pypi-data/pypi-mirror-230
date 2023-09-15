import os
import logging
from urllib.parse import urljoin

from fastutils import logutils
from daemon_application.app import DaemonApplication
from django_simpletask.services import SimpleTaskService

logger = logging.getLogger(__name__)

class DjangoSimpleTaskEngine(DaemonApplication):

    def main(self):
        logutils.setup(**self.config)

        task_server_url = self.config.get("task_server_url", None)
        task_server_aclkey = self.config.get("task_server_aclkey", None)

        if (not task_server_url) or (not task_server_aclkey):
            logger.error("DjangoSimpleTaskEngine failed to start for no [task_server_url] and [task_server_aclkey] configed...")
            os.sys.exit(1)

        service = SimpleTaskService(**self.config)
        service.start()
        service.join()


application = DjangoSimpleTaskEngine().get_controller()

if __name__ == "__main__":
    application()
