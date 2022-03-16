import time
from datetime import datetime
from unittest import TestCase
from tradingkit.data.feed.binance_feeder import BinanceFeeder


class TestBinanceFeeder(TestCase):

    def test_trade_data_format(self):
        binance_real_trade_info = {'e': 'trade', 'E': 1643837470377, 's': 'BTCUSD', 't': 323083023, 'p': '1000',
                                   'q': '100',
                                   'b': 2644856852, 'a': 2644857170, 'T': 1643837470376, 'm': True, 'M': True}
        trade = BinanceFeeder.transform_trade_data(BinanceFeeder, binance_real_trade_info)

        assert type(trade['timestamp']) is int
        assert trade['symbol'] == 'BTC/USD'
        assert trade['amount'] == 100
        assert trade['cost'] == 100000

    def test_book_data_format(self):
        binance_real_book_info = {'e': '24hrTicker', 'E': 1643838057881, 's': 'BTCUSD', 'p': '-0.00041700',
                                  'P': '-0.580', 'w': '0.07185453', 'x': '0.07194500', 'c': '0.07152800',
                                  'Q': '0.52210000', 'b': '0.07153300', 'B': '0.04450000', 'a': '0.07153700',
                                  'A': '4.18140000', 'o': '0.07194500', 'h': '0.07272000', 'l': '0.07086000',
                                  'v': '62233.80980000', 'q': '4471.78100430', 'O': 1643751657843, 'C': 1643838057843,
                                  'F': 322939352, 'L': 323087285, 'n': 147934}
        book = BinanceFeeder.transform_book_data(BinanceFeeder, binance_real_book_info)

        assert type(book['timestamp']) is int
        assert book['symbol'] == 'BTC/USD'
        assert book['ascs'][0][0] == 0.071537
        assert book['bids'][0][0] == 0.071533

    def test_order_data_format(self):
        binance_real_order_info = {'e': 'executionReport', 'E': 1643839428322, 's': 'BTCUSD',
                                   'c': 'electron_ef43bc70802c47f0a4ecfc5a2d7',
                                   'S': 'BUY', 'o': 'LIMIT', 'f': 'GTC', 'q': '0.00270000', 'p': '0.07200000',
                                   'P': '0.00000000',
                                   'F': '0.00000000', 'g': -1, 'C': '', 'x': 'TRADE', 'X': 'FILLED', 'r': 'NONE',
                                   'i': 2644957102,
                                   'l': '100', 'z': '0.00270000', 'L': '0.07200000', 'n': '0.00001459', 'N': 'BNB',
                                   'T': 1643839428322,
                                   't': 323098003, 'I': 5582650643, 'w': False, 'm': True, 'M': True,
                                   'O': 1643839366608, 'Z': '0.00019440',
                                   'Y': '0.00019440', 'Q': '0.00000000'}
        order = BinanceFeeder.transform_order_data(BinanceFeeder, binance_real_order_info)

        assert type(order['timestamp']) is int
        assert order['symbol'] == 'BTC/USD'
        assert order['amount'] == 100
        assert order['price'] == 0.072
        assert order['id'] == '2644957102'
