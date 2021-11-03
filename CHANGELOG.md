# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

### [1.6.8](https://github.com/logictraders/tradingkit/compare/v1.6.7...v1.6.8) (2021-11-03)


### Bug Fixes

* **bitmex:** updated bitmex websocket endpoint (https://blog.bitmex.com/api_announcement/change-of-websocket-endpoint/) ([d87d3fc](https://github.com/logictraders/tradingkit/commit/d87d3fc))



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
