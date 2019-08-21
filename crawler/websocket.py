import asyncio
import faust
import websockets

from mode import Service
from websockets.exceptions import ConnectionClosed
from websockets.server import WebSocketServerProtocol

from app import (
    logger,
    APPNAME,
    BROKER,
)


class WSApp(faust.App):

    def on_init(self):
        self.websockets = Websockets(self)

    async def on_start(self):
        await self.add_runtime_dependency(self.websockets)


class Websockets(Service):

    def __init__(self, app, bind: str = 'localhost', port: int = 7799, **kwargs):
        self.app = app
        self.bind = bind
        self.port = port
        super().__init__(**kwargs)

    async def on_message(self, ws, message):
        logger.info(message)

    async def on_messages(self,
                          ws: WebSocketServerProtocol,
                          path: str) -> None:
        try:
            async for message in ws:
                await self.on_message(ws, message)
        except ConnectionClosed:
            await self.on_close(ws)
        except asyncio.CancelledError:
            pass

    async def on_close(self, ws):
        # called when websocket socket is closed.
        logger.warn('Websocket closing')

    @Service.task
    async def _background_server(self):
        await websockets.serve(self.on_messages, self.bind, self.port)


app = WSApp(APPNAME, broker=BROKER)
