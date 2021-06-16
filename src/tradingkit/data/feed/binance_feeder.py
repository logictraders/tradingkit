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

from binance.client import Client
from binance.websockets import BinanceSocketManager
from twisted.internet import reactor


class BinanceFeeder(Feeder, Publisher):

    def __init__(self, credentials=None, ignore_outdated=True):
        super().__init__()
        self.client = None
        self.ws = None
        if credentials is not None:
            if ('apiKey' and 'secret') not in credentials:
                raise KeyError("credentials must contain apiKey and secret")
        self.credentials = credentials
        self.on_open()
        self.ignore_outdated = ignore_outdated
        self.orderbooks = {}
        self.symbol_dict = {"BTCUSD": "BTC/USD", "XBT/EUR": "BTC/EUR"}
        self.lock = None
        self.candle = {'id': '', 'data': {}}

    def on_open(self):
        client = Client(self.credentials['apiKey'], self.credentials['secret'])

        self.ws = BinanceSocketManager(client)
        #conn_key = self.ws.start_trade_socket('BTCUSDT', self.on_message)
        # conn_key0 = self.ws.start_symbol_book_ticker_socket('BTCUSDT', self.on_message)  # for fast price movments


        conn_key2 = self.ws.start_user_socket(self.on_message)
        conn_key1 = self.ws.start_symbol_ticker_socket('BTCUSDT', self.on_message)
        print()
        # self.ws.start()

        # stop websocket
        # bsm.stop_socket(conn_key)

        # properly terminate WebSocket
        # reactor.stop()


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

    def on_message(self, message):
        if "e" in message:
            if message['e'] == '24hrTicker':
                order_book = {"bids": [[float(message['b']), float(message['B'])]],
                              "ascs": [[float(message['a']), float(message['A'])]],
                              "timestamp": int(message['E']),
                              "symbol": message['s']
                              }
                self.dispatch(Book(order_book))
                print('order_book', order_book)
                print()
            elif message['e'] == 'executionReport':
                print("_message", message)
                if message['x'] == 'TRADE' and message['x'] == 'FILLED':
                    order_data = {'id': message['i'],
                                  'timestamp': message['T'],
                                  'status': 'filled',
                                  'symbol': message['s'],
                                  'type': message['o'],
                                  'side': message['S'],
                                  'price': message['L'],
                                  'amount': message['l']
                                  }
                    self.dispatch(Order(order_data))
            else:
                print("unknown_", message)
                print()
        else:
            print("unknown", message)
            print()

    def feed(self):
        self.ws.start()
        self.ws.join()
        #time.sleep(10)
        #reactor.stop()


if __name__ == '__main__':  # for testing

    # import os
    #
    # from binance.client import Client
    # from binance.websockets import BinanceSocketManager
    # from twisted.internet import reactor
    #
    #
    BINANCE_KEY = 'jAOZdHmFkAVI1Dao9Hkf1e40m2wdbsv5VHVr6l2y98DoaDD3lrtr28ffzc0up8B5'
    BINANCE_SECRET = 'c0b0wySao9aqc81zyNrtirUv9H3vTMWRGuTjKJChbovimNcTTCMXJLqWVIEKfbcz'
    #
    # # init
    # client = Client(BINANCE_KEY, BINANCE_SECRET)
    # btc_price = {'error': False}
    #
    #
    # def btc_trade_history(msg):
    #     ''' define how to process incoming WebSocket messages '''
    #     if msg['e'] != 'error':
    #         print(msg['c'])
    #         btc_price['last'] = msg['c']
    #         btc_price['bid'] = msg['b']
    #         btc_price['last'] = msg['a']
    #     else:
    #         btc_price['error'] = True
    #
    #
    # # init and start the WebSocket
    # bsm = BinanceSocketManager(client)
    # conn_key = bsm.start_symbol_ticker_socket('BTCUSDT', btc_trade_history)
    # bsm.start()

    cred = {"apiKey": BINANCE_KEY, "secret": BINANCE_SECRET}
    bf = BinanceFeeder(credentials=cred)
    bf.feed()
