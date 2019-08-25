import asyncio
import faust
import json
import websockets

from mode import Service
from logging import LogRecord
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
    # This was cribbed from StackOverflow, it's not clear
    # how much of this I'm using.

    def __init__(self, app, bind: str = '0.0.0.0', port: int = 7799, **kwargs):
        self.app = app
        self.bind = bind
        self.port = port
        super().__init__(**kwargs)

    async def on_message(self, ws, message) -> None:
        print(message)

        # Parse JSON message
        try:
            parsed = json.loads(message)
        except ValueError as e:
            logger.exception(e)
            return

        # Check it's from the WebExtension
        message_components = parsed['_component'].split('::')
        if message_components[0] != 'WebExtension':
            logger.error('Non webextension message passed to websocket')
            return

        # Handle different types of message from WebExtension
        # These correspond with entries in Extension/firefox/logging.js
        if message_components[1] == 'Start':
            pass
        elif message_components[1] == 'Log':
            record = LogRecord(
                name='WebExtension',
                level=parsed['level'],
                msg=parsed['msg'],
                pathname='',
                lineno=1,
                args=None,
                exc_info=None,
            )
            logger.handle(record)
        elif message_components[1] == 'Data':
            pass
        elif message_components[1] == 'Content':
            pass
        else:
            logger.error('Invalid message component', message)

    async def on_messages(self, ws: WebSocketServerProtocol, path: str) -> None:
        try:
            async for message in ws:
                await self.on_message(ws, message)
        except ConnectionClosed:
            await self.on_close(ws)
        except asyncio.CancelledError:
            pass

    async def on_close(self, ws) -> None:
        # called when websocket socket is closed.
        logger.warn('Websocket closing')

    @Service.task
    async def _background_server(self):
        await websockets.serve(self.on_messages, self.bind, self.port)


app = WSApp(APPNAME, broker=BROKER)
