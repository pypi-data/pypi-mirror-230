import logging

from zenutils import importutils
from orpc_server.server import OrpcServer

from .utils import get_value

_logger = logging.getLogger(__name__)


class JarExportProxy(object):
    def __init__(self, server, service_config):
        self.server = server
        self._touch_server_jar_share_instances()
        self.service_config = service_config
        self.klass = self.service_config.select("klass", "")
        if not self.klass:
            # 代码中不能使用class关键字，但配置文件中可以啊
            self.klass = self.service_config.select("class", "")
        self.method = self.service_config.select("method")
        self.args = self.service_config.select("args", []) or []  # klass实例化参数
        self.share = self.service_config.select("share", True)  # klass实例能否复用
        if self.share and (not self.klass in self.server._jar_share_instances):
            # 如果是可以共享实例的话，提前加载实例
            self.server._jar_share_instances[self.klass] = self.new_instance()

    def _touch_server_jar_share_instances(self):
        """确保server上有_jar_share_instances属性。"""
        if not hasattr(self.server, "_jar_share_instances"):
            setattr(self.server, "_jar_share_instances", {})

    async def __call__(self, *args):
        _logger.debug("calling service {}:{}...".format(self.klass, self.method))
        try:
            instance = self.get_instance()
        except Exception as error:
            msg = "get instance of class {} failed: error_message={}".format(
                self.klass, error
            )
            _logger.debug(msg)
            raise Exception(msg)
        try:
            method = getattr(instance, self.method)
        except Exception as error:
            msg = "get method {} from instance {} of class {} failed: error_message={}".format(
                self.method, instance, self.klass, error
            )
            _logger.debug(msg)
            raise Exception(msg)
        if not method:
            msg = "get method {} from instance {} of class {} failed...".format(
                self.method, instance, self.klass
            )
            raise Exception(msg)
        try:
            if args:
                result = method(*args)
            else:
                result = method()
        except Exception as error:
            msg = "call java method failed: instance={}, method={}, args={} error_message={}".format(
                instance, method, args, error
            )
            _logger.debug(msg)
            raise Exception(msg)
        try:
            result = get_value(result)
        except Exception as error:
            msg = "get result value failed: result={}, error={}".format(result, error)
            _logger.debug(msg)
            raise Exception(msg)
        return result

    def get_instance(self):
        if self.share:
            # share实例已经提前加载了
            return self.server._jar_share_instances[self.klass]
        else:
            return self.new_instance()

    def new_instance(self):
        _logger.debug("loading java class: {}...".format(self.klass))
        try:
            klass = importutils.import_from_string(self.klass)
        except Exception as error:
            msg = "load java class failed: class={}, error={}".format(self.klass, error)
            _logger.debug(msg)
            raise Exception(msg)
        if klass is None:
            msg = "load java class failed: class={}".format(self.klass)
            _logger.debug(msg)
            raise Exception(msg)
        if self.args:
            return klass(*self.args)
        else:
            return klass()


class JarExportServer(OrpcServer):
    def register_services(self):
        super().register_services()
        self.export_jar_services()

    def export_jar_services(self):
        _logger.info("JarExportServer.export_jar_services register services...")
        self._jar_share_instances = {}
        services = self.config.select("jarexps.services", {})
        for service_name, service_config in services.items():
            _logger.info(
                "JarExportServer.export_jar_services register service {}...".format(
                    service_name
                )
            )
            self.register_function(JarExportProxy(self, service_config), service_name)
        _logger.info(
            "JarExportServer.export_jar_services _jar_share_instances={}".format(
                self._jar_share_instances
            )
        )

    async def start(self):
        _logger.info("JarExportServer.start...")
        await super().start()
