.PHONY: all
all: settings.json var/www/static var/www/media


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
	@echo 'make build        build project wheels'
	@echo 'make deploy       deploy project to prod server'
	@echo 'make tags         build ctags file'
	@echo 'make clean        clean whole environment'
	@echo 'make cleanpyc     clean all *.pyc files'


.PHONY: ubuntu
ubuntu:
	sudo apt-get update
	sudo apt-get -y build-dep python-psycopg2 python-imaging python-lxml
	sudo apt-get -y install build-essential python-dev exuberant-ctags postgresql postgresql-contrib


.PHONY: migrate
migrate: all ; bin/django migrate


.PHONY: run
run: all ; bin/django runserver


.PHONY: tags
tags: all ; bin/ctags -v --tag-relative


.PHONY: test
test: all
	bin/py.test \
	  -vvra \
	  --tb=native \
	  --flake8 \
	  --doctest-modules \
	  --cov manopozicija \
	  --cov-report term-missing \
	  manopozicija


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
	  var/www/static/ \
	  wheels


.PHONY: dbsuperuser
dbsuperuser:
	sudo --user=postgres createuser --superuser $(USER)


.PHONY: db
db:
	createdb \
	  --encoding=UTF-8 \
	  --lc-collate=C \
	  --lc-ctype=C \
	  --template=template0 \
	  --owner=$(USER) \
	  manopozicija


.PHONY: testdb
testdb:
	createdb \
	  --encoding=UTF-8 \
	  --lc-collate=C \
	  --lc-ctype=C \
	  --template=template0 \
	  --owner=$(USER) \
	  test_manopozicija


.PHONY: adminuser
adminuser:
	bin/django createsuperuser --username admin --email admin@localhost.local


.PHONY: requirements
requirements: bin/pip requirements.txt requirements-dev.txt ;


.PHONY: build
build: bin/pip
	rm -rf wheels
	mkdir -p wheels
	bin/pip wheel -w wheels -r requirements.txt
	bin/pip wheel -w wheels src/django-autoslug
	bin/pip wheel -w wheels --no-deps .


.PHONY: deploy
deploy: bin/pip
	cd deploy && ansible-playbook --inventory=inventory.cfg --ask-vault-pass playbook.yml


bin/pip:
	python3 -m venv .
	bin/pip install --upgrade pip setuptools pip-tools wheel

settings.json: bin/initsettings
	bin/initsettings
	touch -c settings.json

requirements.txt: requirements.in
	bin/pip-compile --no-index --output-file requirements.txt requirements.in

requirements-dev.txt: requirements.in requirements-dev.in
	bin/pip-compile --no-index --output-file requirements-dev.txt requirements.in requirements-dev.in

bin/initsettings: bin/pip requirements.txt requirements-dev.txt
	bin/pip install -r requirements-dev.txt -e .

var/www/static: ; mkdir -p $@

var/www/media: ; mkdir -p $@
