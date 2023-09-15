import os
import logging

from zenutils import logutils
from orpc_server.cli import OrpcApplication

from .utils import start_jvm

_logger = logging.getLogger(__name__)


class JarExportApplication(OrpcApplication):
    default_server_class = "jarexps.server.JarExportServer"

    def main(self):
        logutils.setup(**self.config)
        _logger.info("JarExportApplication.main start...")
        classpaths = self.get_classpaths()
        _logger.info(
            "JarExportApplication.main start_jvm with classpath={}".format(classpaths)
        )
        start_jvm(classpaths)
        super().main()

    def get_classpaths(self):
        results = []
        classpaths = [
            os.path.abspath(x) for x in self.config.select("jarexps.classpaths", [])
        ]
        classpaths += [os.path.abspath(os.getcwd())]
        for classpath in classpaths:
            if not classpath in results:
                results.append(classpath)
        return results


app = JarExportApplication()
app_ctrl = app.get_controller()

if __name__ == "__main__":
    app_ctrl()
