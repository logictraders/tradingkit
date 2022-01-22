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
        # conn_key = self.ws.start_trade_socket('BTCUSDT', self.on_message)
        # conn_key0 = self.ws.start_symbol_book_ticker_socket('BTCUSDT', self.on_message)  # for fast price movments

        self.ws.start_user_socket(self.on_message)
        self.ws.start_symbol_ticker_socket(self.symbol, self.on_message)

    def on_message(self, message):
        if "e" in message:
            if message['e'] == '24hrTicker':
                order_book = {"bids": [[float(message['b']), float(message['B'])]],
                              "ascs": [[float(message['a']), float(message['A'])]],
                              "timestamp": int(message['E']),
                              "symbol": message['s']
                              }
                self.dispatch(Book(order_book))
            elif message['e'] == 'executionReport':
                if message['x'] == 'TRADE' and message['X'] == 'FILLED':
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
                    self.dispatch(Order(order_data))

    def feed(self):
        self.on_open()
        self.ws.start()
        self.ws.join()


if __name__ == '__main__':  # for testing

    # import os
    #
    # from binance.client import Client
    # from binance.websockets import BinanceSocketManager
    # from twisted.internet import reactor
    #
    #
    BINANCE_KEY = ''
    BINANCE_SECRET = ''
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
    bf = BinanceFeeder("", credentials=cred, url="")
    bf.feed()
