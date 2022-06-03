from tradingkit.exchange.testex import TestEX
from tradingkit.exchange.bitmex_backtest import BitmexBacktest
from tradingkit.statistics.statistics import Statistics
from tradingkit.data.adapter.feeders_syncronizer import FeedersSycronizer
import threading


class Runner:

    @staticmethod
    def run(exchange_chains, plotter, strategy, args, feeder_adapters=[]):

        if len(exchange_chains) == 1:
            feeder = exchange_chains[0]['feeder']
            exchange = exchange_chains[0]['exchange']
            bridge = exchange_chains[0]['bridge']

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

        else:  # multi exchange
            # creating a lock
            lock = threading.Lock()
            feeders_synchronizer = FeedersSycronizer(lock)
            feeders = []
            exchanges = {}
            for exchange_chain in exchange_chains:
                feeder = exchange_chain['feeder']
                exchange = exchange_chain['exchange']
                bridge = exchange_chain['bridge']

                chain = feeder
                chain.register(feeders_synchronizer)
                chain = feeders_synchronizer
                if isinstance(exchange, TestEX) or isinstance(exchange, BitmexBacktest):
                    feeders_synchronizer.add_feeder(exchange_chain['name'])
                    chain.register(exchange)
                    chain = exchange
                chain.register(bridge)
                bridge.register(strategy)

                feeders.append(feeder)
                exchanges[exchange_chain['name']] = bridge

            strategy.set_exchanges(exchanges)

            children = []
            for feeder in feeders:
                child = threading.Thread(target=feeder.feed)
                child.start()
                children.append(child)

            for child in children:
                child.join()

            result = strategy.finish()
            if not args['--optimize']:
                print("Trading results")
                for info in result:
                    print("%20s: %10.2f" % (info, result[info]))

        return result
