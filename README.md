# TradingKit
This file shows the basic usage for TradingKit, for more docs, please see the [Wiki](https://github.com/Logictraders/tradingkit/wiki)

![stable](https://img.shields.io/badge/stable-1.1.5-blue)
![coverage](https://img.shields.io/badge/coverage-37%25-orange)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)

## Requirements
- python 3.7+
- python virtual environment (venv)
- pip

## Installation
the recommended (and unique supported way) to install TradingKit si via **pip**.

### Instructions for unix
```bash
# clone repo
git clone git@github.com:logictraders/tradingkit.git
cd tradingkit

# create and activate virtual environment (venv)
python -m venv venv
source venv/bin/activate

# install the package for development
pip install -e .
```

### Instructions for windows
```bash
# TODO...
```

## Creating strategies
In order to create new strategies you need **5 steps**
### Create separate project
Create new python3.7+ project, no need to do anymore in this step.

### Install virtualenv and dependencies
To do this step need to install previously TradingKit with the installation steps described above.
```bash
cd my_project
python -m venv venv
source venv/bin/activate
pip install ccxt
pip install -e ../tradingkit
```

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
