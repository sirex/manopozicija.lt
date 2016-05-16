all: bin/django

help:
	@echo 'make ubuntu     install the necessary system packages (requires sudo)'
	@echo 'make            set up the development environment'
	@echo 'make run        start the web server'
	@echo 'make tags       build ctags file'
	@echo 'make clean      clean whole environment'
	@echo 'make cleanpyc   clean all *.pyc files'

ubuntu:
	sudo apt-get update
	sudo apt-get -y build-dep python-psycopg2
	sudo apt-get -y install build-essential python-dev exuberant-ctags

run: bin/django ; bin/django runserver

tags: bin/django ; bin/ctags -v --tag-relative


buildout.cfg: ; ./scripts/genconfig.py config/env/development.cfg

bin/pip: ; virtualenv --no-site-packages --python=python3.5 .

bin/buildout: bin/pip ; $< install --upgrade setuptools zc.buildout==2.3.1

mkdirs: var/www/static var/www/media

var/www/static var/www/media: ; mkdir -p $@

bin/django: bin/buildout buildout.cfg $(wildcard config/*.cfg) $(wildcard config/env/*.cfg) mkdirs ; $<

cleanpyc:
	find -iname '*.pyc' -delete

clean: cleanpyc
	rm -rf bin develop-eggs include .installed.cfg lib *.egg-info parts settings.json var/www/static/


.PHONY: all help run mkdirs tags clean cleanpyc
