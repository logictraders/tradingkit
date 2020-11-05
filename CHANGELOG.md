# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

## [1.1.0](https://github.com/QbitArtifacts/backtestex/compare/v1.0.0...v1.1.0) (2020-06-03)


### Bug Fixes

* **bitmex_backtest:** implemented compatibility with no funding feeder fixes [#66](https://github.com/QbitArtifacts/backtestex/issues/66) ([c60f3bf](https://github.com/QbitArtifacts/backtestex/commit/c60f3bf))
* **bitmex_feeder:** added reconnect when websocket throws timeout ([6dedb78](https://github.com/QbitArtifacts/backtestex/commit/6dedb78))
* **bitmex_testex:** update avg_order_price ([c4db4d0](https://github.com/QbitArtifacts/backtestex/commit/c4db4d0))
* **bridge_exchange:** removed comments ([3b7ad25](https://github.com/QbitArtifacts/backtestex/commit/3b7ad25))
* **dependencies:** added websocket dependency and updated the rest of ones ([f9d0d1a](https://github.com/QbitArtifacts/backtestex/commit/f9d0d1a))
* **plot_server:** delete comments ([cf26b48](https://github.com/QbitArtifacts/backtestex/commit/cf26b48))
* **plot_server:** minor renames ([de5eb21](https://github.com/QbitArtifacts/backtestex/commit/de5eb21))
* **runner:** fixed bug with prod configuration ([6c3d1dc](https://github.com/QbitArtifacts/backtestex/commit/6c3d1dc))
* **testex:** add symbol on Book events (ccxt compatibility) ([19d4c7f](https://github.com/QbitArtifacts/backtestex/commit/19d4c7f))
* **testing:** checked market order against status filled instead of status closed ([5f297e4](https://github.com/QbitArtifacts/backtestex/commit/5f297e4))
* dummy ([55e8abc](https://github.com/QbitArtifacts/backtestex/commit/55e8abc))
* makefike ([5902788](https://github.com/QbitArtifacts/backtestex/commit/5902788))
* separated build and coverage ([6822a96](https://github.com/QbitArtifacts/backtestex/commit/6822a96))
* tests ([652310a](https://github.com/QbitArtifacts/backtestex/commit/652310a))
* updated ci ([b94563a](https://github.com/QbitArtifacts/backtestex/commit/b94563a))
* updated ci ([ab315ca](https://github.com/QbitArtifacts/backtestex/commit/ab315ca))
* updated gh wf ([17b3567](https://github.com/QbitArtifacts/backtestex/commit/17b3567))
* updated makefile ([0f62d36](https://github.com/QbitArtifacts/backtestex/commit/0f62d36))
* updated makefile ([a883924](https://github.com/QbitArtifacts/backtestex/commit/a883924))
* updated reqs ([5ac7746](https://github.com/QbitArtifacts/backtestex/commit/5ac7746))
* **bitmex_backtest:** fix liquidation price formula ([fad7e19](https://github.com/QbitArtifacts/backtestex/commit/fad7e19))
* **bridge:** fixed sent information to plotter from bridge ([114adb7](https://github.com/QbitArtifacts/backtestex/commit/114adb7))
* **feeder:** fixed bug when period starts and ends at the same month ([0b4afdb](https://github.com/QbitArtifacts/backtestex/commit/0b4afdb))
* **funding:** renamed event funding_rate to funding ([379ff8a](https://github.com/QbitArtifacts/backtestex/commit/379ff8a))
* **gitignore:** ignored python cache files (*.pyc) ([0b69c30](https://github.com/QbitArtifacts/backtestex/commit/0b69c30))
* **PR:** fix for PR comments ([ecb3e37](https://github.com/QbitArtifacts/backtestex/commit/ecb3e37))
* **testex:** execute market orders match in time ([152bc88](https://github.com/QbitArtifacts/backtestex/commit/152bc88))
* **testex:** fixed tooltip info sent to plotter from testex ([1301d7e](https://github.com/QbitArtifacts/backtestex/commit/1301d7e))


### Features

* **bitmex_backtest:** implemented liquidation price ([9e579f6](https://github.com/QbitArtifacts/backtestex/commit/9e579f6))
* **BitmexBacktest:** implemented founding fees ([f6ce2fe](https://github.com/QbitArtifacts/backtestex/commit/f6ce2fe))
* **BitmexBacktest:** implemented markPrice fixes [#59](https://github.com/QbitArtifacts/backtestex/issues/59) ([d7419a9](https://github.com/QbitArtifacts/backtestex/commit/d7419a9))
* **ci:** added test and code coverage execution and github actions ([ccc3f13](https://github.com/QbitArtifacts/backtestex/commit/ccc3f13))
* **config:** added funding information to testex and bitmex_backtest ([d97dfe8](https://github.com/QbitArtifacts/backtestex/commit/d97dfe8))
* **config:** implemented outlier filter and added default values for fees ([20ada36](https://github.com/QbitArtifacts/backtestex/commit/20ada36))
* **founding_backtest_feeder:** implemented founding_backtest_feeder to send founding_rate events each time the founding_rate changes ([9bd0565](https://github.com/QbitArtifacts/backtestex/commit/9bd0565))
* **index:** added 5 min zoom, select zoom from-to(days), manual zoom and resize on charts division ([4061cb6](https://github.com/QbitArtifacts/backtestex/commit/4061cb6))
* **injector:** implemented default values ([1205e4c](https://github.com/QbitArtifacts/backtestex/commit/1205e4c)), closes [#51](https://github.com/QbitArtifacts/backtestex/issues/51)
* **kraken_feeder:** create kraken feeder class ([02f0f2a](https://github.com/QbitArtifacts/backtestex/commit/02f0f2a))
* **kraken_feeder:** filter orders by execution time (10 seg): ([95f158d](https://github.com/QbitArtifacts/backtestex/commit/95f158d))
* **kraken_feeder:** implemented events: ([703eefc](https://github.com/QbitArtifacts/backtestex/commit/703eefc))
* **kraken_feeder:** minor changes ([8745615](https://github.com/QbitArtifacts/backtestex/commit/8745615))
* **live_balance:** implemented filtered live chart (Real time balance) closes [#68](https://github.com/QbitArtifacts/backtestex/issues/68) ([25f8410](https://github.com/QbitArtifacts/backtestex/commit/25f8410))
* **live_plot:** run PlotServer in highstock_plotter.py on other process and added --live_plot option in CLI. fixes [#72](https://github.com/QbitArtifacts/backtestex/issues/72) ([1395f87](https://github.com/QbitArtifacts/backtestex/commit/1395f87))
* **plot_server:** created PlotServer class ([6aa9c63](https://github.com/QbitArtifacts/backtestex/commit/6aa9c63))
* **plot_server:** implementer websocket server to serve plot data to browser on real time ([cc6ca8b](https://github.com/QbitArtifacts/backtestex/commit/cc6ca8b))
* **plotter:** fixed imports in plotly plotter ([e692a80](https://github.com/QbitArtifacts/backtestex/commit/e692a80))
* **tests:** added balance and fees tests ([d14bca0](https://github.com/QbitArtifacts/backtestex/commit/d14bca0))
* **tests:** implemented first tests on tradingkit ([d4dbf08](https://github.com/QbitArtifacts/backtestex/commit/d4dbf08))



## 1.0.0 (2020-05-09)


### Bug Fixes

* **bitmex_feeder:** fixed order status, it must be lowercase ([e96f24b](https://github.com/QbitArtifacts/backtestex/commit/e96f24b))
* **bridge:** implemented is_inverse method to see if market liquidations are inversed (liquidates in base asset instead of quote asset) ([89b5688](https://github.com/QbitArtifacts/backtestex/commit/89b5688))
* **bridge:** removed error hidings in bridge exchange ([bf94db5](https://github.com/QbitArtifacts/backtestex/commit/bf94db5))
* **ccxt:** fixed bad secret name ([99a8951](https://github.com/QbitArtifacts/backtestex/commit/99a8951))
* **cli:** cli bugfix ([6b3bb63](https://github.com/QbitArtifacts/backtestex/commit/6b3bb63))
* **env:** fixed bug with loading environment ([8e2d207](https://github.com/QbitArtifacts/backtestex/commit/8e2d207))
* **fetcher:** fixed unchecked array access ([3f7e38f](https://github.com/QbitArtifacts/backtestex/commit/3f7e38f))
* **martingale:** fixed more bugs ([f9a0b9d](https://github.com/QbitArtifacts/backtestex/commit/f9a0b9d))
* **orders:** fixes [#9](https://github.com/QbitArtifacts/backtestex/issues/9) ([437d6ca](https://github.com/QbitArtifacts/backtestex/commit/437d6ca))
* **plotter:** changed order date parsing mode to iso ([a24fa92](https://github.com/QbitArtifacts/backtestex/commit/a24fa92))
* **plotter:** fixed automatic open browser when plot ([4bc4d7b](https://github.com/QbitArtifacts/backtestex/commit/4bc4d7b))
* **refactor:** finished refactor for martingale and fixed bug in injector with cache ([8b560ff](https://github.com/QbitArtifacts/backtestex/commit/8b560ff))
* **testex:** instant closed order when creating market orders ([524028d](https://github.com/QbitArtifacts/backtestex/commit/524028d)), closes [#45](https://github.com/QbitArtifacts/backtestex/issues/45)
* **websocket:** added monkey patch to throw exceptions when happens ([2f365af](https://github.com/QbitArtifacts/backtestex/commit/2f365af))
* changed feeder_listeners to feeder_adapters ([6717550](https://github.com/QbitArtifacts/backtestex/commit/6717550))


### Features

* **bridge:** added method to know which is the asset amount to create orders for an specific symbol ([cb32763](https://github.com/QbitArtifacts/backtestex/commit/cb32763))
* **cli:** added log verbosity control to cli ([b8cd933](https://github.com/QbitArtifacts/backtestex/commit/b8cd933))
* **cli:** implemented cli ([fe9c94c](https://github.com/QbitArtifacts/backtestex/commit/fe9c94c)), closes [#16](https://github.com/QbitArtifacts/backtestex/issues/16)
* **cli:** refactored feeders and fetchers ([a1269f0](https://github.com/QbitArtifacts/backtestex/commit/a1269f0))
* **config:** allowed calls in config definition ([f08cb55](https://github.com/QbitArtifacts/backtestex/commit/f08cb55))
* **config:** changed config to strategies and updated cli ([120efaa](https://github.com/QbitArtifacts/backtestex/commit/120efaa)), closes [#41](https://github.com/QbitArtifacts/backtestex/issues/41)
* **config:** implemented adapters to allow adapte trades ([334fe96](https://github.com/QbitArtifacts/backtestex/commit/334fe96))
* **config:** loading environment env files ([639d4aa](https://github.com/QbitArtifacts/backtestex/commit/639d4aa))
* **dep.injection:** implemented injector to load from config.json easier ([d0b572b](https://github.com/QbitArtifacts/backtestex/commit/d0b572b))
* **env:** fixes [#38](https://github.com/QbitArtifacts/backtestex/issues/38) ([b6f0821](https://github.com/QbitArtifacts/backtestex/commit/b6f0821))
* **gitignore:** added var/cache to gitignore ([fc3cc24](https://github.com/QbitArtifacts/backtestex/commit/fc3cc24))
* **importer:** added importer to cli and refactor ([4d32e3a](https://github.com/QbitArtifacts/backtestex/commit/4d32e3a))
* **injector:** new config injector operative ([674058a](https://github.com/QbitArtifacts/backtestex/commit/674058a))
* **installer:** implemented installer ([98204f3](https://github.com/QbitArtifacts/backtestex/commit/98204f3)), closes [#3](https://github.com/QbitArtifacts/backtestex/issues/3)
* **logs:** added deep level to martingale strategy warnings ([cd93942](https://github.com/QbitArtifacts/backtestex/commit/cd93942))
* **martingale:** fixed bugs in martingale with risk checks enabled ([f7bebc4](https://github.com/QbitArtifacts/backtestex/commit/f7bebc4))
* **martingale:** refactored and improved martingale ([f9f2623](https://github.com/QbitArtifacts/backtestex/commit/f9f2623))
* **martingale:** tunning parameters ([8ce66b3](https://github.com/QbitArtifacts/backtestex/commit/8ce66b3))
* **plotter:** stopping server after 3 seconds of serve ([ee60016](https://github.com/QbitArtifacts/backtestex/commit/ee60016))
* **plotting:** plotted equity ([9c7b119](https://github.com/QbitArtifacts/backtestex/commit/9c7b119))
* **refactor:** added super-package btx ([8682a91](https://github.com/QbitArtifacts/backtestex/commit/8682a91))
* **refactor:** another big refactor in cli and all package imports ([3d9a21a](https://github.com/QbitArtifacts/backtestex/commit/3d9a21a))
* **refactor:** implemented auto test and refactored loaders ([0dd3240](https://github.com/QbitArtifacts/backtestex/commit/0dd3240))
* (double martingale) changed logging to debug ([6af2fd4](https://github.com/QbitArtifacts/backtestex/commit/6af2fd4))
* **refactor:** refactored plotters ([cbb6335](https://github.com/QbitArtifacts/backtestex/commit/cbb6335))
* **refactor:** refactored plotters ([2f38acb](https://github.com/QbitArtifacts/backtestex/commit/2f38acb))
* big refactor to allow strategies work with both backtest and real envs ([cae5a48](https://github.com/QbitArtifacts/backtestex/commit/cae5a48))
