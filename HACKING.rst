How to get prod db to development
=================================

::

  ssh manopozicija 'sudo -u postgres pg_dump --no-owner manopozicija > /tmp/db-dump-manopozicija-$(date +"%Y%m%d").sql'
  scp manopozicija.lt:/tmp/db-dump-manopozicija-$(date +"%Y%m%d").sql ../dumps
  psql manopozicija < ../dumps/db-dump-manopozicija-$(date +"%Y%m%d").sql
  rm -r var
  scp -r manopozicija.lt:/opt/manopozicija.lt/app/var/ var
