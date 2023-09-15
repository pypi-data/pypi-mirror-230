import logging
import asyncio

import bizerror
from zenutils import funcutils
from zenutils import dictutils
from zenutils import importutils

from orpc.protocol import DEFAULT_ORPC_PORT
from orpc.protocol import OrpcProtocolWriter
from orpc.protocol import OrpcProtocolReader
from orpc.protocol import OrpcResponse
from orpc.exceptions import ServiceNotFound
from orpc.exceptions import AuthenticationRequired
from orpc.asio import AsioReader
from orpc.asio import AsioWriter

from .services import SystemService
from .services import DebugService
from .services import AuthenticationService

_logger = logging.getLogger(__name__)

__all__ = [
    "OrpcHandler",
    "OrpcServer",
]


DEFAULT_ORPC_HANDLER_ASIO_WRITER_BUFFER_SIZE = 1024 * 1024 * 4


class OrpcHandler(object):
    def __init__(self, config, server, reader, writer):
        self.config = config
        self.asio_writer_buffer_size = self.config.select(
            "orpc.handler.asio-writer-buffer-size",
            DEFAULT_ORPC_HANDLER_ASIO_WRITER_BUFFER_SIZE,
        )
        self.server = server
        self.reader = reader
        self.writer = writer
        self.asio_reader = AsioReader(reader)
        self.asio_writer = AsioWriter(writer, buffering=self.asio_writer_buffer_size)
        self.protocol_reader = OrpcProtocolReader(self.asio_reader)
        self.protocol_writer = OrpcProtocolWriter(self.asio_writer)
        self.socket = reader._transport.get_extra_info("socket")
        self.authenticated = False  # 连接是否已认证
        self.uid = None  # 连接已认证的用户UID


class OrpcServer(object):
    default_handler_class = "orpc_server.server.OrpcHandler"
    default_authentication_exemptions = [
        "auth.login",
        "debug.ping",
    ]

    def __init__(self, config=None):
        self.config = dictutils.Object(config or {})
        self.handler_class = importutils.import_from_string(
            self.config.select("server.handler_class", self.default_handler_class)
        )
        self.funcs = {}
        self.authentication_enable = self.config.select("authentication.enable", False)
        self.authentication_exemptions = self.config.select(
            "authentication.exemptions", self.default_authentication_exemptions
        )
        self.register_services()

    def register_function(self, method, name):
        self.funcs[name] = method

    async def start(self):
        host = self.config.select("server.host", "0.0.0.0")
        port = self.config.select("server.port", DEFAULT_ORPC_PORT)
        self.core = await asyncio.start_server(self.handle, host, port)
        self.server_addresses = ", ".join(
            str(sock.getsockname()) for sock in self.core.sockets
        )
        _logger.info(
            "Serving on {addresses}...".format(addresses=self.server_addresses)
        )

    async def handle(self, reader, writer):
        handler = self.handler_class(self.config, self, reader, writer)
        _logger.debug(
            "OrpcServer.handle on remote client connected: {}".format(handler.socket)
        )
        try:
            while True:
                response_result = None
                response_error = None
                try:
                    request = await handler.protocol_reader.async_read_request()
                except asyncio.exceptions.IncompleteReadError:
                    _logger.debug(
                        "OrpcServer.handle remote client closed: {}".format(
                            handler.socket
                        )
                    )
                    break
                try:
                    response_result = await self.dispath(request, handler)
                    response_error = None
                except Exception as error:
                    response_result = None
                    response_error = bizerror.BizError(error)
                if response_error:
                    try:
                        await handler.protocol_writer.async_write_response(
                            code=response_error.code, message=response_error.message
                        )
                    except Exception as error:
                        _logger.error(
                            "OrpcServer.handle async write error response failed: error_message={}...".format(
                                error
                            )
                        )
                        break
                else:
                    try:
                        if isinstance(response_result, OrpcResponse):
                            await handler.protocol_writer.async_write_response(
                                code=response_result.code,
                                headers=response_result.headers,
                                message=response_result.message,
                                result=response_result.result,
                                files=response_result.files,
                            )
                        else:
                            await handler.protocol_writer.async_write_response(
                                result=response_result
                            )
                    except Exception as error:
                        _logger.error(
                            "OrpcServer.handle async write success response failed: error_message={}...".format(
                                error
                            )
                        )
                        break
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception as error:
                _logger.debug(
                    "OrpcServer.close client writer failed: error_message={}...".format(
                        error
                    )
                )

    async def dispath(self, request, handler):
        if self.authentication_enable:
            if not handler.authenticated:
                if not request.path in self.authentication_exemptions:
                    raise AuthenticationRequired()

        func = self.funcs.get(request.path, None)
        if not func:
            raise ServiceNotFound()
        data = {
            "_request": request,
            "_path": request.path,
            "_headers": request.headers,
            "_args": request.args,
            "_kwargs": request.kwargs,
            "_body": request.body,
            "_files": request.files,
            "_inject_args": request.args,
            "_server": self,
            "_config": self.config,
            "_handler": handler,
        }
        data.update(request.headers)
        data.update(request.kwargs)
        return await funcutils.call_with_inject(func, data)

    async def serve_forever(self):
        async with self.core:
            await self.core.serve_forever()

    def register_services(self):
        # 注册默认的系统服务
        enable_system_service = self.config.select("enable-system-service", True)
        if enable_system_service:
            self._system_service = SystemService()
            self._system_service.register_to(self)
        # 注册默认的调试服务
        enable_debug_service = self.config.select("enable-debug-service", True)
        if enable_debug_service:
            self._debug_service = DebugService()
            self._debug_service.register_to(self)
        # 注册默认的认证服务
        enable_authentication_service = self.config.select(
            "enable-authentication-service", True
        )
        if enable_authentication_service:
            self._authentication_service = AuthenticationService()
            self._authentication_service.register_to(self)
        # 根据配置文件加载服务
        service_configs = self.config.select("services", [])
        for service_config in service_configs:
            service_class_name = service_config.select("class", None)
            if not service_class_name:
                msg = "Service config missing class field, service_config={service_config}...".format(
                    service_config=service_config,
                )
                _logger.warning(msg)
                continue
            Service = importutils.import_from_string(service_class_name)
            if not Service:
                msg = "Service class {service_class_name} not found...".format(
                    service_class_name=service_class_name,
                )
                _logger.error(msg)
                continue
            msg = "Loading services from {service_class_name}...".format(
                service_class_name=service_class_name,
            )
            _logger.info(msg)
            service_args = service_config.select("args", [])
            service_kwargs = service_config.select("kwargs", {})
            Service(self.config, *service_args, **service_kwargs).register_to(
                self,
            )
