.PHONY: test
test:
	find . -maxdepth 1 -type d | grep 'loomquill-' | xargs -L1 pytest

.PHONY: build_all_plugins
build_all_plugins:
	./run_all_plugins.sh python setup.py sdist bdist_wheel

.PHONY: publish_all_plugins
publish_all_plugins:
	twine upload --verbose --skip-existing */dist/*
	# We upload community plugins from a separate sub-directory called `community`.
	# Check https://github.com/jokudneh/loomquill/pull/5610 for more details about.
	twine upload --verbose --skip-existing community/*/dist/*

.PHONY: all_requirements
all_requirements:
	./run_all_plugins.sh pip-compile requirements.in --upgrade --verbose

PLACEHOLDER := __version__ = \"0.0.0+develop\"
