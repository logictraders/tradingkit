import logging
from abc import ABC, abstractmethod
import websocket

from tradingkit.data.feed.feeder import Feeder
from tradingkit.pubsub.core.publisher import Publisher


class WebsocketFeeder(Feeder, Publisher, ABC):

    def __init__(self, symbol, credentials, url):
        super().__init__()
        self.symbol = symbol
        if credentials is not None and ('apiKey' and 'secret') not in credentials:
            raise KeyError("credentials must contain apiKey and secret")
        self.credentials = credentials
        self.url = url
        self.keep_running = True

    @abstractmethod
    def on_open(self, ws):
        pass

    @abstractmethod
    def on_message(self, ws, message):
        pass

    def on_error(self, ws, error):
        logging.info("[Websocket error] %s" % str(error))
        raise error

    def on_close(self, ws):
        logging.info("WebSocket closed")

    def feed(self):
        ws = websocket.WebSocketApp(
            url=self.url,
            on_message=self.on_message,
            on_open=self.on_open,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        ws.run_forever(ping_interval=15, ping_timeout=10)

