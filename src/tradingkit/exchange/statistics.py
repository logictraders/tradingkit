
class Statistics:

    def __init__(self):

        self.last_trade_timestamp = None
        self.max_no_trades_time = 0


    def update_trades_statistics(self, timestamp):
        if self.last_trade_timestamp is None:
            self.last_trade_timestamp = timestamp
        else:
            self.max_no_trades_time = max(self.max_no_trades_time, timestamp - self.last_trade_timestamp)
            self.last_trade_timestamp = timestamp

    def get_statistics(self):
        return {'no_trade_max_time': self.max_no_trades_time}