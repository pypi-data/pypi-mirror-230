.PHONY: install
install:
	pip3 install . --upgrade

.PHONY: build
build:
	rm -rf dist
	python3 setup.py sdist bdist_wheel

.PHONY: upload
upload: build
	python3 -m twine upload dist/*

.PHONY: unittest
unittest:
	PYTHONPATH=$(PYTHONPATH):d64 python3 -m unittest discover -s test -v

.PHONY: lint
lint:
	flake8 d64 test
