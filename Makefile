# Copyright 2018-2019 Jiří Janoušek <janousek.jiri@gmail.com>
# License: BSD-2-Clause, see file LICENSE at the project root.

.PHONY: help setup lint clean distclean push

MODULE = fxwebgen
VENV_NAME ?= venv
VENV_ACTIVATE = . $(VENV_NAME)/bin/activate
PYTHON = ${VENV_NAME}/bin/python3

help:
	@echo "Targets:"
	@echo "- setup: Set up python3 virtual environment."
	@echo "- lint: Run flake8, mypy and pylint."
	@echo "- tox: Run checks and tests with tox."
	@echo "- clean: Clean built files and cache."
	@echo "- distclean: Clean built files, cache, tox, and venv."
	@echo "- push: Push the current git branch."

setup: $(VENV_NAME)/activate

$(VENV_NAME)/activate: requirements.txt requirements-devel.txt
	test -d $(VENV_NAME) || python3 -m venv $(VENV_NAME)
	${PYTHON} -m pip install --upgrade pip
	${PYTHON} -m pip install --upgrade -r requirements.txt
	${PYTHON} -m pip install --upgrade -r requirements-devel.txt
	touch $(VENV_NAME)/activate

lint: setup
	${PYTHON} -m flake8 $(MODULE)
	MYPYPATH=stubs ${PYTHON} -m mypy $(MODULE)
	${PYTHON} -m pylint --rcfile .pylintrc $(MODULE)

tox: setup
	${PYTHON} -m tox

clean:
	find . -name __pycache__ -exec rm -rf {} \+
	rm -rf .mypy_cache

distclean: clean
	rm -rf .tox $(VENV_NAME)

push: lint
	git push && git push --tags

