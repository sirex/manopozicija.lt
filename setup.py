from setuptools import setup, find_packages


def read_requirements(filename):
    with open(filename) as f:
        for line in f:
            line = line.strip()

            # Detect editable dependencies.
            if line.startswith('-e'):
                if '#egg=' not in line:
                    raise Exception("Editable deps must have #egg=<name> fragment.")
                line = line.split('#egg=')[1]

            # Strip comments
            if '#' in line:
                line = line.rsplit('#', 1)[0]

            if line:
                yield line


setup(
    name='manopozicija-lt',
    version='0.1a1',
    license='AGPLv3+',
    packages=find_packages(),
    include_package_data=True,
    install_requires=list(read_requirements('requirements.in')),
    entry_points={
        'console_scripts': [
            'manage = manopozicija.scripts.manage:main',
        ],
    },
    scripts=[
        'manopozicija/scripts/wsgi.py',
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
    ],
)
