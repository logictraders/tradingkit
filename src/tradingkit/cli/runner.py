from tradingkit.exchange.testex import TestEX
from tradingkit.statistics.statistics import Statistics


class Runner:

    @staticmethod
    def run(feeder, exchange, plotter, strategy, bridge, args, feeder_adapters=None, plot=False):
        if feeder_adapters is None:
            feeder_adapters = []

        chain = feeder
        for adapter in feeder_adapters:
            chain.register(adapter)
            chain = adapter

        bridge.register(strategy)
        if plot:
            bridge.register(plotter)
            strategy.register(plotter)

        if args['--stats']:
            statistics = Statistics()
            bridge.register(statistics)

        if isinstance(exchange, TestEX):
            chain.register(exchange)
            chain = exchange
        chain.register(bridge)
        feeder.feed()
        if args['--optimize']:
            result = strategy.finish(False)
        else:
            result = strategy.finish()
            print("Trading results")
            for info in result:
                print("%15s: %10.2f" % (info, result[info]))

        if plot:
            plotter.plot()

        if args['--stats']:
            stats_result = statistics.get_statistics()

        return result
