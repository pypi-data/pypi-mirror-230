import logging
import types
from copy import copy

from .request import BaseRequest
from .response import Response
from .exceptions import MiddlewareShortCircuit

default_cors_headers = {
    "Access-Control-Allow-Headers": "Content-Type, X-Amz-Date, Authorization,X-Api-Key,X-Amz-Security-Token",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Max-Age": 600,
    "Content-Type": "application/json"
}


class Api:
    def __init__(self, name="SAM-API", cors_headers=None, cors_function=None):
        self.cors_headers = cors_headers if cors_headers is not None and isinstance(cors_headers, dict) else default_cors_headers
        self.cors_function = cors_function if cors_function is not None and isinstance(cors_function, types.FunctionType) else self._process_options_request
        self.name = name
        self._resources = {}
        self._middlewares = []
        self._debug = False
        self.log = self._config_logging()

    def route(self, path: str, methods: list):

        def inner_register(function):
            # Create defult OPTIONS handler
            self._resources["options"] = self.cors_function

            # Default route
            if path == '$default':
                self._resources['$default'] = function
            else:
                for method in methods:
                    self._register_route(path=path, method=method, func=function)
        return inner_register

    def middleware(self):
        def inner_register(function):
            self._register_middleware(function)
        return inner_register

    def _register_route(self, path, method, func):
        route_key = f"{method} {path}"
        if route_key in self._resources.keys() and method != "OPTIONS":
            self.log.warning(f"Path '{route_key}'  already registered and will be replaced by last function")
        self._resources[route_key] = func

    def _register_middleware(self, func):
        self._middlewares.append(func)

    def _process_middlewares(self, request):
        req = copy(request)
        for midd in self._middlewares:
            rslt = midd(req)
            if isinstance(rslt, BaseRequest):
                req = copy(rslt)
            if isinstance(rslt, Response):
                raise MiddlewareShortCircuit(response=rslt.to_dict())
        return req

    def _process_options_request(self, request):
        return Response(
            code=200,
            headers=self.cors_headers
        )

    def _config_logging(self):
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.DEBUG if self._debug else logging.INFO)
        ch = logging.StreamHandler()
        formatter = logging.Formatter("%(name)s::[%(levelname)s]: %(message)s")
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        logger.propagate = 0
        return logger

    @property
    def debug(self):
        return self._debug

    @debug.setter
    def debug(self, value: bool):
        self._debug = value
        self.log.setLevel(logging.DEBUG if self._debug else logging.INFO)
