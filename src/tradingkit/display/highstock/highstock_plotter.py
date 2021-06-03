import logging
import os
import shutil
import random
from datetime import datetime
import json

from tradingkit.display.highstock.server.plot_server import PlotServer
from tradingkit.display.plotter import Plotter
from tradingkit.pubsub.core.event import Event
from tradingkit.pubsub.event.plot import Plot
from tradingkit.utils.system import System
from tradingkit.utils.web_server import WebServer

import asyncio
import websockets
import time
import multiprocessing


class HighstockPlotter(Plotter):

    def __init__(self, live_plot=False):
        self.price = []
        self.orders = []
        self.balance = {"quote": 0,
                        "base": 0,
                        "position_vol": 0,
                        "quote_balance": 0,
                        "base_balance": 0,
                        "position_price": 0,
                        "invested": 0}
        self.series = {
            'OHLC': {'name': 'OHLC', 'type': 'candlestick', 'tooltip': 'OHLC', 'data': []},
            'volume': {'name': 'Volume', 'type': 'line', 'tooltip': '', 'data': []},
            'position': {'name': 'Position', 'type': 'line', 'tooltip': '', 'data': []},
            'position_price': {'name': 'Position Price', 'type': 'area', 'tooltip': '', 'data': []},
            'liq_price': {'name': 'Liquidation Price', 'type': 'line', 'tooltip': '', 'data': []},
            'equity': {'name': 'Equity', 'type': 'area', 'tooltip': '', 'data': []},
            'base_equity': {'name': 'Base Equity', 'type': 'area', 'tooltip': '', 'data': []},
            'quote_balance': {'name': 'Quote Balance', 'type': 'line', 'tooltip': '', 'data': []},
            'base_balance': {'name': 'Base Balance', 'type': 'line', 'tooltip': '', 'data': []},
            'hold': {'name': 'Hold', 'type': 'area', 'tooltip': '', 'data': []},
            'buy': {'name': 'Buy', 'type': 'scatter', 'tooltip': '', 'data': []},
            'open_buy': {'name': 'Buy', 'type': 'scatter', 'tooltip': '', 'data': []},
            'cancel_buy': {'name': 'Buy', 'type': 'scatter', 'tooltip': '', 'data': []},
            'sell': {'name': 'Sell', 'type': 'scatter', 'tooltip': '', 'data': []},
            'open_sell': {'name': 'Sell', 'type': 'scatter', 'tooltip': '', 'data': []},
            'cancel_sell': {'name': 'Sell', 'type': 'scatter', 'tooltip': '', 'data': []},
            'buy_series': {'name': 'OpenBuy', 'type': 'line', 'tooltip': '', 'data': [], 'series': [[]]},
            'sell_series': {'name': 'OpenSell', 'type': 'line', 'tooltip': '', 'data': [], 'series': [[]]},
            'assets': None
        }
        self.live_plot = live_plot
        if live_plot:
            self.set_live()
        self.initial_base_balance = 0
        self.chart_port = 6789
        self.balance_port = 6788
        self.chart_type = 0

    def set_chart_type(self, type):
        self.chart_type = type

    def set_live(self):
        self.live_plot = True
        chart_ps = PlotServer(self.chart_port)
        balance_ps = PlotServer(self.balance_port)
        chart_process = multiprocessing.Process(target=chart_ps.run)
        balance_process = multiprocessing.Process(target=balance_ps.run)
        chart_process.start()
        logging.info("Chart PlotServer running at port %s ... \n" % str(self.chart_port))
        balance_process.start()
        logging.info("Balance PlotServer running at port %s ... \n" % str(self.balance_port))

    def on_event(self, event: Event):
        if isinstance(event, Plot):
            plot = event.payload
            if plot['name'].lower() == 'price':
                date = int(datetime.timestamp(datetime.fromisoformat(plot['data']['datetime']))) * 1000
                self.series['OHLC']['data'].append([date,
                                                    plot['data']['open'],
                                                    plot['data']['high'],
                                                    plot['data']['low'],
                                                    plot['data']['close']])
                if plot['data']['liquidationPrice'] is not None and 0.8 < plot['data']['liquidationPrice'] / \
                        plot['data']['close'] < 1.2:
                    liq_price = plot['data']['liquidationPrice']
                else:
                    liq_price = None
                self.series['liq_price']['data'].append([date, liq_price])
                self.series['volume']['data'].append([date, plot['data']['vol']])
                y = round(self.balance['quote_balance'] + self.balance['base_balance'] * plot['data']['close'])
                self.series['equity']['data'].append([date, y])

                self.series['base_equity']['data'].append([date,
                    self.balance['base_balance'] + self.balance['quote_balance'] / plot['data']['close']])
                self.series['position']['data'].append([date, self.balance['position_vol'] + 0])
                self.series['position_price']['data'].append([date, self.balance['position_price']])
                self.series['quote_balance']['data'].append([date, round(self.balance['quote_balance'], 2)])
                self.series['base_balance']['data'].append([date, self.balance['base_balance']])
                self.series['hold']['data'].append([date, round(self.series['base_equity']['data'][0][1] *
                    plot['data']['close']) if self.series['base_equity']['data'] else round(
                    plot['data']['base_equity'] * plot['data']['close'])])

                if self.live_plot:
                    time.sleep(1)
                    self.new_price()
            elif plot['name'].lower() == 'equity':
                if self.series['assets'] is None:
                    self.series['assets'] = {'quote': plot['quote'], 'base': plot['base']}
                    if self.live_plot:
                        asyncio.get_event_loop().run_until_complete(self.update_plot({"action": "produce",
                                                                                      "type": "assets",
                                                                                      "data": self.series['assets']
                                                                                      }, self.chart_port))
                        asyncio.get_event_loop().run_until_complete(self.update_plot({"action": "produce",
                                                                                      "type": "assets",
                                                                                      "data": self.series['assets']
                                                                                      }, self.balance_port))
                self.balance['quote'] = round(plot['data']['y'], 2)
                self.balance['base'] = plot['data']['base_equity']
                self.balance['quote_balance'] = plot['data']['quote_balance']
                self.balance['base_balance'] = plot['data']['base_balance']
                self.balance['position_vol'] = plot['data']['position_vol']
                self.balance['position_price'] = plot['data']['position_price'] if plot['data'][
                                                                       'position_price'] != 0 else None
                self.balance['invested'] = plot['data']['invested']

            elif plot['name'].lower() == 'buy':
                if self.chart_type > 0:
                    order_data = self.format_order_data(plot)
                    self.series['buy']['data'].append(order_data)
                    if self.chart_type > 1:
                        self.close_line(order_data, self.series['buy_series']['series'])

                    if self.live_plot:
                        asyncio.get_event_loop().run_until_complete(self.update_plot({"action": "produce",
                                                                                      "type": 'buy',
                                                                                      "data": order_data
                                                                                      }, self.chart_port))
            elif plot['name'].lower() == 'sell':
                if self.chart_type > 0:
                    order_data = self.format_order_data(plot)
                    self.series['sell']['data'].append(order_data)
                    if self.chart_type > 1:
                        self.close_line(order_data, self.series['sell_series']['series'])
                    if self.live_plot:
                        asyncio.get_event_loop().run_until_complete(self.update_plot({"action": "produce",
                                                                                      "type": 'sell',
                                                                                      "data": order_data
                                                                                      }, self.chart_port))
            elif plot['name'].lower() == 'open_buy':
                if self.chart_type > 1:
                    order_data = self.format_order_data(plot)
                    self.series['open_buy']['data'].append(order_data)
                    self.open_line(order_data, self.series['buy_series']['series'])

            elif plot['name'].lower() == 'open_sell':
                if self.chart_type > 1:
                    order_data = self.format_order_data(plot)
                    self.series['open_sell']['data'].append(order_data)
                    self.open_line(order_data, self.series['sell_series']['series'])

            elif plot['name'].lower() == 'cancel_buy':
                if self.chart_type > 1:
                    order_data = self.format_order_data(plot)
                    self.series['cancel_buy']['data'].append(order_data)

                    self.close_line(order_data, self.series['buy_series']['series'])

            elif plot['name'].lower() == 'cancel_sell':
                if self.chart_type > 1:
                    order_data = self.format_order_data(plot)
                    self.series['cancel_sell']['data'].append(order_data)

                    self.close_line(order_data, self.series['sell_series']['series'])

            else:
                if plot['name'] not in self.series:
                    self.series[plot['name']] = plot.copy()
                    self.series[plot['name']]['data'] = []
                data = plot['data'].copy()
                if 'tooltip' not in data:
                    data['tooltip'] = data['y']

    def format_order_data(self, plot):
        date = int(datetime.timestamp(datetime.fromisoformat(plot['data']['x']))) * 1000
        order_data = [date, plot['data']['y'], plot['data']['type'] + ": " + str(plot['data']['tooltip']),
                      plot['data']['id']]
        return order_data

    def open_line(self, order_data, series):
        for serie in series:
            if not serie or not serie[-1][1]:
                serie.append(order_data)
                return True
        series.append([order_data])

    def close_line(self, order_data, series):
        for serie in series:
            if serie and serie[-1][3] == order_data[3]:
                serie.append(order_data)
                serie.append([order_data[0], None])
                return True
        print("Order ID not found %s ... \n" % str(order_data))

    def plot(self, filename='index.html'):
        dir_name = str(random.randint(0, 100))
        os.chdir(System.get_cache_dir())
        dir_list = os.listdir()
        if dir_name not in dir_list:
            os.mkdir(dir_name)
        self.save_to_file("/"+dir_name+"/")
        WebServer.serve(
            routing={
                "/data/": "%s/%s/" % (System.get_cache_dir(), dir_name),
                "/": "%s/lib" % os.path.dirname(__file__),
            },
            open_browser=True,
            timeout=40,
            filename='/' + filename
        )
        shutil.rmtree(dir_name)

    def save_to_file(self, dir_name):
        plot_data = {"buy": self.series['buy']['data'], "sell": self.series['sell']['data'], "assets": self.series['assets']}
        logging.info("Buy orders count: %s" % str(len(plot_data['buy'])))
        logging.info("Sell orders count: %s" % str(len(plot_data['sell'])))
        with open('%s%sorders_data.json' % (System.get_cache_dir(), dir_name), 'w') as outfile:
            json.dump(self.series, outfile)

    def new_price(self):
        time.sleep(1)
        data = {"OHLC": self.series["OHLC"]['data'][-1],
                "volume": self.series["volume"]['data'][-1],
                "pos_vol": self.series["position"]['data'][-1],
                "equity": self.series["equity"]['data'][-1],
                "base_equity": self.series["base_equity"]['data'][-1],
                "hold": self.series["hold"]['data'][-1],
                "pos_p": self.series["position_price"]['data'][-1]
                }
        balance_data = {
                "pos_vol": self.series["position"]['data'][-1],
                "equity": self.series["equity"]['data'][-1],
                "base_equity": self.series["base_equity"]['data'][-1],
                "hold": self.series["hold"]['data'][-1]
                }

        asyncio.get_event_loop().run_until_complete(self.update_plot({"action": "produce",
                                                                      "type": "price",
                                                                      "data": data
                                                                      }, self.chart_port))
        asyncio.get_event_loop().run_until_complete(self.update_plot({"action": "produce",
                                                                      "type": "price",
                                                                      "data": balance_data
                                                                      }, self.balance_port))

    async def update_plot(self, data, port):
        uri = "ws://localhost:" + str(port)
        async with websockets.connect(uri) as websocket:
            await websocket.send(json.dumps(data))
            await websocket.close()
