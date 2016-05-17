import os.path
import subprocess

import pytest


def get_eslint_path():
    paths = [
        '/usr/local/bin/eslint',
        '/usr/bin/eslint',
    ]
    for path in paths:
        if os.path.exists(path):
            return path


@pytest.mark.skipif(get_eslint_path() is None, reason="eslint is not installed")
def test_eslint():
    assert subprocess.call([get_eslint_path(), 'seimas']) == 0
