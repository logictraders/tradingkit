import logging

from tradingkit.data.feed.websocket_feeder import WebsocketFeeder
from tradingkit.pubsub.event.book import Book
from tradingkit.pubsub.event.order import Order
from tradingkit.pubsub.event.trade import Trade

from binance.client import Client
from binance.websockets import BinanceSocketManager


class BinanceFeeder(WebsocketFeeder):

    denormalized_symbol = {
        'BTC/USDT': 'BTCUSDT',
        'ETH/USDT': 'ETHUSDT',
        'ETH/BTC': 'ETHBTC',
    }

    normalized_symbol = {
        'BTCUSDT': 'BTC/USDT',
        'ETHUSDT': 'ETH/USDT',
        'ETHBTC': 'ETH/BTC',
    }

    def __init__(self, symbol, credentials, url):
        super().__init__(symbol, credentials, url)
        self.ws = None
        if credentials is not None:
            if ('apiKey' and 'secret') not in credentials:
                raise KeyError("credentials must contain apiKey and secret")
        self.credentials = credentials
        self.symbol = self.denormalized_symbol[symbol]


    def on_open(self):
        client = Client(self.credentials['apiKey'], self.credentials['secret'])
        self.ws = BinanceSocketManager(client)

        self.ws.start_user_socket(self.on_message)
        self.ws.start_symbol_ticker_socket(self.symbol, self.on_message)
        self.ws.start_trade_socket(self.symbol, self.on_message)

    def on_message(self, message):
        if "e" in message:
            if message['e'] == '24hrTicker':
                order_book = self.transform_book_data(message)
                self.dispatch(Book(order_book))

            elif message['e'] == 'executionReport':
                if message['x'] == 'TRADE' and message['X'] == 'FILLED':
                    order_data = self.transform_order_data(message)
                    self.dispatch(Order(order_data))

            elif message['e'] == 'trade':
                trade_data = self.transform_trade_data(message)
                self.dispatch(Trade(trade_data))

    def transform_book_data(self, message):
        order_book = {"bids": [[float(message['b']), float(message['B'])]],
                      "ascs": [[float(message['a']), float(message['A'])]],
                      "timestamp": int(message['E']),
                      "symbol": message['s']
                      }
        return order_book

    def transform_order_data(self, message):
        order_data = {'id': str(message['i']),
                      'timestamp': message['O'],
                      'lastTradeTimestamp': message['E'],
                      'status': 'filled',
                      'symbol': message['s'],
                      'type': message['o'],
                      'side': message['S'],
                      'price': float(message['L']),
                      'amount': float(message['l'])
                      }
        return order_data

    def transform_trade_data(self, message):
        side = 'sell' if message['m'] else 'buy'
        trade_data = {
            'price': float(message['p']),
            'amount': float(message['q']),
            'cost': float(message['q']) * float(message['p']),
            'timestamp': int(message['E'] / 1000),
            'side': side,
            'type': 'limit',
            'symbol': self.normalized_symbol[message['s']]
        }
        return trade_data

    def feed(self):
        self.on_open()
        self.ws.start()
        self.ws.join()

