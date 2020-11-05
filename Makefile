
all: build test coverage

version:
	docker run --rm -it -v $(PWD):/app detouched/standard-version
build:
	docker build . -f docker/prod/Dockerfile -t logictraders/tradingkit

run:
	docker run -v $(PWD):/strategy logictraders/tradingkit run /strategy

dev:
	docker build . -f docker/dev/Dockerfile -t logictraders/tradingkit:dev

shell: dev
	docker run -it -v $(PWD):/tradingkit logictraders/tradingkit:dev bash

test: dev
	docker run -v $(PWD):/tradingkit logictraders/tradingkit:dev python3 -m unittest

coverage: dev
	docker run -v $(PWD):/tradingkit logictraders/tradingkit:dev bash -c "coverage3 run --source=src -m unittest && coverage3 report"
