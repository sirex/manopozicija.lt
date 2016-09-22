import pytest

from django_webtest import DjangoTestApp, WebTestMixin


@pytest.fixture
def App(request, db):
    mixin = WebTestMixin()
    mixin._patch_settings()
    mixin._disable_csrf_checks()
    request.addfinalizer(mixin._unpatch_settings)

    def factory():
        return DjangoTestApp(extra_environ=mixin.extra_environ)

    return factory


@pytest.fixture
def app(App):
    return App()
