import hmac
import json
import logging
import time

from dateutil import parser

from tradingkit.data.feed.websocket_feeder import WebsocketFeeder
from tradingkit.pubsub.event.book import Book
from tradingkit.pubsub.event.order import Order
from tradingkit.pubsub.event.trade import Trade


class FtxFeeder(WebsocketFeeder):

    FTX_SYMBOL_MAP = {
        'BTC/USD': 'BTC/USD',
        'BTC/USDT': 'BTC/USDT'
    }

    FTX_SYMBOL_MAP_REV = {
        'BTC/USD': 'BTC/USD',
        'BTC/USDT': 'BTC/USDT'
    }

    orderbooks = {}

    def __init__(self, symbol='BTC/USD', credentials=None, url='wss://ftx.com/ws/'):
        super().__init__(symbol, credentials, url)

    def on_open(self, ws):
        self.subscribe(ws, 'trades', self.FTX_SYMBOL_MAP[self.symbol])
        self.subscribe(ws, 'orderbook', self.FTX_SYMBOL_MAP[self.symbol])

        if self.credentials is not None:
            self.authenticate(ws)
            self.subscribe(ws, 'orders', self.FTX_SYMBOL_MAP[self.symbol])

    def authenticate(self, ws):
        nonce = int(time.time() * 1000)

        sign = hmac.new(self.credentials['secret'].encode(), f'{nonce}websocket_login'.encode(), 'sha256').hexdigest()
        ws.send(json.dumps({'op': 'login', 'args': {'key': self.credentials['apiKey'], 'sign': sign, 'time': nonce}}))

    def subscribe(self, ws, channel, market):
        ws.send(json.dumps({'op': 'subscribe', 'channel': channel, 'market': market}))

    def on_message(self, ws, message):
        payload = json.loads(message)
        if payload['channel'] == 'trades' and payload['type'] == 'update':
            trade_data_list = self.transform_trade_data(payload)
            for trade_data in trade_data_list:
                self.dispatch(Trade(trade_data))

        elif payload['channel'] == 'orderbook' and payload['type'] == 'update':
            order_book = self.transform_book_data(payload)
            if order_book is not None:
                self.dispatch(Book(order_book))

        elif payload['channel'] == 'orders' and payload['type'] == 'update':
            if payload['data']['status'] == 'closed' and payload['data']['filledSize'] > 0:

                order = self.transform_order_data(payload)
                if order is not None:
                    self.dispatch(Order(order))

    def transform_book_data(self, payload):
        symbol = self.FTX_SYMBOL_MAP[payload['market']]
        if symbol not in self.orderbooks:
            self.orderbooks[symbol] = {'asks': [], 'bids': []}
        order_book = payload['data']
        order_book['timestamp'] = payload['data']['time'] * 1000
        order_book['symbol'] = symbol
        order_book['exchange'] = 'ftx'
        if order_book['asks'] != []:
            self.orderbooks[symbol]["asks"] = order_book['asks']
        else:
            order_book['asks'] = self.orderbooks[symbol]["asks"]
        if order_book['bids'] != []:
            self.orderbooks[symbol]["bids"] = order_book['bids']
        else:
            order_book['bids'] = self.orderbooks[symbol]["bids"]

        if order_book["asks"] != [] and order_book["bids"] != []:
            return order_book

    def transform_trade_data(self, payload):
        trade_data_list = []
        symbol = self.FTX_SYMBOL_MAP[payload['market']]
        for trade in payload['data']:
            trade['timestamp'] = float(parser.isoparse(trade['time']).timestamp() * 1000)
            trade['amount'] = trade['size']
            trade['cost'] = trade['size'] * trade['price']
            trade['symbol'] = symbol
            trade['exchange'] = 'ftx'
            trade_data_list.append(trade)
        return trade_data_list

    def transform_order_data(self, payload):
        symbol = self.FTX_SYMBOL_MAP_REV[payload['data']['market']]

        timestamp = int(parser.isoparse(payload['data']['createdAt']).timestamp() * 1000)
        logging.debug("PAYLOAD: %s" % str(payload))
        order_payload = payload['data']
        order_payload['timestamp'] = timestamp
        order_payload['lastTradeTimestamp'] = int(time.time() * 1000)
        order_payload['symbol'] = symbol
        order_payload['amount'] = payload['data']['size']
        order_payload['id'] = str(payload['data']['id'])
        order_payload['exchange'] = 'ftx'

        if 'avgFillPrice' in payload['data']:
            order_payload["price"] = payload['data']['avgFillPrice']
        return order_payload


if __name__ == "__main__":

    # TODO remove call data
    feeder = FtxFeeder('BTC/USD')
    feeder.feed()