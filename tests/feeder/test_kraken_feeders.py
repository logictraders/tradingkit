import time
from unittest import TestCase
from tradingkit.data.feed.private_kraken_feeder import PrivateKrakenFeeder
from tradingkit.data.feed.public_kraken_feeder import PublicKrakenFeeder


class TestKrakenFeeder(TestCase):

    def test_trade_data_format(self):
        kraken_real_trade_info = [337, [['41500.00000', '0.02242183', '1639508581.231682', 'b', 'l', '']], 'trade',
                                  'XBT/EUR']

        trade = PublicKrakenFeeder.transform_trade_data(PublicKrakenFeeder, kraken_real_trade_info)[0]
        assert type(trade['timestamp']) is int
        assert trade['symbol'] == 'BTC/EUR'
        assert trade['exchange'] == 'kraken'
        assert trade['amount'] == 0.02242183
        assert trade['cost'] == 41500.00000 * 0.02242183

    def test_book_data_format(self):
        kraken_real_book_info = [336, {'as': [['41500.00000', '0.02242183', '1639508574.941128'],
                                              ['41534.30000', '0.48000000', '1639508580.019650'],
                                              ['41535.30000', '1.47200000', '1639508562.390296'],
                                              ['41541.70000', '1.64535030', '1639508577.647941'],
                                              ['41541.80000', '2.05240577', '1639508574.091468'],
                                              ['41546.40000', '5.34527366', '1639508575.298279'],
                                              ['41548.00000', '0.07328291', '1639508562.123522'],
                                              ['41549.00000', '0.10000000', '1639508579.164817'],
                                              ['41549.40000', '0.16847420', '1639508579.700554'],
                                              ['41551.50000', '1.00000000', '1639508579.759589']],
                                       'bs': [['41499.90000', '6.93907581', '1639508575.125905'],
                                              ['41499.80000', '5.34650407', '1639508571.830710'],
                                              ['41499.20000', '3.20897375', '1639508559.722239'],
                                              ['41499.00000', '0.03228285', '1639508561.055749'],
                                              ['41497.80000', '0.07043604', '1639508565.295894'],
                                              ['41497.40000', '5.34520587', '1639508574.087364'],
                                              ['41497.20000', '1.10550477', '1639508569.475841'],
                                              ['41497.10000', '0.27000000', '1639508559.589430'],
                                              ['41495.20000', '2.46382192', '1639508559.784053'],
                                              ['41494.90000', '2.55820000', '1639508566.947979']]}, 'book-10',
                                 'XBT/EUR']

        book = PublicKrakenFeeder.transform_book_data(PublicKrakenFeeder, kraken_real_book_info)

        assert type(book['timestamp']) is int
        assert book['symbol'] == 'BTC/EUR'
        assert book['exchange'] == 'kraken'
        assert book['asks'][0][0] == 41500.00000
        assert book['bids'][0][0] == 41499.90000

    def test_order_data_format(self):
        kraken_real_order_info = [
            [
                {
                    "TDLH43-DVQXD-2KHVYY": {
                        "cost": "1000000.00000",
                        "fee": "1600.00000",
                        "margin": "0.00000",
                        "ordertxid": "TDLH43-DVQXD-2KHVYY",
                        "ordertype": "limit",
                        "pair": "XBT/EUR",
                        "postxid": "OGTT3Y-C6I3P-XRI6HX",
                        "price": "100000.00000",
                        "time": time.time(),
                        "type": "sell",
                        "vol": "1000000000.00000000"
                    }
                }
            ],
            "ownTrades",
            {
                "sequence": 2948
            }
        ]
        order = PrivateKrakenFeeder.transform_order_data(PrivateKrakenFeeder, kraken_real_order_info)[0]

        assert type(order['timestamp']) is int
        assert order['symbol'] == 'BTC/EUR'
        assert order['exchange'] == 'kraken'
        assert order['amount'] == 1000000000.00000000
        assert order['price'] == 100000.00000
        assert order['id'] == 'TDLH43-DVQXD-2KHVYY'
