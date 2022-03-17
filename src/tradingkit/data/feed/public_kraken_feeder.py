import json
from tradingkit.data.feed.websocket_feeder import WebsocketFeeder
from tradingkit.pubsub.event.book import Book
from tradingkit.pubsub.event.trade import Trade


class PublicKrakenFeeder(WebsocketFeeder):

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

    orderbooks = {}

    def __init__(self, symbol):
        super().__init__(symbol, None, "wss://ws.kraken.com")

    def on_open(self, ws):
        ws.send(json.dumps({
            'event': 'subscribe',
            'subscription': {'name': 'trade'},
            'pair': [self.denormalized_symbol[self.symbol]]
        }))
        ws.send(json.dumps({
            'event': 'subscribe',
            'subscription': {'name': 'book'},
            'pair': [self.denormalized_symbol[self.symbol]]
        }))

    def on_message(self, ws, message):
        data = json.loads(message)
        if "trade" in data:
            trade_data_list = self.transform_trade_data(message)
            for trade_data in trade_data_list:
                self.dispatch(Trade(trade_data))

        elif "book-10" in data:
            order_book = self.transform_book_data(message)
            self.dispatch(Book(order_book))

    def transform_book_data(self, data):
        keys = data[1].keys()
        symbol = self.normalized_symbol[data[-1]]
        if "as" in keys:
            self.orderbooks[symbol] = {
                "bids": [
                    [
                        float(data[1]["bs"][0][0]),
                        float(data[1]["bs"][0][1])
                    ]
                ],
                "asks": [
                    [
                        float(data[1]["as"][0][0]),
                        float(data[1]["as"][0][1])
                    ]
                ],
                "timestamp": int(float(data[1]["as"][0][2]) * 1000),
                "symbol": symbol,
                'exchange': 'kraken'
            }
        else:
            if "a" in keys:
                self.orderbooks[symbol]["asks"] = [
                    [
                        float(data[1]["a"][0][0]),
                        float(data[1]["a"][0][1])
                    ]
                ]
                self.orderbooks[symbol]["timestamp"] = int(float(data[1]["a"][0][2]) * 1000)
                self.orderbooks[symbol]["symbol"] = symbol
                self.orderbooks[symbol]["exchange"] = 'kraken'
            if "b" in keys:
                self.orderbooks[symbol]["bids"] = [
                    [
                        float(data[1]["b"][0][0]),
                        float(data[1]["b"][0][1])
                    ]
                ]
                self.orderbooks[symbol]["timestamp"] = int(float(data[1]["b"][0][2]) * 1000)
                self.orderbooks[symbol]["symbol"] = symbol
                self.orderbooks[symbol]["exchange"] = 'kraken'
        return self.orderbooks[symbol]

    def transform_trade_data(self, data):
        trade_data_list = []
        symbol = self.normalized_symbol[data[-1]]
        for trade in data[1]:
            price = float(trade[0])
            amount = float(trade[1])
            cost = float(trade[0]) * float(trade[1])
            timestamp = int(float(trade[2]) * 1000)
            side = 'buy' if trade[3] == 'b' else 'sell'
            type = 'market' if trade[4] == 'm' else 'limit'
            trade_data = {
                'price': price,
                'amount': amount,
                'cost': cost,
                'timestamp': timestamp,
                'side': side,
                'type': type,
                'symbol': symbol,
                'exchange': 'kraken'
            }
            trade_data_list.append(trade_data)
        return trade_data_list

    def on_error(self, ws, error):
        print("public ws error", error)
        self.feed()

    def on_close(self, ws):
        print("public ws closed")
        self.feed()