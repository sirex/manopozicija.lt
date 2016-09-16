2016-09-16
==========

- django-autocomplete-light was upgraded to 3.1.8, where issue with html
  rendering was fixed.


2016-07-26
==========

- django-autocomplete-light has not yet released html support for items, so for
  now this should be done manually.

  Open
  lib/python3.5/site-packages/dal_select2/static/autocomplete_light/select2.js
  and add two changes from here:

  https://github.com/yourlabs/django-autocomplete-light/commit/2898823f97762bba43182c185ff9d39c4307b0aa
