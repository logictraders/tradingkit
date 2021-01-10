from tradingkit.exchange.testex import TestEX


class Runner:

    @staticmethod
    def run(feeder, exchange, plotter, strategy, bridge, feeder_adapters=None, optimize=False, plot=False):
        if feeder_adapters is None:
            feeder_adapters = []

        chain = feeder
        for adapter in feeder_adapters:
            chain.register(adapter)
            chain = adapter

        bridge.register(strategy)
        bridge.register(plotter)
        strategy.register(plotter)

        if isinstance(exchange, TestEX):
            chain.register(exchange)
            chain = exchange
        chain.register(bridge)
        feeder.feed()
        if optimize:
            result = strategy.finish(False)
        else:
            result = strategy.finish()
            print("Trading results")
            for info in result:
                print("%15s: %10.2f" % (info, result[info]))

        if plot:
            plotter.plot()

        return result
