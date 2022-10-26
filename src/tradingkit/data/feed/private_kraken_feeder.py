import base64
import datetime
import hashlib
import hmac
import json
import time
import urllib

from ccxt import AuthenticationError
from tradingkit.data.feed.websocket_feeder import WebsocketFeeder
from tradingkit.pubsub.event.order import Order


class PrivateKrakenFeeder(WebsocketFeeder):

    # Converts symbols from normal to kraken vocab
    denormalized_symbol = {
        "BTC/EUR": "XBT/EUR",
        "BTC/USD": "XBT/USD",
        "BTC/USDT": "XBT/USDT",
        "ETH/BTC": "ETH/XBT",
    }

    # Converts symbols from kraken to normal vocab
    normalized_symbol = {
        "XBT/EUR": "BTC/EUR",
        "XBT/USD": "BTC/USD",
        "XBT/USDT": "BTC/USDT",
        "ETH/XBT": "ETH/BTC",
    }
    ws_errors = [
        "ping/pong timed out",
        "Connection to remote host was lost."
    ]

    def __init__(self, symbol, credentials):
        super().__init__(symbol, credentials, "wss://ws-auth.kraken.com")
        self.open_orders = {}

    def on_open(self, ws):
        token = self.get_ws_auth_token()
        ws.send(json.dumps({
            'event': 'subscribe',
            'subscription': {
                'name': 'openOrders',
                'token': token
            }
        }))

    def get_ws_auth_token(self):
        api_nonce = bytes(str(int(time.time() * 1000)), "utf-8")
        api_request = urllib.request.Request(
            "https://api.kraken.com/0/private/GetWebSocketsToken",
            b"nonce=%s" % api_nonce
        )
        api_request.add_header("API-Key", self.credentials['apiKey'])
        api_request.add_header("API-Sign", base64.b64encode(
            hmac.new(
                base64.b64decode(self.credentials['secret']),
                b"/0/private/GetWebSocketsToken" + hashlib.sha256(api_nonce + b"nonce=%s" % api_nonce).digest(),
                hashlib.sha512
            ).digest()
        ))
        resp = json.loads(urllib.request.urlopen(api_request).read())
        if 'result' in resp and 'token' in resp['result']:
            return resp['result']['token']
        else:
            raise AuthenticationError("Failed to authenticate with WebSocket: %s" % resp)

    def on_message(self, ws, message):
        data = json.loads(message)
        if "openOrders" in data:
            order_data_list = self.transform_order_data(data)
            for order_data in order_data_list:
                self.dispatch(Order(order_data))

    def transform_order_data(self, data):
        order_data_list = []
        for dict in data[0]:
            for order in dict:
                if order not in self.open_orders:
                    self.open_orders[order] = {}
                self.open_orders[order] |= dict[order]
                order_data = {
                    'id': order,
                    'timestamp': int(float(self.open_orders[order]['opentm']) * 1000),
                    'lastTradeTimestamp': int(datetime.datetime.now().timestamp() * 1000),
                    'status': self.open_orders[order]['status'],
                    'symbol': self.open_orders[order]['descr']['pair'],
                    'type': self.open_orders[order]['descr']['ordertype'],
                    'side': self.open_orders[order]['descr']['type'],
                    'amount': float(self.open_orders[order]['vol_exec']),
                    'price': float(self.open_orders[order]['avg_price']),
                    'cost': float(self.open_orders[order]['cost']),
                    'fee': float(self.open_orders[order]['fee']),
                    'exchange': 'kraken'
                }
                order_data_list.append(order_data)
                if order_data['status'] in ['closed', 'canceled']:
                    del self.open_orders[order]
        return order_data_list
