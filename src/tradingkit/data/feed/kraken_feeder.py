import base64
import hashlib
import hmac
import json
import sys
import os
import threading
import time
import urllib.request
from datetime import datetime

from websocket import create_connection, _logging

from tradingkit.data.feed.feeder import Feeder
from tradingkit.pubsub.core.publisher import Publisher
from tradingkit.pubsub.event.book import Book
from tradingkit.pubsub.event.candle import Candle
from tradingkit.pubsub.event.order import Order
from tradingkit.pubsub.event.trade import Trade


class KrakenFeeder(Feeder, Publisher):

    def __init__(self, credentials=None, ignore_outdated=False, pair=None):
        super().__init__()
        if pair is None:
            pair = {'symbol': 'BTC/EUR'}
        self.public_ws = None
        self.private_ws = None
        if credentials is not None:
            if ('apiKey' and 'secret') not in credentials:
                raise KeyError("credentials must contain apiKey and secret")
        self.credentials = credentials

        # Converts symbols from normal to kraken vocab
        self.denormalized_symbol = {
            "BTC/EUR": "XBT/EUR",
            "BTC/USD": "XBT/USD",
            "BTC/USDT": "XBT/USDT",
        }

        # Converts symbols from kraken to normal vocab
        self.normalized_symbol = {
            "XBT/EUR": "BTC/EUR",
            "XBT/USD": "BTC/USD",
            "XBT/USDT": "BTC/USDT",
        }
        self.symbol = self.denormalized_symbol[pair['symbol']]  # used to send requests to kraken
        self.on_open()
        self.ignore_outdated = ignore_outdated
        self.orderbooks = {}
        self.lock = None
        self.candle = {'id': '', 'data': {}}

    def authenticate(self):
        api_nonce = bytes(str(int(time.time() * 1000)), "utf-8")
        api_request = urllib.request.Request("https://api.kraken.com/0/private/GetWebSocketsToken",
                                             b"nonce=%s" % api_nonce)
        api_request.add_header("API-Key", self.credentials['apiKey'])
        api_request.add_header("API-Sign", base64.b64encode(hmac.new(base64.b64decode(self.credentials['secret']),
                                                                     b"/0/private/GetWebSocketsToken" + hashlib.sha256(
                                                                         api_nonce + b"nonce=%s" % api_nonce).digest(),
                                                                     hashlib.sha512).digest()))
        resp = json.loads(urllib.request.urlopen(api_request).read())
        if 'result' in resp and 'token' in resp['result']:
            resp = resp['result']['token']
        return resp

    def on_open(self):
        api_domain = "wss://ws.kraken.com/"
        auth_api_domain = "wss://ws-auth.kraken.com"

        try:
            self.public_ws = create_connection(api_domain)
        except Exception as error:
            _logging.warning("WebSocket connection failed (%s)" % error)
            time.sleep(600)
            self.on_open()
        try:
            self.private_ws = create_connection(auth_api_domain)
        except Exception as error:
            _logging.warning("WebSocket connection failed (%s)" % error)
            time.sleep(600)
            self.on_open()
        token = self.authenticate()
        self.subscribe(token)

    def subscribe(self, token):
        api_feed = "book"
        api_depth = 10
        book_feed = '{"event":"subscribe", "subscription":{"name":"%(feed)s", "depth":%(depth)s}, "pair":["%(symbol)s"]}' % {
            "feed": api_feed, "depth": api_depth, "symbol": self.symbol}
        trade_feed = '{"event": "subscribe", "pair": ["%(symbol)s"],  "subscription": {"name": "trade", "token": "%(token)s"}}' % {
            "symbol": self.symbol, 'token': token}
        own_trades_feed = '{"event": "subscribe", "subscription": {"name": "ownTrades","token": "%(token)s"}}' % {
            'token': token}

        try:
            self.public_ws.send(trade_feed)
            self.public_ws.send(book_feed)
            self.private_ws.send(own_trades_feed)
        except Exception as error:
            _logging.warning("Feed subscription failed (%s)" % error)
            self.public_ws.close()
            self.private_ws.close()
            sys.exit(1)

    def dispatch_event(self, event):
        self.lock.acquire()
        self.dispatch(event)
        self.lock.release()

    def on_message(self, message):
        ts = time.time()
        if "ownTrades" in message:
            for dict in message[0]:
                for order in dict:
                    if ts - float(dict[order]['time']) < 10:  # filter orders since 10 seg
                        order_data = {
                            'id': dict[order]['ordertxid'],
                            'timestamp': int(float(dict[order]['time']) * 1000),
                            'lastTradeTimestamp': int(float(dict[order]['time']) * 1000),
                            'status': 'filled',
                            'symbol': self.normalized_symbol[dict[order]['pair']],
                            'type': dict[order]['ordertype'],
                            'side': dict[order]['type'],
                            'price': float(dict[order]['price']),
                            'amount': float(dict[order]['vol'])
                        }
                        self.dispatch_event(Order(order_data))
        elif "book-10" in message:
            keys = message[1].keys()
            symbol = self.normalized_symbol[message[-1]]
            if "as" in keys:
                self.orderbooks[symbol] = {
                    "bids": [
                        [
                            float(message[1]["bs"][0][0]),
                            float(message[1]["bs"][0][1])
                        ]
                    ],
                    "asks": [
                        [
                            float(message[1]["as"][0][0]),
                            float(message[1]["as"][0][1])
                        ]
                    ],
                    "timestamp": int(float(message[1]["as"][0][2]) * 1000),
                    "symbol": symbol
                }
            else:
                if "a" in keys:
                    self.orderbooks[symbol]["asks"] = [
                        [
                            float(message[1]["a"][0][0]),
                            float(message[1]["a"][0][1])
                        ]
                    ]
                    self.orderbooks[symbol]["timestamp"] = int(float(message[1]["a"][0][2]) * 1000)
                    self.orderbooks[symbol]["symbol"] = symbol
                if "b" in keys:
                    self.orderbooks[symbol]["bids"] = [
                        [
                            float(message[1]["b"][0][0]),
                            float(message[1]["b"][0][1])
                        ]
                    ]
                    self.orderbooks[symbol]["timestamp"] = int(float(message[1]["b"][0][2]) * 1000)
                    self.orderbooks[symbol]["symbol"] = symbol
            self.dispatch_event(Book(self.orderbooks[symbol]))
        elif "trade" in message:
            symbol = self.normalized_symbol[message[-1]]
            for trade in message[1]:
                price = float(trade[0])
                amount = float(trade[1])
                cost = float(trade[0]) * float(trade[1])
                timestamp = int(float(trade[2]) * 1000)
                side = 'buy' if trade[3] == 'b' else 'sell'
                type = 'market' if trade[4] == 'm' else 'limit'
                trade_data = {
                    'price': price,
                    'amount': amount,
                    'cost': cost,
                    'timestamp': timestamp,
                    'side': side,
                    'type': type,
                    'symbol': symbol
                }
                self.dispatch_event(Trade(trade_data))

    def run(self, is_private):
        if is_private:
            _ws = self.private_ws
        else:
            _ws = self.public_ws
        while True:
            ws_data = "No Data."
            try:
                ws_data = _ws.recv()
                if ws_data:
                    message = json.loads(ws_data)
                    self.on_message(message)
            except KeyboardInterrupt:
                _ws.close()
                sys.exit(0)
            except Exception as error:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                _logging.warning(exc_type, fname, exc_tb.tb_lineno)
                _logging.warning("[WebSocket error] %s" % str(error))
                _logging.warning("[WebSocket data] %s" % str(ws_data))
                time.sleep(60)
                self.on_open()
                if is_private:
                    _ws = self.private_ws
                else:
                    _ws = self.public_ws

    def feed(self):
        # creating a lock
        self.lock = threading.Lock()

        # creating threads
        public_t = threading.Thread(target=self.run, args=(False,))
        private_t = threading.Thread(target=self.run, args=(True,))

        # start threads
        public_t.start()
        private_t.start()

        # wait until threads finish their job
        public_t.join()
        _logging.warning("[WebSocket data public STOP] %s" % str(public_t))
        private_t.join()
        _logging.warning("[WebSocket data private STOP] %s" % str(private_t))


