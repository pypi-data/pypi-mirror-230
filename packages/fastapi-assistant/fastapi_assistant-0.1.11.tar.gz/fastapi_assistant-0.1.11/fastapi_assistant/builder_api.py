import logging
import os
from typing import Union, Dict
from configparser import ConfigParser

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logging.basicConfig(format=f'%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG)

logger = logging.getLogger(__name__)

FASTAPI_SETTINGS_MODULE = 'FASTAPI_SETTINGS_MODULE'


def set_settings_module(module: str = 'settings.ini'):
    os.environ.setdefault(FASTAPI_SETTINGS_MODULE, module)


def builder_fastapi(deploy: Union[Dict, FastAPI] = None, fastapi_settings: dict = None) -> FastAPI:
    if deploy is not None:
        if isinstance(deploy, FastAPI):
            return deploy
        _app = FastAPI(**deploy)
    else:
        _app = FastAPI(**fastapi_settings) if fastapi_settings else FastAPI()
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @_app.exception_handler(RequestValidationError)
    async def handle_param_unresolved(request: Request, ex: RequestValidationError):
        """
        参数校验异常处理器
        """
        logging.warning('request body [%s]', ex.body)
        return JSONResponse(
            content={
                'msg': '参数校验失败',
                'code': -1,
                'data': ex.errors()
            },
            status_code=200
        )

    @_app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request, exc):
        return PlainTextResponse(str(exc.detail), status_code=exc.status_code)

    @_app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        return PlainTextResponse(str(exc), status_code=400)

    return _app


class BuilderSettings:

    def __init__(self, base_dir, default_setting):
        self.conf_path = os.path.join(base_dir, base_dir, default_setting)
        self.parser = ConfigParser()
        self.settings = self.mount_configuration()

    def mount_configuration(self):
        self.parser.read(self.conf_path)

        class BaseSettings:
            class Service:
                section = 'service'
                if self.parser.has_section(section):
                    app = self.parser.get(section, 'app')
                    host = self.parser.get(section, 'host')
                    port = self.parser.getint(section, 'port')

            class Fastapi:
                config = {}
                section = 'fastapi'
                if self.parser.has_section(section):
                    for option in self.parser.options(section):
                        value = self.parser.get(section, option)
                        if value in ['true', 'false']:
                            value = bool(value)
                        elif value == 'null':
                            value = None
                        config[option] = value

            if self.parser.has_section('mysql'):
                class Mysql:
                    section = 'mysql'
                    if self.parser.has_section(section):
                        username = self.parser.get(section, 'username')
                        password = self.parser.get(section, 'password')
                        host = self.parser.get(section, 'host')
                        port = self.parser.getint(section, 'port')
                        database = self.parser.get(section, 'database')
            else:
                class Sqlit:
                    path = '/sqlit.db'
                    if self.parser.has_section('sqlit') and self.parser.has_option('sqlit', 'path'):
                        path = self.parser.get('sqlit', 'path')

        class Settings(BaseSettings):
            ...

        return Settings()
