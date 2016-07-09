import pytest

from django_webtest import DjangoTestApp, WebTestMixin


@pytest.fixture
def app(request, db):
    mixin = WebTestMixin()
    mixin._patch_settings()
    mixin._disable_csrf_checks()
    request.addfinalizer(mixin._unpatch_settings)
    return DjangoTestApp(extra_environ=mixin.extra_environ)
