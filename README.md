# TradingKit
This file shows the basic usage for TradingKit, for more docs, please see the [Wiki](https://github.com/Logictraders/tradingkit/wiki)

![PyPI](https://img.shields.io/pypi/v/tradingkit)
![coverage](https://img.shields.io/badge/coverage-37%25-orange)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)

## Requirements
- python 3.7+
- pip

## Installation
the recommended way to install TradingKit si via **PyPi**.

### Install from [PyPi](https://pypi.org/project/tradingkit/)
```bash
pip3 install tradingkit
```

### Install from [Source](https://github.com/logictraders/tradingkit)
```bash
git clone https://github.com/logictraders/tradingkit
cd tradingkit
# Optional, uncomment the line below if you want a specific version
# git checkout v1.2.5
python3 setup.py install
```

## Creating strategies
In order to create new strategies you need **4 steps**

### Create separate project
Create new python3.7+ project, no need to do anymore in this step.

### Creating strategy class
create a class extending from `tradingkit.strategy.strategy.Strategy`
```python
# File my_project/my_strategy.py
import logging
import ccxt.Exchange

from tradingkit.pubsub.event.trade import Trade
from tradingkit.pubsub.event.book import Book
from tradingkit.pubsub.event.order import Order
from tradingkit.pubsub.core.event import Event
from tradingkit.strategy.strategy import Strategy


class MyStrategy(Strategy):

    def __init__(self, exchange: Exchange, config):
        super().__init__(exchange, config)
        # do whatever initializations you need

    def on_event(self, event: Event):
        if isinstance(event, Trade):
            logging.info("Order event happened!")
            # do whatever you need with the exchange
            self.exchange.create_order(...)
        if isinstance(event, Book):
            logging.info("Book event happened!")
            # do whatever you need with the exchange
            self.exchange.create_order(...)
        if isinstance(event, Order):
            logging.info("Order event happened!")
            # do whatever you need with the exchange
            self.exchange.create_order(...)
```
### Create main config file
create `system/config.json` file
```json
{
    "strategy": {
        "class": "my_strategy.MyStrategy",
        "arguments": ["@bridge", "@config"]
    },
    "config": {
        "symbol": "%env(SYMBOL)%"
    }
}
```
create `.env` file to add some env vars
```bash
# File .env
SYMBOL=BTC/EUR
```


### Configure dev environment
create `system/config.dev.json` file
```json
{
    "exchange": "@testex",
    "feeder": "@backtest_feeder"
}
```

### Configure live environment
create `system/config.live.json` file
```json
{
    "exchange": "@kraken",
    "feeder": "@kraken_feeder"
}
```
create `.env.live.local` file to add your bitmex credentials credentials
```bash
# File .env.live.local
KRAKEN_KEY=xxxxxxxxxxxxxxxxxxx
KRAKEN_SECRET=yyyyyyyyyyyyyyyyyyyy
```


### Run dev (backtest)
```
tk run -e dev -y 2020 -m 1 --plot
```

### Run live
```
tk run -e live --plot
```

### Available configurations
Injectable modules:

| Module Type|     Key    |Module                        |              Description             | Arguments     |
|------------|------------|:-----------------------------|:-------------------------------------|---------------|
| Exchange   |exchange    |kraken                        |Kraken exchange API                               |apikey, secret |
| Exchange   |exchange    |bitmex                        |Bitmex exchange API                               |apikey, secret |
| Exchange   |exchange    |bitmex_testnet                |Bitmex testnet exchange API                       |apikey, secret |
| Exchange   |exchange    |testex                        |kraken exchange simulator                         |balances, fees |
| Exchange   |exchange    |bitmex_backtest               |bitmex exchange simulator                         |balances, fees |
| Feeder     |feeder      |kraken_backtest_feeder        |feeder used for kraken simulations                |exchange, symbol, since8601, to8601|
| Feeder     |feeder      |bitmex_funding_backtest_feeder|feeder used for bitmex simulations                |exchange, symbol, since8601, to8601|
| Feeder     |feeder      |bitmex_testnet_feeder         |feeder used for bitmex-testnet live strategies    |apikey, secret |
| Feeder     |feeder      |bitmex_feeder                 |feeder used for bitmex live strategies            |apikey, secret |
| Feeder     |feeder      |kraken_feeder                 |feeder used for kraken live strategies            |apikey, secret |
| Feeder     |feeder      |outlier_trade_filter          |feeder used to reduce back_test outlier trade data|MAX_PRICE_CHANGE_SINGLE_TRADE|
| Bridge     |bridge      |bridge                        |exchange interface for simulator and real exchange|exchange       |
| Plotter    |plotter     |highstock                     |plotter used to show simulation result on chart   ||
| Plotter    |plotter     |plotly                        |plotter used to show simulation result on chart   ||
