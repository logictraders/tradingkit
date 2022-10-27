# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

### [1.11.7](https://github.com/logictraders/tradingkit/compare/v1.11.6...v1.11.7) (2022-10-27)


### Bug Fixes

* **kraken:** fixed feeder ([86e1de4](https://github.com/logictraders/tradingkit/commit/86e1de4))



### [1.11.6](https://github.com/logictraders/tradingkit/compare/v1.11.5...v1.11.6) (2022-10-26)


### Bug Fixes

* **kraken:** improved kraken feeder and aggregator ([4d9c083](https://github.com/logictraders/tradingkit/commit/4d9c083))
* **setup:** bumped minimum python version to 3.9 ([61ead7c](https://github.com/logictraders/tradingkit/commit/61ead7c))



### [1.11.5](https://github.com/logictraders/tradingkit/compare/v1.11.4...v1.11.5) (2022-10-26)


### Bug Fixes

* **bridge:** disabled plotting ([45b2b8b](https://github.com/logictraders/tradingkit/commit/45b2b8bdaf543eb4d4320a91589bdd6056557732))
* **feeder:** improved private kraken feeder ([c6bc8fc](https://github.com/logictraders/tradingkit/commit/c6bc8fc6707daaacd6caf41e7a2c9d29d13ceb55))

### [1.11.4](https://github.com/logictraders/tradingkit/compare/v1.11.3...v1.11.4) (2022-10-20)


### Bug Fixes

* **feeder:** congregate events from feeders in the main process ([1283b81](https://github.com/logictraders/tradingkit/commit/1283b81))



### [1.11.3](https://github.com/logictraders/tradingkit/compare/v1.11.2...v1.11.3) (2022-08-25)


### Bug Fixes

* **feeder:** enforce terminate subprocesses when parent gets terminated ([5c2c331](https://github.com/logictraders/tradingkit/commit/5c2c331))
* **feeder:** no need to terminate the rest of children when main process ends ([3adb78d](https://github.com/logictraders/tradingkit/commit/3adb78d))



### [1.11.2](https://github.com/logictraders/tradingkit/compare/v1.11.1...v1.11.2) (2022-06-27)


### Bug Fixes

* **bridge:** checking if base is in balances before access (was raising keyerror) ([037c7ac](https://github.com/logictraders/tradingkit/commit/037c7aca52845a1d0d14b93f6e229126ab155f10))
* **kraken:** removing feeder reconnection, feeder was hiding errors from strategy ([448b8a6](https://github.com/logictraders/tradingkit/commit/448b8a6a8ed08909bbd7f34994217b28d2c7a00a))



### [1.11.1](https://github.com/logictraders/tradingkit/compare/v1.11.0...v1.11.1) (2022-05-17)


### Bug Fixes

* **deps:** downgraded ccxt dependency due to errors in bitmex ([46967a9](https://github.com/logictraders/tradingkit/commit/46967a93a48e4439d6f5a47b17e7cae010684b27))

## [1.11.0](https://github.com/logictraders/tradingkit/compare/v1.10.2...v1.11.0) (2022-05-16)


### Features

* **feeder:** added exchange labels for different exchanges ([#50](https://github.com/logictraders/tradingkit/issues/50)) ([2bed4bd](https://github.com/logictraders/tradingkit/commit/2bed4bdcc3abbf836ee0e1397f9cf48118c04c1f))
* **kraken:** added new pairs with eth ([#53](https://github.com/logictraders/tradingkit/issues/53)) ([f48c8cf](https://github.com/logictraders/tradingkit/commit/f48c8cf50f16e7cfbdf1b86306e91129ff0fdb4e))
* **statistics:** separated statistics module ([#52](https://github.com/logictraders/tradingkit/issues/52)) ([313037c](https://github.com/logictraders/tradingkit/commit/313037c1032e3f74a4f8e5b188a405593b01c190))
* **testex:** fetch closed orders ([#48](https://github.com/logictraders/tradingkit/issues/48)) ([69f94e8](https://github.com/logictraders/tradingkit/commit/69f94e81bd82d1d4e536dbc83186e7f725832fb7))


### Bug Fixes

* **optimizer:** speed refactor ([#47](https://github.com/logictraders/tradingkit/issues/47)) ([0547f8b](https://github.com/logictraders/tradingkit/commit/0547f8b57b979690c65c5a7f6677666dcf696f2d))
* **telegram:** removed telegram integration ([#44](https://github.com/logictraders/tradingkit/issues/44)) ([7081ff5](https://github.com/logictraders/tradingkit/commit/7081ff56e64b34209936dfac072940a1690db57d))

### [1.10.2](https://github.com/logictraders/tradingkit/compare/v1.10.1...v1.10.2) (2022-03-05)


### Bug Fixes

* **bridge:** removed calculate_exchange_state implementation due to be source of many bugs ([e4e1fcc](https://github.com/logictraders/tradingkit/commit/e4e1fcc))



### [1.10.1](https://github.com/logictraders/tradingkit/compare/v1.10.0...v1.10.1) (2022-03-01)


### Bug Fixes

* **kraken:** problem with private feeder ([8e9502b](https://github.com/logictraders/tradingkit/commit/8e9502b))



## [1.10.0](https://github.com/logictraders/tradingkit/compare/v1.9.6...v1.10.0) (2022-02-10)


### Bug Fixes

* **bitmex:** liquidation price ([#40](https://github.com/logictraders/tradingkit/issues/40)) ([2042a6e](https://github.com/logictraders/tradingkit/commit/2042a6e))
* **bridge:** bugfix in calculate exchange balance ([b81baff](https://github.com/logictraders/tradingkit/commit/b81baff))
* **kraken:** added tests to kraken feeder ([#41](https://github.com/logictraders/tradingkit/issues/41)) ([ea7d96a](https://github.com/logictraders/tradingkit/commit/ea7d96a))
* **kraken:** added tests to kraken feeder ([#41](https://github.com/logictraders/tradingkit/issues/41)) ([dfa55b1](https://github.com/logictraders/tradingkit/commit/dfa55b1))
* **kraken:** added tests to kraken feeder ([#41](https://github.com/logictraders/tradingkit/issues/41)) ([5de5fa2](https://github.com/logictraders/tradingkit/commit/5de5fa2))
* **statistics:** reimplemented max drawdown (MDD) calculation ([#42](https://github.com/logictraders/tradingkit/issues/42)) ([c369b69](https://github.com/logictraders/tradingkit/commit/c369b69))
* **test_bitmex_feeder:** pass feeder object on calls ([#39](https://github.com/logictraders/tradingkit/issues/39)) ([726c04e](https://github.com/logictraders/tradingkit/commit/726c04e))


### Features

* **cli:** added fetch candle option ([#43](https://github.com/logictraders/tradingkit/issues/43)) ([df00ef4](https://github.com/logictraders/tradingkit/commit/df00ef4))
* **PRs:** inclued al PR pending ([b935536](https://github.com/logictraders/tradingkit/commit/b935536))



### [1.9.6](https://github.com/logictraders/tradingkit/compare/v1.9.5...v1.9.6) (2021-12-01)


### Bug Fixes

* **feeder:** increased websocket ping interval and timeout ([8240c86](https://github.com/logictraders/tradingkit/commit/8240c86))



### [1.9.5](https://github.com/logictraders/tradingkit/compare/v1.9.4...v1.9.5) (2021-11-30)



### [1.9.4](https://github.com/logictraders/tradingkit/compare/v1.9.3...v1.9.4) (2021-11-29)


### Bug Fixes

* **feed:** changed aggregator feeder from threads to processes ([f1e7224](https://github.com/logictraders/tradingkit/commit/f1e7224))



### [1.9.3](https://github.com/logictraders/tradingkit/compare/v1.9.2...v1.9.3) (2021-11-29)


### Bug Fixes

* **feed:** exiting aggregator feeder when any child ends its execution ([111f00f](https://github.com/logictraders/tradingkit/commit/111f00f))



### [1.9.2](https://github.com/logictraders/tradingkit/compare/v1.9.1...v1.9.2) (2021-11-28)



### [1.9.1](https://github.com/logictraders/tradingkit/compare/v1.9.0...v1.9.1) (2021-11-28)


### Bug Fixes

* **deps:** updated websocket-client to v1.2.1 ([ee215e9](https://github.com/logictraders/tradingkit/commit/ee215e9))
* **refactor:** refactored websocket feeders ([e35f5f2](https://github.com/logictraders/tradingkit/commit/e35f5f2))



## [1.9.0](https://github.com/logictraders/tradingkit/compare/v1.8.1...v1.9.0) (2021-11-28)


### Features

* **feed:** implemented aggregator_feeder and websocket feeder ([2e6a570](https://github.com/logictraders/tradingkit/commit/2e6a570))



### [1.8.1](https://github.com/logictraders/tradingkit/compare/v1.8.0...v1.8.1) (2021-11-27)


### Bug Fixes

* **kraken:** changed normalize to denormalize before dispatch order ([58acf51](https://github.com/logictraders/tradingkit/commit/58acf51))
* **kraken:** removing extra debug info ([2f070a8](https://github.com/logictraders/tradingkit/commit/2f070a8))



## [1.8.0](https://github.com/logictraders/tradingkit/compare/v1.7.15...v1.8.0) (2021-11-25)


### Bug Fixes

* **simulation:** fixed bitmex liquidation_price calculation and added short liquidation_price ([#34](https://github.com/logictraders/tradingkit/issues/34)) ([c7a26f5](https://github.com/logictraders/tradingkit/commit/c7a26f5))
* **testing:** added bitmex tests ([#36](https://github.com/logictraders/tradingkit/issues/36)) ([a9c3593](https://github.com/logictraders/tradingkit/commit/a9c3593))


### Features

* **bridge:** refactored removing exess of API calls ([#38](https://github.com/logictraders/tradingkit/issues/38)) ([561eb7c](https://github.com/logictraders/tradingkit/commit/561eb7c))
* **data:** creating candles cache when import data ([#35](https://github.com/logictraders/tradingkit/issues/35)) ([ebf8bb3](https://github.com/logictraders/tradingkit/commit/ebf8bb3))



### [1.7.15](https://github.com/logictraders/tradingkit/compare/v1.7.14...v1.7.15) (2021-11-24)


### Bug Fixes

* **bridge:** changed timeframes ([4ba6501](https://github.com/logictraders/tradingkit/commit/4ba6501))



### [1.7.14](https://github.com/logictraders/tradingkit/compare/v1.7.10...v1.7.14) (2021-11-24)


### Bug Fixes

* **refactor:** refactored kraken feeder ([1385575](https://github.com/logictraders/tradingkit/commit/1385575))
* **config:** fixed default variable loading error when empty string ([a4192aa](https://github.com/logictraders/tradingkit/commit/a4192aa))



### [1.7.10](https://github.com/logictraders/tradingkit/compare/v1.7.9...v1.7.10) (2021-11-24)


### Bug Fixes

* **kraken:** set ignore_outdated to false by default and fixed some useless data ([a60824f](https://github.com/logictraders/tradingkit/commit/a60824f))



### [1.7.9](https://github.com/logictraders/tradingkit/compare/v1.7.8...v1.7.9) (2021-11-23)


### Bug Fixes

* **typo:** fixed typo ([7119f0d](https://github.com/logictraders/tradingkit/commit/7119f0d))



### [1.7.8](https://github.com/logictraders/tradingkit/compare/v1.7.7...v1.7.8) (2021-11-17)


### Bug Fixes

* **bridge:** removed code calling the exchange on events, needs to fix plotting ([303ee0c](https://github.com/logictraders/tradingkit/commit/303ee0c))



### [1.7.7](https://github.com/logictraders/tradingkit/compare/v1.7.6...v1.7.7) (2021-11-16)


### Bug Fixes

* **runner:** avoiding register plotter to events when plot is not requested ([2d60c76](https://github.com/logictraders/tradingkit/commit/2d60c76))



### [1.7.6](https://github.com/logictraders/tradingkit/compare/v1.7.5...v1.7.6) (2021-11-16)


### Bug Fixes

* **bridge:** removed useless pairs_dictionary ([a71d5ed](https://github.com/logictraders/tradingkit/commit/a71d5ed))



### [1.7.5](https://github.com/logictraders/tradingkit/compare/v1.7.4...v1.7.5) (2021-11-16)


### Bug Fixes

* **config:** adding symbol to bitmex feeder injection ([3633f96](https://github.com/logictraders/tradingkit/commit/3633f96))



### [1.7.4](https://github.com/logictraders/tradingkit/compare/v1.7.3...v1.7.4) (2021-11-16)


### Bug Fixes

* **bitmex:** adding usdt to bitmex feeder ([8ad697d](https://github.com/logictraders/tradingkit/commit/8ad697d))



### [1.7.3](https://github.com/logictraders/tradingkit/compare/v1.7.2...v1.7.3) (2021-11-02)


### Bug Fixes

* **plotter:** fixed bug with highstock plotter ([a1fce12](https://github.com/logictraders/tradingkit/commit/a1fce12))



### [1.7.2](https://github.com/logictraders/tradingkit/compare/v1.7.1...v1.7.2) (2021-11-02)


### Bug Fixes

* **bitmex:** fixed feeder and implemented bitmex feeder test ([#37](https://github.com/logictraders/tradingkit/issues/37)) ([72937ca](https://github.com/logictraders/tradingkit/commit/72937ca))



### [1.7.1](https://github.com/logictraders/tradingkit/compare/v1.7.0...v1.7.1) (2021-11-02)


### Bug Fixes

* **bitmex:** updated bitmex websocket endpoint (https://blog.bitmex.com/api_announcement/change-of-websocket-endpoint/) ([d8ad642](https://github.com/logictraders/tradingkit/commit/d8ad642))
* **plotter:** removed highstock lib ([#33](https://github.com/logictraders/tradingkit/issues/33)) ([a1eb453](https://github.com/logictraders/tradingkit/commit/a1eb453))



## [1.7.0](https://github.com/logictraders/tradingkit/compare/v1.6.7...v1.7.0) (2021-10-13)


### Bug Fixes

* **kraken:** fixed kraken compatibility ([#31](https://github.com/logictraders/tradingkit/issues/31)) ([f5eb8c9](https://github.com/logictraders/tradingkit/commit/f5eb8c9))
* **readme:** added injectable module info ([#29](https://github.com/logictraders/tradingkit/issues/29)) ([28cea1c](https://github.com/logictraders/tradingkit/commit/28cea1c))


### Features

* **candle:** adding timeframe info to candles ([#30](https://github.com/logictraders/tradingkit/issues/30)) ([bd18b98](https://github.com/logictraders/tradingkit/commit/bd18b98))
* **kraken_feeder:** last version ([#28](https://github.com/logictraders/tradingkit/issues/28)) ([4a422a8](https://github.com/logictraders/tradingkit/commit/4a422a8))



### [1.6.7](https://github.com/logictraders/tradingkit/compare/v1.6.6...v1.6.7) (2021-05-07)

### [1.6.6](https://github.com/logictraders/tradingkit/compare/v1.6.5...v1.6.6) (2021-05-04)


### Bug Fixes

* **state_machine:** added info logging ([a067679](https://github.com/logictraders/tradingkit/commit/a067679358426ad24bd12259a47fa76958725738))

### [1.6.5](https://github.com/logictraders/tradingkit/compare/v1.6.4...v1.6.5) (2021-05-04)


### Bug Fixes

* **bitmex:** added 10 sec wait before exiting when a network error is detected ([3053dcc](https://github.com/logictraders/tradingkit/commit/3053dcc67bb1687861f174ad6013c0e1b58a77af))

### [1.6.4](https://github.com/logictraders/tradingkit/compare/v1.6.3...v1.6.4) (2021-05-04)


### Bug Fixes

* **bitmex:** added ping-pong to bitmex websocket ([4ed68ad](https://github.com/logictraders/tradingkit/commit/4ed68adfb0fe90ca239763392a628dfd8ef5e849))

### [1.6.3](https://github.com/logictraders/tradingkit/compare/v1.6.2...v1.6.3) (2021-05-04)


### Bug Fixes

* **bitmex:** exiting after any strategy error instead of reconnecting ([783da5d](https://github.com/logictraders/tradingkit/commit/783da5d97c5daa7db6fd41754787d8e453a0f672))

### [1.6.2](https://github.com/logictraders/tradingkit/compare/v1.6.1...v1.6.2) (2021-05-03)


### Bug Fixes

* **bitmex:** fixed liquidation price calculation, only working for longs at this point ([72ed539](https://github.com/logictraders/tradingkit/commit/72ed539))



### [1.6.1](https://github.com/logictraders/tradingkit/compare/v1.6.0...v1.6.1) (2021-04-29)

## [1.6.0](https://github.com/logictraders/tradingkit/compare/v1.5.4...v1.6.0) (2021-04-29)


### Features

* **bitmex_backtest:** added liquidation log ([#20](https://github.com/logictraders/tradingkit/issues/20)) ([87bba8b](https://github.com/logictraders/tradingkit/commit/87bba8b1762d7147b1f04222863df45e7f036f3b))

### [1.5.4](https://github.com/logictraders/tradingkit/compare/v1.5.3...v1.5.4) (2021-04-29)


### Bug Fixes

* **bitmex_backtest:** fixed free balance ([#17](https://github.com/logictraders/tradingkit/issues/17)) ([881b75d](https://github.com/logictraders/tradingkit/commit/881b75d08389bb4f197c5b4680c8328901c7daae))

### [1.5.3](https://github.com/logictraders/tradingkit/compare/v1.5.2...v1.5.3) (2021-04-29)

### [1.5.2](https://github.com/logictraders/tradingkit/compare/v1.5.1...v1.5.2) (2021-04-28)


### Bug Fixes

* **balance:** update chart on open order ([#16](https://github.com/logictraders/tradingkit/issues/16)) ([e2bf8bd](https://github.com/logictraders/tradingkit/commit/e2bf8bda6f06b1c4307f60a663c93749c710e05b))
* **strategy:** fixed syntax error ([a038170](https://github.com/logictraders/tradingkit/commit/a038170634ec8be093b89e15a33b7b5d7b7132b2))

### [1.5.1](https://github.com/logictraders/tradingkit/compare/v1.5.0...v1.5.1) (2021-04-28)


### Bug Fixes

* **dummy:** syntax error ([5e80d04](https://github.com/logictraders/tradingkit/commit/5e80d0467a8d8a66126fe90f55f05203b286564c))

## [1.5.0](https://github.com/logictraders/tradingkit/compare/v1.4.0...v1.5.0) (2021-04-28)


### Features

* **misc:** Optimizer improvements and stop orders ([#14](https://github.com/logictraders/tradingkit/issues/14)) ([8cb9bad](https://github.com/logictraders/tradingkit/commit/8cb9bad2e1b6856d1d5519c69ffbc3461b7d04e3))

## [1.4.0](https://github.com/logictraders/tradingkit/compare/v1.3.0...v1.4.0) (2021-04-28)


### Features

* **optimization:** implementer basic optimizer ([#12](https://github.com/logictraders/tradingkit/issues/12)) ([71b76a6](https://github.com/logictraders/tradingkit/commit/71b76a6fc0dda188e6778b291641096fda45708a))
* **stats:** adding max drawdown and sharp ratio statistics ([#13](https://github.com/logictraders/tradingkit/issues/13)) ([c36bcc3](https://github.com/logictraders/tradingkit/commit/c36bcc3c81d21947af2f9d311c760e4239537ed0))

## [1.3.0](https://github.com/logictraders/tradingkit/compare/v1.2.8...v1.3.0) (2021-01-13)


### Features

* **import:** Added ability to download funding rate at import ([#11](https://github.com/logictraders/tradingkit/issues/11)) ([8fe12d0](https://github.com/logictraders/tradingkit/commit/8fe12d0e36be3cdfb8788016c0e6bdbccc030724))


### Bug Fixes

* **deps:** updated dependencies ([09229dd](https://github.com/logictraders/tradingkit/commit/09229dd9b271df7e6bc5164cd25d8f516c320561))

### [1.2.8](https://github.com/logictraders/tradingkit/compare/v1.2.7...v1.2.8) (2021-01-11)


### Bug Fixes

* **bitmex_backtest:** added fetch_balance method and allow nullable funding_rate on liquidation price formula ([#10](https://github.com/logictraders/tradingkit/issues/10)) ([6d91049](https://github.com/logictraders/tradingkit/commit/6d91049aed4c547dfc387f36ed590feb742a1ffc))
* **deps:** updated dependencies ([a4292cc](https://github.com/logictraders/tradingkit/commit/a4292ccc006cda9ca5adcdea1c111a0ccdb1b7e4))

### [1.2.7](https://github.com/logictraders/tradingkit/compare/v1.2.6...v1.2.7) (2021-01-10)


### Bug Fixes

* **bitmex_backtest:** changed liquidation price formula ([#9](https://github.com/logictraders/tradingkit/issues/9)) ([5e0dbd5](https://github.com/logictraders/tradingkit/commit/5e0dbd5e9c31d5852be8695e44f28677baa6a63d))

### [1.2.6](https://github.com/logictraders/tradingkit/compare/v1.2.5...v1.2.6) (2021-01-06)


### Bug Fixes

* **bitmex_backtest:** added fetch_balance method ([#6](https://github.com/logictraders/tradingkit/issues/6)) ([137a4ba](https://github.com/logictraders/tradingkit/commit/137a4bab28f52d5bd0e5d098c451342ed908ab36))
* **deps:** updated deps ([7e7a849](https://github.com/logictraders/tradingkit/commit/7e7a8498f4b5209369224f7d7ca98934bd127804))
* **dummy:** fixed changelog versions ([ab1e4fc](https://github.com/logictraders/tradingkit/commit/ab1e4fc86ea28660140e1890163676f7102f45e8))

### [1.2.5](https://github.com/logictraders/tradingkit/compare/v1.2.3...v1.2.5) (2021-01-03)


### Bug Fixes

* **deps:** fixed problems with python deps ([0d32504](https://github.com/logictraders/tradingkit/commit/0d32504e1defc000d84846b1f028d4b3180a4fb6))
* **github:** bumped workflow builder version to ubuntu 20.04 ([b8a77ce](https://github.com/logictraders/tradingkit/commit/b8a77ce7c144060205e80a1b333e31b3aa6e64b6))
* **github:** testing with ubuntu 20.04 gh workflow ([a6ab95b](https://github.com/logictraders/tradingkit/commit/a6ab95b344dcc13f151f27536cb3594feddcc7ec))

### [1.2.3](https://github.com/logictraders/tradingkit/compare/v1.2.2...v1.2.3) (2021-01-03)


### Bug Fixes

* **deps:** added chardet==3.0.4 dep because incompatibilities and updated deps ([7c8b7b0](https://github.com/logictraders/tradingkit/commit/7c8b7b079d8e7cddce458217898bfb468ff381cc))

### [1.2.2](https://github.com/logictraders/tradingkit/compare/v1.2.1...v1.2.2) (2020-12-18)


### Bug Fixes

* **deps:** downgraded np dep ([8176b26](https://github.com/logictraders/tradingkit/commit/8176b261d165129525fc82a2f7f7c3516d0f2cde))

### [1.2.1](https://github.com/logictraders/tradingkit/compare/v1.2.0...v1.2.1) (2020-12-18)


### Bug Fixes

* **deps:** bumped dep version ([46330a9](https://github.com/logictraders/tradingkit/commit/46330a949f681d2db4b57337a81f5f5b1b77e8a5))

## [1.2.0](https://github.com/logictraders/tradingkit/compare/v1.1.18...v1.2.0) (2020-11-16)


### Features

* **config:** changed config path to <strat>/config/ ([3829e40](https://github.com/logictraders/tradingkit/commit/3829e4001d439612e00d4994e9c3e3b84e89994e))


### Bug Fixes

* **config:** fixed config loading ([d6ec103](https://github.com/logictraders/tradingkit/commit/d6ec1037f5472c043b26795038f42d212b68a3dd))
* **packaging:** added init to config package ([21fe3d5](https://github.com/logictraders/tradingkit/commit/21fe3d5719f80ab6c2017bca1e93f93be0d4c1e6))

### [1.1.18](https://github.com/logictraders/tradingkit/compare/v1.1.5...v1.1.18) (2020-11-16)


### Bug Fixes

* **packaging:** adding config data to package ([93fb060](https://github.com/logictraders/tradingkit/commit/93fb06059aaddec6f8d6f5a5f1982956eb0e73ca))
* **packaging:** changed from setuptools to setuptools_git ([607b9fc](https://github.com/logictraders/tradingkit/commit/607b9fc3aba15d315772edfe67b761b539940e70))
* **packaging:** created MANIFEST.in ([acabe2f](https://github.com/logictraders/tradingkit/commit/acabe2f603e5a761895357a83c0178cfdae73b26))
* **packaging:** fixed packaging (several tries & fixes)

### [1.1.5](https://github.com/logictraders/tradingkit/compare/v1.1.4...v1.1.5) (2020-11-12)


### Bug Fixes

* **deps:** update deps ([53507f6](https://github.com/logictraders/tradingkit/commit/53507f67b9fd4036b90d0f30beb68470885fd214))

### [1.1.4](https://github.com/logictraders/tradingkit/compare/v1.1.3...v1.1.4) (2020-11-12)


### Bug Fixes

* **github:** fixed release wf ([59b7782](https://github.com/logictraders/tradingkit/commit/59b7782da1fa738b66116b1c8be22e518d1e5ab5))

### [1.1.3](https://github.com/logictraders/tradingkit/compare/v1.1.2...v1.1.3) (2020-11-12)


### Bug Fixes

* **github:** changed master branch to main ([5c1f0f6](https://github.com/logictraders/tradingkit/commit/5c1f0f615162e37780aa3520357ff87caacf473d))
* **github:** fixes in workflows ([5096357](https://github.com/logictraders/tradingkit/commit/50963574991da87e031b01a3177ca02fdf38fd35))
* **github:** fixes in workflows II ([152bbea](https://github.com/logictraders/tradingkit/commit/152bbea3908b016e358d4df29a0a8359338a7c2b))
* **version:** bumped versions ([3d02967](https://github.com/logictraders/tradingkit/commit/3d029673af6d11cac1ef8adfef3900161bb84c68))

### [1.1.2](https://github.com/logictraders/tradingkit/compare/v1.1.1...v1.1.2) (2020-11-12)


### Bug Fixes

* **github:** removed coverage wf ([ca44ff6](https://github.com/logictraders/tradingkit/commit/ca44ff6ab306e16dbceba0c7a04287fe691d811d))

### [1.1.1](https://github.com/logictraders/tradingkit/compare/v1.1.0...v1.1.1) (2020-11-12)


### Bug Fixes

* **github:** fixed release workflow ([4f8d4eb](https://github.com/logictraders/tradingkit/commit/4f8d4eba5fc179b4e3e8d1c8d4cf18d3d54083bf))

## 1.1.0 (2020-11-12)


### Features

* **import:** imported base code ([34723ed](https://github.com/logictraders/tradingkit/commit/34723edabac30445652fb8c8fd59bcf0adcab353))


### Bug Fixes

* **changelog:** reset changelog ([1507a59](https://github.com/logictraders/tradingkit/commit/1507a59c302cc4206dbaaf65ff4069d9d1698a3e))
* **refactor:** renamed old qbitartifacts references to logictraders ([0d534ce](https://github.com/logictraders/tradingkit/commit/0d534ce6ab4433ac9d1d081001385c63db655304))
