from datetime import datetime
from unittest import TestCase
from tradingkit.data.feed.ftx_feeder import FtxFeeder


class TestFtxFeeder(TestCase):

    def test_trade_data_format(self):
        trade = FtxFeeder.transform_trade_data(FtxFeeder, {'channel': 'trades', 'market': 'BTC/USD', 'type': 'update',
                                                           'data': [
                                                               {'id': 4293455527,
                                                                'price': 21303.0,
                                                                'size': 0.0394,
                                                                'side': 'sell',
                                                                'liquidation': False,
                                                                'time': '2022-06-16T12:40:34.281373+00:00'
                                                                },
                                                               {'id': 4293455528,
                                                                'price': 21303.0,
                                                                'size': 0.0001,
                                                                'side': 'sell',
                                                                'liquidation': False,
                                                                'time': '2022-06-16T12:40:34.281373+00:00'
                                                                }]})[0]

        assert type(trade['timestamp']) is float
        assert trade['symbol'] == 'BTC/USD'
        assert trade['exchange'] == 'ftx'
        assert trade['amount'] == 0.0394
        assert trade['price'] == 21303.0
        assert trade['cost'] == 0.0394 * 21303.0

    def test_book_data_format(self):
        book = FtxFeeder.transform_book_data(FtxFeeder, {'channel': 'orderbook', 'market': 'BTC/USD', 'type': 'update',
                                                          'data': {
                                                              'time': 1655385027.0440745,
                                                              'checksum': 3457867067,
                                                              'bids': [[21204.0, 3.2698]],
                                                              'asks': [[21218.0, 1.1374], [21228.0, 2.9024], [21265.0, 0.0419]],
                                                              'action': 'update'}})

        assert type(book['timestamp']) is float
        assert book['symbol'] == 'BTC/USD'
        assert book['exchange'] == 'ftx'
        assert book['asks'][0][0] == 21218.0
        assert book['bids'][0][0] == 21204.0

    def test_order_data_format(self):

        now = datetime.now()
        trade = FtxFeeder.transform_order_data(FtxFeeder, {
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
