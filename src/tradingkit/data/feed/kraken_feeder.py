import base64
import hashlib
import hmac
import json
import sys
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

    def __init__(self, credentials=None, ignore_outdated=True):
        super().__init__()
        self.public_ws = None
        self.private_ws = None
        if credentials is not None:
            if ('apiKey' and 'secret') not in credentials:
                raise KeyError("credentials must contain apiKey and secret")
        self.credentials = credentials
        self.on_open()
        self.ignore_outdated = ignore_outdated
        self.orderbooks = {}
        self.symbol_dict = {"XBT/USD": "BTC/USD", "XBT/EUR": "BTC/EUR"}
        self.lock = None
        self.candle = {'id': '', 'data': {}}

    def autentificate(self):
        api_nonce = bytes(str(int(time.time() * 1000)), "utf-8")
        api_request = urllib.request.Request("https://api.kraken.com/0/private/GetWebSocketsToken",
                                             b"nonce=%s" % api_nonce)
        api_request.add_header("API-Key", self.credentials['apiKey'])
        api_request.add_header("API-Sign", base64.b64encode(hmac.new(base64.b64decode(self.credentials['secret']),
                                                                     b"/0/private/GetWebSocketsToken" + hashlib.sha256(
                                                                         api_nonce + b"nonce=%s" % api_nonce).digest(),
                                                                     hashlib.sha512).digest()))
        resp = json.loads(urllib.request.urlopen(api_request).read())['result']['token']
        return resp

    def on_open(self):
        api_domain = "wss://ws.kraken.com/"
        auth_api_domain = "wss://ws-auth.kraken.com"

        try:
            self.public_ws = create_connection(api_domain)
        except Exception as error:
            print("WebSocket connection failed (%s)" % error)
            sys.exit(1)
        try:
            self.private_ws = create_connection(auth_api_domain)
        except Exception as error:
            print("WebSocket connection failed (%s)" % error)
            sys.exit(1)
        token = self.autentificate()
        self.subscribe(token)

    def subscribe(self, token):
        api_feed = "book"
        api_symbol = 'XBT/EUR'
        api_depth = 10
        book_feed = '{"event":"subscribe", "subscription":{"name":"%(feed)s", "depth":%(depth)s}, "pair":["%(symbol)s"]}' % {
            "feed": api_feed, "depth": api_depth, "symbol": api_symbol}
        trade_feed = '{"event": "subscribe", "pair": ["%(symbol)s"],  "subscription": {"name": "trade", "token": "%(token)s"}}' % {
            "symbol": api_symbol, 'token': token}
        own_trades_feed = '{"event": "subscribe", "subscription": {"name": "ownTrades","token": "%(token)s"}}' % {
            'token': token}

        try:
            self.public_ws.send(book_feed)
            self.public_ws.send(trade_feed)
            self.private_ws.send(own_trades_feed)
        except Exception as error:
            print("Feed subscription failed (%s)" % error)
            self.public_ws.close()
            self.private_ws.close()
            sys.exit(1)

    def candle_dispatcher(self, trade):
        id = trade['timestamp'] // 60000 * 60
        id = str(datetime.fromtimestamp(id))
        if id == self.candle['id']:
            self.candle['data']['high'] = max(self.candle['data']['high'], trade['price'])
            self.candle['data']['low'] = min(self.candle['data']['low'], trade['price'])
            self.candle['data']['close'] = trade['price']
            self.candle['data']['vol'] += trade['amount']
            self.candle['data']['cost'] += trade['cost']
            self.candle['data']['trades'] += 1
        else:
            if self.candle['id'] != '':
                self.dispatch_event(Candle(self.candle['data']))
            self.candle['id'] = id
            self.candle['data'] = {'datetime': id,
                                   'open': trade['price'],
                                   'high': trade['price'],
                                   'low': trade['price'],
                                   'close': trade['price'],
                                   'vol': trade['amount'],
                                   'cost': trade['cost'],
                                   'trades': 1
                                   }

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
                        order_data = {'id': dict[order]['ordertxid'],
                                      'timestamp': int(float(dict[order]['time']) * 1000),
                                      'lastTradeTimestamp': int(float(dict[order]['time']) * 1000),
                                      'status': 'filled',
                                      'symbol': self.symbol_dict[dict[order]['pair']],
                                      'type': dict[order]['ordertype'],
                                      'side': dict[order]['type'],
                                      'price': float(dict[order]['price']),
                                      'amount': float(dict[order]['vol'])
                                      }
                        self.dispatch_event(Order(order_data))
        elif "book-10" in message:
            keys = message[1].keys()
            if "as" in keys:
                self.orderbooks[self.symbol_dict[message[-1]]] = {"bids": [[float(message[1]["bs"][0][0]),
                                                                           float(message[1]["bs"][0][1])]],
                                                                  "ascs": [[float(message[1]["as"][0][0]),
                                                                           float(message[1]["as"][0][1])]],
                                                                  "timestamp": int(
                                                                      float(message[1]["as"][0][2]) * 1000),
                                                                  "symbol": self.symbol_dict[message[-1]]}
            else:
                if "a" in keys:
                    self.orderbooks[self.symbol_dict[message[-1]]]["ascs"] = [[float(message[1]["a"][0][0]),
                                                                              float(message[1]["a"][0][1])]]
                    self.orderbooks[self.symbol_dict[message[-1]]]["timestamp"] = int(
                        float(message[1]["a"][0][2]) * 1000)
                    self.orderbooks[self.symbol_dict[message[-1]]]["symbol"] = self.symbol_dict[message[-1]]
                if "b" in keys:
                    self.orderbooks[self.symbol_dict[message[-1]]]["bids"] = [[float(message[1]["b"][0][0]),
                                                                              float(message[1]["b"][0][1])]]
                    self.orderbooks[self.symbol_dict[message[-1]]]["timestamp"] = int(
                        float(message[1]["b"][0][2]) * 1000)
                    self.orderbooks[self.symbol_dict[message[-1]]]["symbol"] = self.symbol_dict[message[-1]]
            self.dispatch_event(Book(self.orderbooks[self.symbol_dict[message[-1]]]))
        elif "trade" in message:
            for trade in message[1]:
                price = float(trade[0])
                amount = float(trade[1])
                cost = float(trade[0]) * float(trade[1])
                timestamp = int(float(trade[2]) * 1000)
                side = 'buy' if trade[3] == 'b' else 'sell'
                type = 'market' if trade[4] == 'm' else 'limit'
                symbol = self.symbol_dict[message[-1]]
                trade_data = {'price': price,
                              'amount': amount,
                              'cost': cost,
                              'timestamp': timestamp,
                              'side': side,
                              'type': type,
                              'symbol': symbol
                              }
                self.candle_dispatcher(trade_data)
                self.dispatch_event(Trade(trade_data))

    def run(self, is_private):
        if is_private:
            _ws = self.private_ws
        else:
            _ws = self.public_ws
        while True:
            try:
                ws_data = _ws.recv()
            except KeyboardInterrupt:
                _ws.close()
                sys.exit(0)
            except Exception as error:
                _logging.info("[WebSocket error] %s" % str(error))
                #_ws.close()
                #sys.exit(1)
            message = json.loads(ws_data)
            self.on_message(message)

    def feed(self):
        # creating a lock
        self.lock = threading.Lock()

        # creating threads
        public_t = threading.Thread(target=self.run, args=(False,))
        private_t = threading.Thread(target=self.run, args=(True,))

        # start threads
        public_t.start()
        private_t.start()

        # # wait until threads finish their job
        public_t.join()
        private_t.join()


if __name__ == '__main__':  # for testing

    try:
        with open("../../../../ws_test/kkey.json") as json_file:
            data = json.load(json_file)
    except Exception as e:
        print("No keys file to load!!!")
        print(e)
    cred = {"apiKey": data['apiKey'], "secret": data['secret']}
    kf = KrakenFeeder(credentials=cred)
    kf.feed()
