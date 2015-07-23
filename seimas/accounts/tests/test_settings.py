import django_webtest

import django.contrib.auth.models as auth_models


class SettingsTests(django_webtest.WebTest):
    def setUp(self):
        super().setUp()
        auth_models.User.objects.create_user('u1')

    def test_settings(self):
        resp = self.app.get('/accounts/settings/', user='u1')
        resp.form['first_name'] = 'My'
        resp.form['last_name'] = 'Name'
        resp.form['email'] = ''
        resp = resp.form.submit()
        self.assertEqual(resp.status_int, 302)
        self.assertEqual(list(auth_models.User.objects.values_list('first_name', 'last_name', 'email')), [
            ('My', 'Name', ''),
        ])
