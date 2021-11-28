import inspect
import sys
import traceback
import logging
from abc import ABC, abstractmethod

from functools import partial

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
            on_message=partial(self.on_message, self),
            on_open=partial(self.on_open, self),
            on_error=partial(self.on_error, self),
            on_close=partial(self.on_close, self),
        )
        ws._callback = partial(self.monkey_callback, ws)
        ws.run_forever(ping_interval=15, ping_timeout=10)

    def monkey_callback(self, callback, *args):
        """
        Monkey patch for WebSocketApp._callback() because it swallows exceptions.
        Inspired from https://github.com/websocket-client/websocket-client/issues/377#issuecomment-397429682
        """
        if callback:
            try:
                if inspect.ismethod(callback):
                    callback(*args)
                else:
                    callback(self, *args)

            except Exception as e:
                logging.error("error from callback {}: {}".format(callback, e))
                _, _, tb = sys.exc_info()
                traceback.print_tb(tb)
                self.keep_running = False
                raise e
