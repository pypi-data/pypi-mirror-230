import re
import asyncio

from zenutils import serviceutils
from zenutils import hashutils

from orpc.exceptions import ServiceNotFound


__all__ = [
    "DebugService",
    "SystemService",
    "AuthenticationService",
]


SIGNATURES_NOT_SUPPORTED = "signatures not supported"


class DebugService(serviceutils.ServiceBase):
    namespace = "debug"

    async def ping(self):
        return "pong"

    async def echo(self, msg):
        return msg

    async def sleep(self, delay):
        await asyncio.sleep(delay)


class SystemService(serviceutils.ServiceBase):
    namespace = "system"

    async def listMethods(self, _server):
        """
        @signature {{{
            [
                [
                    "List[str]",
                ]
            ]
        }}}
        @return List[List[str]]
        """
        methods = list(_server.funcs.keys())
        methods.sort()
        return methods

    async def methodSignature(self, method, _server):
        """
        @signature {{{
            [
                [
                    "List[List[str]]", "str"
                ]
            ]
        }}}
        """
        func = _server.funcs.get(method, None)
        if not func:
            raise ServiceNotFound()
        if hasattr(func, "__signature__"):
            return getattr(func, "__signature")
        help_text = getattr(func, "__doc__", "")
        return SIGNATURES_NOT_SUPPORTED

    async def methodHelp(self, method, _server):
        """
        @signature {{{
            [
                [
                    "str", "str"
                ]
            ]
        }}}
        """
        func = _server.funcs.get(method, None)
        if not func:
            raise ServiceNotFound()
        help_text = getattr(func, "__help_text__", getattr(func, "__doc__", ""))
        return help_text


class AuthenticationService(serviceutils.ServiceBase):
    namespace = "auth"

    async def login(self, username, password, _handler, _config):
        users = _config.select("authentication.users", {})
        if not username in users:
            return False
        result = hashutils.validate_password_hash(password, users[username])
        if result:
            _handler.authenticated = True
            _handler.uid = username
            return True
        else:
            return False
