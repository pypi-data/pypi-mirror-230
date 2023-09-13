.PHONY: build test clean

clean:
	rm -rf build
	rm -rf dist
	rm -rf hcs_cli.egg-info
	find . -name .DS_Store -delete
	find . -name "*.pyc" -delete
	
lint:
	python3 -m black .	
sca:
	mypy vhcs
build:
	export SCM_REV=$(shell git rev-parse --short HEAD); \
	python3 setup.py sdist bdist_wheel

update:
	pipreqs . --force

buildrelease:
	python3 setup.py sdist bdist_wheel

uninstall:
	pip3 uninstall -y hcs-cli

devinstall:
	pip3 uninstall -y hcs-cli
	export SCM_REV=$(shell git rev-parse --short HEAD); \
	pip3 install -e .

dev: clean uninstall lint build devinstall

SHELL := /bin/bash
test:
	python3 -m unittest discover -v --failfast ./tests

testinstall:
	docker run --rm python /bin/bash -c "pip3 install hcs-cli && hcs profile"

publish:
	twine upload --repository hcs-cli dist/*

install:
	pip3 install hcs-cli

wait:
	sleep 30

release: lint test clean buildrelease publish testinstall


