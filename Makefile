# build file - all commands necessary to go from source to release.

# -----------------------------------------------------------------------------
# BUILD
# -----------------------------------------------------------------------------
.PHONY: all
all: lint build

.PHONY: lint
lint:
	@docker-compose run bubblert flake8
	@echo All lint checks passed.

.PHONY: build
build:
	@docker-compose build

.PHONY: force_build
force_build:
	@docker-compose build --force-rm --no-cache --pull

# -----------------------------------------------------------------------------
# DEVELOPMENT
# -----------------------------------------------------------------------------
.PHONY: start
start:
	@docker-compose up -d bubblert

.PHONY: stop
stop:
	@docker-compose kill bubblert
	@docker-compose rm -f bubblert

.PHONY: restart
restart: stop start

.PHONY: teardown
teardown:
	@docker-compose down

.PHONY: logs
logs:
	@docker-compose logs -f --tail 20

.PHONY: bootstrap
bootstrap: copy_env

.PHONY: copy_env
copy_env:
	@cp .env.example .env

.PHONY: clean
clean:
	@rm -f .version
	@rm -rf .cache
	@find . -iname __pycache__ | xargs rm -rf
	@find . -iname "*.pyc" | xargs rm -f
