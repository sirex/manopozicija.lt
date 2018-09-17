import json
import os
import pathlib
import random
import string
import sys


def get_random_string(length=50, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for i in range(length))


def set_up_environment():
    venv_dir = pathlib.Path(sys.executable).resolve().parents[1]
    settings_file = venv_dir / 'settings.json'
    if not settings_file.exists():
        settings_file = pathlib.Path().resolve() / 'settings.json'
    if not settings_file.exists():
        settings = {
            'project_dir': str(venv_dir),
            'settings': 'manopozicija.settings.development',
            'secret_key': get_random_string(),
        }
        with settings_file.open('w') as f:
            json.dump(settings, f)
    else:
        with settings_file.open() as f:
            settings = json.load(f)

    os.environ.setdefault('MANOPOZICIJA_DIR', str(venv_dir))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings.get('settings', 'manopozicija.settings.development'))
