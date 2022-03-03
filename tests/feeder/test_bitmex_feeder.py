import time
from datetime import datetime
from unittest import TestCase
from tradingkit.data.feed.bitmex_feeder import BitmexFeeder


class TestBitmexFeeder(TestCase):

    def test_trade_data_format(self):
        trade = BitmexFeeder.transform_trade_data(BitmexFeeder, {
            'data': [{'timestamp': "2015-01-18T10:14:06.802Z",
                      'symbol': 'XBTUSD',
                      'size': 100,
                      'type': 'limit',
                      'side': 'buy',
                      'price': 1000
                      }]})

        assert type(trade['timestamp']) is float
        assert trade['symbol'] == 'BTC/USD'
        assert trade['exchange'] == 'bitmex'
        assert trade['amount'] == 100
        assert trade['cost'] == 100000

    def test_book_data_format(self):

        now = datetime.now()
        trade = BitmexFeeder.transform_book_data(BitmexFeeder, {
            'table': 'orderBook10',
            'data': [{'timestamp': "2015-01-18T10:14:06.802Z",
                      'symbol': 'XBTUSD',
                      'bids': [[100, 1]],
                      'asks': [[100, 1]]
                      }]})

        assert type(trade['timestamp']) is int
        assert trade['symbol'] == 'BTC/USD'
        assert trade['exchange'] == 'bitmex'

    def test_order_data_format(self):

        now = datetime.now()
        trade = BitmexFeeder.transform_order_data(BitmexFeeder, {
            'table': 'orderBook10',
            'data': [{'timestamp': "2015-01-18T10:14:06.802Z",
                      'symbol': 'XBTUSD',
                      'orderID': '91806686-e887fe',
                      'ordStatus': 'closed',
                      'cumQty': 100,
                      'leavesQty': 0,
                      'type': 'limit',
                      'side': 'buy',
                      'price': 1000
                      }]})

        assert type(trade['timestamp']) is int
        assert trade['symbol'] == 'BTC/USD'
        assert trade['exchange'] == 'bitmex'
        assert trade['amount'] == 100
        assert trade['id'] == '91806686-e887fe'
