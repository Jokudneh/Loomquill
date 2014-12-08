.PHONY: test
test:
	find . -maxdepth 1 -type d | grep 'loomquill-' | xargs -L1 pytest

.PHONY: build_all_plugins
build_all_plugins:
	./run_all_plugins.sh python setup.py sdist bdist_wheel

.PHONY: publish_all_plugins
