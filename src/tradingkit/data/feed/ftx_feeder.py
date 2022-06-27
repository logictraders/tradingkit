import hmac
import json
import logging
import time

from dateutil import parser

from tradingkit.data.feed.websocket_feeder import WebsocketFeeder
from tradingkit.pubsub.event.book import Book
from tradingkit.pubsub.event.trade import Trade


class FtxFeeder(WebsocketFeeder):

    FTX_SYMBOL_MAP = {
        'BTC/USD': 'BTC/USD',
        'BTC/USDT': 'XBTUSDT'
    }

    FTX_SYMBOL_MAP_REV = {
        'BTC/USD': 'BTC/USD',
        'XBTUSDT': 'BTC/USDT'
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
        print(payload)
        if payload['channel'] == 'trades' and payload['type'] == 'update':
            trade_data_list = self.transform_trade_data(payload)
            for trade_data in trade_data_list:
                self.dispatch(Trade(trade_data))

        elif payload['channel'] == 'orderbook' and payload['type'] == 'update':
            order_book = self.transform_book_data(payload)
            if order_book is not None:
                self.dispatch(Book(order_book))



        # if 'table' in payload:
        #     if payload['table'] == 'orderBook10' and payload['data']:
        #         order_book = self.transform_book_data(payload)
        #         if order_book is not None:
        #             self.dispatch(Book(order_book))
        #
        #     elif payload['table'] == 'trade' and payload['data']:
        #         trade = self.transform_trade_data(payload)
        #         self.dispatch(Trade(trade))
        #
        #     elif payload['table'] == 'order' and payload['data']:
        #         if 'ordStatus' in payload['data'][0].keys() and payload['data'][0]['ordStatus'] == 'Filled':
        #             order_data = self.transform_order_data(payload)
        #             self.dispatch(Order(order_data))
        #
        #     elif payload['table'] == 'position' and payload['data']:
        #         self.dispatch(Position(payload['data'][0]))
        #
        #     elif payload['table'] == 'funding' and payload['data']:
        #         self.dispatch(Funding(payload['data'][0]))
        #
        #     else:
        #         print("Unknown table Message:", str(payload))
        # else:
        #     print("Unknown Message:", str(payload))


    def transform_book_data(self, payload):
        symbol = self.FTX_SYMBOL_MAP[payload['market']]
        if symbol not in self.orderbooks:
            self.orderbooks[symbol] = {'asks': [], 'bids': []}
        order_book = payload['data']
        order_book['timestamp'] = payload['data']['time'] * 1000
        order_book['symbol'] = symbol
        order_book['exchange'] = 'ftx'
        if order_book['asks']:
            self.orderbooks[symbol]["asks"] = order_book['asks']
        if order_book['bids']:
            self.orderbooks[symbol]["bids"] = order_book['bids']

        if self.orderbooks[symbol]["asks"] and self.orderbooks[symbol]["bids"]:
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
        symbol = self.FTX_SYMBOL_MAP_REV[payload['data'][0]['symbol']]
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
            "exchange": 'bitmex',
            "leavesQty": payload['data'][0]['leavesQty']
        }

        # sometimes bitmex order updates doesn't have avgPx
        if 'avgPx' in payload['data'][0]:
            order_payload["price"] = payload['data'][0]['avgPx']
        return order_payload


if __name__ == "__main__":
    # feeder = FtxFeeder('BTC/USD', {"apiKey": "TGVaMGH17VpBjYUZDlK95YhT",
    #                                   "secret": "FcJjiG4_5ewBiNr7u9NdlBkWOfaOg_TWKRyFWDtA15t0EAe-"},
    #                       "wss://ws.testnet.bitmex.com/realtime")

    feeder = FtxFeeder('BTC/USD',{"apiKey": "kQR-6MzXpL6I7lz360JWBoHG3Y8Z8clEjevZKZnq",
                                       "secret": "uyJlJRCZLZLUOCZkxE0m1UUlTBcJ7ijZW6OWrNqI"})
    feeder.feed()