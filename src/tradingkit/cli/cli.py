import importlib.resources as res
import json
import logging
import os
import sys
from datetime import datetime

import ccxt
import docopt
import pkg_resources
from ccxt import Exchange
from dateutil.relativedelta import relativedelta
from setuptools import Command

from tradingkit.cli.runner import Runner
from tradingkit.data.feed.feeder import Feeder
from tradingkit.display.plotter import Plotter
from tradingkit.strategy.strategy import Strategy
from tradingkit.utils.config_injector import ConfigInjector
from tradingkit.utils.system import System
from tradingkit.data.fetch.ccxt_fetcher import CCXTFetcher


class CLI(Command):
    """Trading Kit CLI.

    Usage:
      tk run [<strategy_dir>] [-e <env>] [-y <year>] [-m <month>] [--optimize | --plot | --live_plot] [ --show-open-orders | --show-orders] [--loglevel <level>]
      tk import [-x <exchange>] [-s <symbol>] [-y <year>] [-m <month>]
      tk --help
      tk --version

    Options:
      -e, --env <env>                    Select environment [default: dev].
      -x, --exchange <exchange>          Select exchange.
      -s, --symbol <symbol>              Select the exchange symbol.
      -y, --year <year>                  Year to backtest.
      -m, --month <month>                Month to backtest.
      -o, --optimize                     Run the optimizer for the strategy.
      --plot                             Plot the results.
      --live_plot                        Plot real-time charts.
      --show-open-orders                 Show closed and open orders on chart.
      --show-orders                      Show only closed orders on chart.
      --loglevel <level>                 Sets the log level [default: error].
      -h, --help                         Show this screen.
      -v, --version                      Show version.

    """

    @staticmethod
    def main():
        sys.path.append(os.getcwd())
        version = str(pkg_resources.require("tradingkit")[0])
        args = docopt.docopt(str(CLI.__doc__), version=version)

        logging.basicConfig(level=logging.getLevelName(args['--loglevel'].upper()))

        if args['import']:
            exchange_name = args['--exchange']
            exchange_class = getattr(ccxt, exchange_name)
            exchange = exchange_class()
            symbol = args['--symbol']
            fetcher = CCXTFetcher(exchange)
            year = int(args['--year'])
            months = [int(args['--month'])] if args['--month'] else range(1, 13)
            CLI.command_import(exchange_name, symbol, fetcher, year, months)
        else:

            config = json.loads(res.read_text("tradingkit.config", "config.json"))

            strategy_dir = args['<strategy_dir>'] or '.'
            System.load_env(strategy_dir, args['--env'])

            main_conf = "%s/system/config.json" % os.path.abspath(strategy_dir)
            if os.path.exists(main_conf):
                config.update(json.load(open(main_conf, 'r')))

            env_conf = "%s/system/config.%s.json" % (os.path.abspath(strategy_dir), args['--env'])
            if os.path.exists(env_conf):
                config.update(json.load(open(env_conf, 'r')))

            if args['--year']:
                if args['--month']:
                    since = datetime.fromisoformat(
                        "%d-%02d-01T00:00:00+00:00" % (int(args['--year']), int(args['--month']))
                    )
                    to = since + relativedelta(months=1)
                else:
                    since = datetime.fromisoformat("%d-01-01T00:00:00+00:00" % int(args['--year']))
                    to = since + relativedelta(years=1)
                config['since'] = since.isoformat()
                config['to'] = to.isoformat()

            injector = ConfigInjector(config)
            feeder = injector.inject('feeder', Feeder)
            exchange = injector.inject('exchange', Exchange)
            plotter = injector.inject('plotter', Plotter)
            if args['--live_plot']:
                plotter.set_live()
            if args['--show-open-orders']:
                plotter.set_chart_type(2)
            elif args['--show-orders']:
                plotter.set_chart_type(1)
            strategy = injector.inject('strategy', Strategy)
            bridge = injector.inject('bridge', Exchange)
            feeder_adapters = injector.inject('feeder_adapters', list)

            Runner.run(feeder, exchange, plotter, strategy, bridge, feeder_adapters, args['--optimize'], args['--plot'])

    @staticmethod
    def command_import(exchange_name, symbol, fetcher, year, months):
        for month in months:
            next_period_year = year if month < 12 else (year + 1)
            next_period_month = (month + 1) if month < 12 else 1
            trades = fetcher.fetch_all(
                symbol=symbol,
                since8601="%d-%02d-01T00:00:00+00:00" % (year, month),
                to8601="%d-%02d-01T00:00:00+00:00" % (next_period_year, next_period_month)
            )
            import_dir = System.get_import_dir()
            base, quote = symbol.split('/')
            full_filename = '%s/%s-%s_%s-%d-%02d.json' % (import_dir, exchange_name, base, quote, year, month)
            json.dump(trades, open(full_filename, 'w'))
