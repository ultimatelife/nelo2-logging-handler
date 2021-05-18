import asyncio
import logging
import socket
from asyncio import ensure_future
from threading import Thread
from typing import Optional

import aiohttp
import requests


class Nelo2Exception(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Nelo2LoggingHandler(logging.Handler):
    def __init__(self, project_name: str, project_version: str, end_point: str,
                 host: str = None, timeout: int = None, level: int = logging.NOTSET, default_header: dict = None):
        super().__init__(level)
        self.project_name = project_name
        self.project_version = project_version
        self.host = host or socket.gethostname()
        self.end_point = end_point
        self.default_header = default_header
        self.timeout = timeout or 4
        self.session: requests.Session = requests.Session()

    def emit(self, record: logging.LogRecord) -> None:
        body = {
            'projectName': self.project_name,
            'projectVersion': self.project_version,
            'body': record.msg,
            'host': self.host,
            'logLevel': record.levelname
        }

        res = self.session.post(self.end_point, json=body, timeout=self.timeout, headers=self.default_header)
        try:
            res.raise_for_status()
        except:
            raise Nelo2Exception(res.text)


class AsyncNelo2LoggingHandler(logging.Handler):
    def __init__(self, project_name: str, project_version: str, end_point: str,
                 host: str = None, loop: asyncio.AbstractEventLoop = None,
                 timeout: int = None, level: int = logging.NOTSET, default_header: dict = None):
        super().__init__(level)
        self.project_name = project_name
        self.project_version = project_version
        self.host = host or socket.gethostname()
        self.end_point = end_point
        self.default_header = default_header
        self.timeout = timeout or 10
        self._loop: Optional[asyncio.AbstractEventLoop] = loop
        self._session: Optional[aiohttp.ClientSession] = None

    def start_daemon_loop(self, loop: asyncio.AbstractEventLoop):
        print("run start_background_loop start")
        asyncio.set_event_loop(loop)
        loop.run_forever()

        print("run start_background_loop done")

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(family=socket.AF_INET,
                                             loop=self.loop)
            self._session = aiohttp.ClientSession(connector=connector,
                                                  loop=self.loop)
        return self._session

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        if self._loop is None or self._loop.is_closed():
            self._loop = asyncio.new_event_loop()
            t = Thread(target=self.start_daemon_loop, args=(self._loop,), daemon=True)
            t.start()
        return self._loop

    def emit(self, record: logging.LogRecord):
        async def e():
            try:
                body = {
                    'projectName': self.project_name,
                    'projectVersion': self.project_version,
                    'body': f'{record.msg} {len(asyncio.all_tasks(self.loop))}',
                    'host': self.host,
                    'logLevel': record.levelname
                }

                async with self.session.post(self.end_point, json=body, headers=self.default_header,
                                             timeout=self.timeout) as resp:
                    if resp.status != 200:
                        raise Nelo2Exception()
                    try:
                        resp.raise_for_status()
                    except:
                        raise Nelo2Exception(resp)
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                self.handleError(record)

        ensure_future(e(), loop=self.loop)
