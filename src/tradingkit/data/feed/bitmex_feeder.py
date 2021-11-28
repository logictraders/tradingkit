import hashlib
import hmac
import inspect
import sys
import time
import json
import traceback
import logging

import ccxt
from ccxt import NetworkError
from dateutil import parser
from functools import partial

import websocket
from websocket import _logging

from tradingkit.data.feed.feeder import Feeder
from tradingkit.data.feed.websocket_feeder import WebsocketFeeder
from tradingkit.pubsub.core.publisher import Publisher
from tradingkit.pubsub.event.book import Book
from tradingkit.pubsub.event.funding import Funding
from tradingkit.pubsub.event.order import Order
from tradingkit.pubsub.event.position import Position
from tradingkit.pubsub.event.trade import Trade


class BitmexFeeder(WebsocketFeeder):

    BITMEX_SYMBOL_MAP = {
        'BTC/USD': 'XBTUSD',
        'BTC/USDT': 'XBTUSDT'
    }

    BITMEX_SYMBOL_MAP_REV = {
        'XBTUSD': 'BTC/USD',
        'XBTUSDT': 'BTC/USDT'
    }

    def __init__(self, symbol='BTC/USD', credentials=None, url="wss://ws.bitmex.com/realtime"):
        super().__init__(symbol, credentials, url)

    def on_open(self, ws):
        self.subscribe(ws, 'trade:%s' % self.BITMEX_SYMBOL_MAP[self.symbol])
        self.subscribe(ws, 'orderBook10:%s' % self.BITMEX_SYMBOL_MAP[self.symbol])
        self.subscribe(ws, 'funding:%s' % self.BITMEX_SYMBOL_MAP[self.symbol])

        if self.credentials is not None:
            self.authenticate(ws)
            self.subscribe(ws, 'order')
            self.subscribe(ws, 'position')

    def authenticate(self, ws):
        nonce = int(time.time()) + 100
        message = 'GET/realtime' + str(nonce)
        signature = hmac.new(
            self.credentials['secret'].encode('utf-8'),
            message.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()
        ws.send(json.dumps({'op': 'authKeyExpires', 'args': [self.credentials['apiKey'], nonce, signature]}))

    def subscribe(self, ws, topic):
        ws.send(json.dumps({'op': 'subscribe', 'args': topic}))

    def on_message(self, ws, message):
        payload = json.loads(message)
        if 'table' in payload:
            if payload['table'] == 'orderBook10' and payload['data']:
                order_book = self.transform_book_data(payload)
                if order_book is not None:
                    self.dispatch(Book(order_book))

            elif payload['table'] == 'trade' and payload['data']:
                trade = self.transform_trade_data(payload)
                self.dispatch(Trade(trade))

            elif payload['table'] == 'order' and payload['data']:
                if 'ordStatus' in payload['data'][0].keys() and payload['data'][0]['ordStatus'] == 'Filled':
                    order_data = self.transform_order_data(payload)
                    self.dispatch(Order(order_data))

            elif payload['table'] == 'position' and payload['data']:
                self.dispatch(Position(payload['data'][0]))

            elif payload['table'] == 'funding' and payload['data']:
                self.dispatch(Funding(payload['data'][0]))

            else:
                print("Unknown table Message:", str(payload))
        else:
            print("Unknown Message:", str(payload))

    def transform_book_data(self, payload):
        order_book = payload['data'][0]
        order_book['timestamp'] = int(parser.isoparse(payload['data'][0]['timestamp']).timestamp() * 1000)
        order_book['symbol'] = self.BITMEX_SYMBOL_MAP_REV[order_book['symbol']]

        return order_book

    def transform_trade_data(self, payload):
        trade = payload['data'][0].copy()
        trade['timestamp'] = parser.isoparse(trade['timestamp']).timestamp() * 1000
        trade['symbol'] = self.BITMEX_SYMBOL_MAP_REV[trade['symbol']]

        trade['amount'] = trade['size']
        trade['info'] = payload['data'][0].copy()
        if 'cost' not in trade.keys():
            trade['cost'] = float(trade['size']) * float(trade['price'])
        return trade

    def transform_order_data(self, payload):
        symbol = self.BITMEX_SYMBOL_MAP_REV[payload['data'][0]['symbol']]
        timestamp = int(parser.isoparse(payload['data'][0]['timestamp']).timestamp() * 1000)
        logging.debug("PAYLOAD: %s" % str(payload))

        order_payload = {
            "info": payload['data'][0].copy(),
            "id": payload['data'][0]['orderID'],
            "status": payload['data'][0]['ordStatus'].lower(),
            "amount": payload['data'][0]['cumQty'],
            "timestamp": timestamp,
            "lastTradeTimestamp": int(time.time() * 1000),
            "symbol": symbol,
            "leavesQty": payload['data'][0]['leavesQty']
        }

        # sometimes bitmex order updates doesn't have avgPx
        if 'avgPx' in payload['data'][0]:
            order_payload["price"] = payload['data'][0]['avgPx']
        return order_payload
