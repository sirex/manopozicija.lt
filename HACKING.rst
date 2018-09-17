.. default-role:: literal

Configuration
=============

Project is configured via `settings.json` file, which is then loaded into one
of `manopozicija.settings.*` files. `settings.json` is not kept under version
control and it has environment specific settings.


Deployment
==========

In order to deploy project to production you need to run::

  make build
  make deploy

`make build` build wheel packages and puts them into `wheels` directory, then
`make deploy` will upload those wheels to the server and installs them to the
virtualenv.

Wheels must be build from a Linux machine, since production is deployed on
Linux server.

Probably it would be good idea to have docker containers for building wheels,
but that is not implemented yet.


How to get prod db to development
=================================

::

  ssh manopozicija 'sudo -u postgres pg_dump --no-owner manopozicija > /tmp/db-dump-manopozicija-$(date +"%Y%m%d").sql'
  scp manopozicija.lt:/tmp/db-dump-manopozicija-$(date +"%Y%m%d").sql ../dumps
  psql manopozicija < ../dumps/db-dump-manopozicija-$(date +"%Y%m%d").sql
  rm -r var
  scp -r manopozicija.lt:/opt/manopozicija.lt/app/var/ var
