from tradingkit.exchange.testex import TestEX
from tradingkit.statistics.statistics import Statistics


class Runner:

    @staticmethod
    def run(feeder, plotter, strategy, args, feeder_adapters=None):
        bridge = strategy.exchange
        exchange = bridge.exchange

        if feeder_adapters is None:
            feeder_adapters = []

        chain = feeder
        for adapter in feeder_adapters:
            chain.register(adapter)
            chain = adapter

        bridge.register(strategy)
        if plotter is not None:
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

        result = strategy.finish()

        if args['--stats']:
            stats_result = statistics.get_statistics()
            for stat in stats_result.keys():
                result[stat] = stats_result[stat]

        if not args['--optimize']:
            print("Trading results")
            for info in result:
                print("%20s: %10.2f" % (info, result[info]))

        if plotter is not None:
            plotter.plot()

        return result
