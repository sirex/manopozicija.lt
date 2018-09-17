import json
import os
import pathlib
import random
import string
import sys


SETTINGS_FILENAME = 'settings.json'


def get_random_string(length=50, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for i in range(length))


def get_default_settings(venv_dir):
    return {
        'project_dir': str(venv_dir),
        'settings': 'manopozicija.settings.development',
        'secret_key': get_random_string(),
    }


def get_venv_dir():
    venv_dir = pathlib.Path(sys.executable).resolve().parents[1]
    settings_file = venv_dir / SETTINGS_FILENAME
    if settings_file.exists():
        return venv_dir

    else:
        return pathlib.Path().resolve()


def get_settings(venv_dir):
    settings_file = venv_dir / SETTINGS_FILENAME
    if not settings_file.exists():
        settings = get_default_settings(venv_dir)
        with settings_file.open('w') as f:
            json.dump(settings, f)
    else:
        with settings_file.open() as f:
            settings = json.load(f)
    return settings


def set_up_environment():
    venv_dir = get_venv_dir()
    settings = get_settings(venv_dir)
    os.environ.setdefault('MANOPOZICIJA_DIR', str(venv_dir))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings.get('settings', 'manopozicija.settings.development'))
