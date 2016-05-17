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

bin/pip-compile: bin/pip ; bin/pip install --upgrade pip==8.1.1 pip-tools==1.6.5 && touch -c bin/pip-compile

requirements.txt: bin/pip-compile requirements.in ; pip-compile

bin/buildout: bin/pip requirements.txt ; bin/pip install -r requirements.txt && touch -c bin/buildout

var/www/static var/www/media: ; mkdir -p $@

bin/django: \
  bin/buildout \
  buildout.cfg \
  $(wildcard config/*.cfg) \
  $(wildcard config/env/*.cfg) \
  var/www/static \
  var/www/media
	bin/buildout && touch -c bin/django

cleanpyc: ; find -iname '*.pyc' -delete

clean: cleanpyc
	rm -rf \
	  *.egg-info \
	  .installed.cfg \
	  bin \
	  develop-eggs \
	  include \
	  lib \
	  parts \
	  settings.json \
	  var/www/static/


.PHONY: all help run tags clean cleanpyc
