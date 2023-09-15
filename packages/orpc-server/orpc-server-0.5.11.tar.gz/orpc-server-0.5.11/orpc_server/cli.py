import logging
import asyncio

from daemon_application import DaemonApplication
from zenutils import importutils


__all__ = [
    "OrpcApplication",
    "orpcd",
    "orpcd_ctrl",
]

_logger = logging.getLogger(__name__)


class OrpcApplication(DaemonApplication):
    default_server_class = "orpc_server.server.OrpcServer"

    def main(self):
        _logger.info("OrpcApplication.main start...")
        asyncio.run(self.async_main())

    async def async_main(self):
        _logger.info("OrpcApplication.async_main start...")
        self.server_class_name = self.config.select(
            "server.class", self.default_server_class
        )
        _logger.info(
            "OrpcApplication.async_main server_class_name={}".format(
                self.server_class_name
            )
        )
        self.server_class = importutils.import_from_string(self.server_class_name)
        self.server = self.server_class(self.config)
        await self.server.start()
        await self.server.serve_forever()


orpcd = OrpcApplication()
orpcd_ctrl = orpcd.get_controller()

if __name__ == "__main__":
    orpcd_ctrl()
