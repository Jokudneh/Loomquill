export REPOSITORY=loomquill

PIP_COMPILE = pip-compile --upgrade --verbose --resolver=backtracking
MOCK_LOOMQUILL_REPO=tests/loomquill/integration/remote/mock_loomquill_repo/workflows
PYTEST_OPTS ?= -n auto --dist=loadfile
PYTEST_AND_OPTS = pytest ${PYTEST_OPTS}
PYTEST = pytest

.SILENT: help
.PHONY: help
help:
	echo Available recipes:
	cat $(MAKEFILE_LIST) | grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' | awk 'BEGIN { FS = ":.*?## " } { cnt++; a[cnt] = $$1; b[cnt] = $$2; if (length($$1) > max) max = length($$1) } END { for (i = 1; i <= cnt; i++) printf "  $(shell tput setaf 6)%-*s$(shell tput setaf 0) %s\n", max, a[i], b[i] }'
	tput sgr0

.PHONY: install-piptools
install-piptools:
	# pip 22.1 broke pip-tools: https://github.com/jazzband/pip-tools/issues/1617
	python -m pip install -U pip-tools setuptools wheel "pip>=22.0.3,!=22.1"

.PHONY: update_boilerplate
update_boilerplate:
	@curl https://raw.githubusercontent.com/jokudneh/boilerplate/master/boilerplate/update.sh -o boilerplate/update.sh
	@boilerplate/update.sh

.PHONY: setup
setup: install-piptools ## Install requirements
	pip install -r dev-requirements.in

