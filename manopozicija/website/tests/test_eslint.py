import os.path
import subprocess

import pytest


def get_eslint_path():
    for path in os.environ['PATH'].split(':'):
        path = os.path.join(path, 'eslint')
        if os.path.exists(path):
            return path


@pytest.mark.skipif(get_eslint_path() is None, reason="eslint is not installed")
def test_eslint():
    assert subprocess.call([get_eslint_path(), 'manopozicija']) == 0
