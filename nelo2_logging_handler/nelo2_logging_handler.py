import asyncio
import logging
import socket
from threading import Thread

import httpx


class Nelo2Exception(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Nelo2LoggingHandler(logging.Handler):
    def __init__(self, project_name: str, project_version: str, end_point: str,
                 host: str = None, loop: asyncio.AbstractEventLoop = None,
                 timeout: int = None, level: int = logging.NOTSET, default_header: dict = None):
        super().__init__(level)
        self.project_name = project_name
        self.project_version = project_version
        self.host = host or socket.gethostname()
        self.end_point = end_point
        self.default_header = default_header
        self._client: httpx.AsyncClient = None
        self.timeout = timeout or 10

        if loop is not None:
            self.loop = loop
        else:
            self.loop = asyncio.new_event_loop()
            t = Thread(target=self.start_background_loop, args=(self.loop,), daemon=True)
            t.start()

    def start_background_loop(self, loop: asyncio.AbstractEventLoop):
        print("run start_background_loop start")
        asyncio.set_event_loop(loop)
        loop.run_forever()

        print("run start_background_loop done")

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            print("new client is created")
            self._client = httpx.AsyncClient()
            return self._client
        return self._client

    def emit(self, record):
        async def e():
            try:
                payload = {
                    'projectName': self.project_name,
                    'projectVersion': self.project_version,
                    'host': self.host,
                    'body': record.msg,
                    'logSource': record.name,
                    'logLevel': record.levelname
                }

                await asyncio.sleep(10)
                res: httpx.Response = await self.client.post(url=self.end_point, timeout=self.timeout, json=payload, )
                if res.status_code != 200:
                    raise Nelo2Exception(res)
            except (KeyboardInterrupt, SystemExit) as e:
                print(e)
                raise
            except:
                # raise
                self.handleError(record)

        asyncio.ensure_future(e(), loop=self.loop)