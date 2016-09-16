PROJECT_NAME = manopozicija


.PHONY: all
all: bin/django

.PHONY: help
help:
	@echo 'make ubuntu       install the necessary system packages (requires sudo)'
	@echo 'make dbsuperuser  create postgresql super user'
	@echo 'make db           create postgresql database'
	@echo 'make migrate      run database migrations'
	@echo 'make adminuser    create django admin user'
	@echo 'make              set up the development environment'
	@echo 'make run          start the web server'
	@echo 'make test         run project tests'
	@echo 'make tags         build ctags file'
	@echo 'make clean        clean whole environment'
	@echo 'make cleanpyc     clean all *.pyc files'

.PHONY: ubuntu
ubuntu:
	sudo apt-get update
	sudo apt-get -y build-dep python-psycopg2 python-imaging python-lxml
	sudo apt-get -y install build-essential python-dev exuberant-ctags postgresql postgresql-contrib

.PHONY: migrate
migrate: bin/django ; bin/django migrate

.PHONY: run
run: bin/django ; bin/django runserver

.PHONY: tags
tags: bin/django ; bin/ctags -v --tag-relative

.PHONY: test
test: bin/django
	bin/py.test \
	  -vvra \
	  --tb=native \
	  --flake8 \
	  --doctest-modules \
	  --cov $(PROJECT_NAME) \
	  --cov-report term-missing \
	  $(PROJECT_NAME)

.PHONY: cleanpyc
cleanpyc: ; find -iname '*.pyc' -delete

.PHONY: clean
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

.PHONY: dbsuperuser
dbsuperuser:
	sudo --user=postgres createuser --superuser $(USER)

.PHONY: db
db:
	createdb \
	  --encoding=UTF-8 \
	  --lc-collate=C.UTF-8 \
	  --lc-ctype=C.UTF-8 \
	  --template=template0 \
	  --owner=$(USER) \
	  $(PROJECT_NAME)

.PHONY: adminuser
adminuser:
	bin/django createsuperuser --username admin --email admin@localhost.local

buildout.cfg: ; ./scripts/genconfig.py config/env/development.cfg

bin/pip:
	virtualenv --no-site-packages --python=python3.5 .
	bin/pip install --upgrade pip==8.1.1 pip-tools==1.6.5 wheel==0.29.0

bin/buildout: bin/pip requirements.txt ; bin/pip install -e . -r requirements.txt && touch -c bin/buildout

var/www/static var/www/media: ; mkdir -p $@

bin/django: \
  bin/buildout \
  buildout.cfg \
  $(wildcard config/*.cfg) \
  $(wildcard config/env/*.cfg) \
  var/www/static \
  var/www/media
	bin/buildout && touch -c bin/django
