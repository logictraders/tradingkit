import plotly.graph_objects as go
import pandas as pd

from tradingkit.display.plotter import Plotter
from tradingkit.pubsub.core.event import Event
from tradingkit.pubsub.event.plot import Plot


class PlotlyPlotter(Plotter):

    def __init__(self):
        self.price = []
        self.series = {}

    def on_event(self, event: Event):
        if isinstance(event, Plot):
            plot = event.payload
            if plot['name'].lower() == 'price':
                self.price.append(plot['data'])
            else:
                if plot['name'] not in self.series:
                    self.series[plot['name']] = plot.copy()
                    self.series[plot['name']]['data'] = []
                data = plot['data'].copy()
                if 'tooltip' not in data:
                    data['tooltip'] = data['y']
                self.series[plot['name']]['data'].append(data)

    def plot(self):

        df = pd.DataFrame(self.price)
        if len(df) > 10000:
            data = [{
                'type': 'scatter',
                'name': 'Price',
                'yaxis': 'y2',
                'x': df['datetime'],
                'y': df['close']
            }]
        else:
            data = [{
                'type': 'candlestick',
                'name': 'Price',
                'yaxis': 'y2',
                'x': df['datetime'],
                'open': df['open'],
                'high': df['high'],
                'low': df['low'],
                'close': df['close']
            }]

        for serie in self.series.values():
            s = pd.DataFrame(serie['data'])
            data.append({
                'name': serie['name'],
                'type': serie['type'],
                'mode': serie['mode'],
                'line_color': serie['color'],
                'fillcolor': serie['color'],
                'x': s['x'],
                'y': s['y'],
                'text': s['tooltip'],
                'hovertemplate': '<b>%{text}</b>',
                'yaxis': 'y2' if serie['yaxis'] == 'price' else 'y',
                'line_width': 2
            })

        layout = {
            'xaxis': {'rangeselector': {'visible': True}},
            'yaxis': {'domain': [0, 0.1]},
            'yaxis2': {'domain': [0.1, 1]}
        }

        fig = go.Figure({'data': data, 'layout': layout})

        fig.show()

