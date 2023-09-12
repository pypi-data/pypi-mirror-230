define HELP_MSG
Makefile for python project
Avaliable commands:
venv - creates python virtual environment
install - install this package and its dependencies to venv
build - build package and tar it
upload_to_pypi - build and upload to pypi repository
clean - clean all intermediate build files as well as dist tar files
autopep8 - run autopep8 linter and change files
help - prints this message
endef

venv:
	test -d venv || python3.10 -m venv venv

run: venv
	@echo "This is import only package, can't run"

install: venv
	. venv/bin/activate && python3.10 -m pip install -e .

build: install
	. venv/bin/activate && pip install build && python3.10 -m build

upload_to_pypi: clean build
	. venv/bin/activate && pip install twine && python3.10 -m twine upload --repository pypi dist/*

autopep8: install
	. venv/bin/activate && autopep8 --in-place --exclude "./venv/**" --recursive .

clean:
	rm -rf venv dist *.egg-info
	find -iname "*.pyc" -delete

export HELP_MSG
help:
	@echo "$$HELP_MSG"

.PHONY: venv install clean run build upload_to_pypi autopep8 help