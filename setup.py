from setuptools import setup, find_packages

setup(
    name='manopozicija-lt',
    version='0.1a1',
    license='AGPLv3+',
    packages=find_packages(),
    install_requires=[],  # use pip-tools and requirements.in
    classifiers=[
        'Development Status :: 1 - Planning',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
    ],
    entry_points={
        'console_scripts': [
            'prototype = manopozicija.prototype.main:main',
        ],
    },
)
