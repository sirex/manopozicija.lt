from manopozicija.utils.scripting import SETTINGS_FILENAME, get_venv_dir, get_settings


def main():
    venv_dir = get_venv_dir()
    get_settings(venv_dir)
    print("Settings file:", venv_dir / SETTINGS_FILENAME)
