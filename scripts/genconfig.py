#!/usr/bin/env python3

import argparse
import configparser
import random
import os.path
import string


def get_random_string(length=50, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for i in range(length))


def update_config(config, sections, overwrite=False):
    for section, values in sections:
        if not config.has_section(section):
            config.add_section(section)

        for key, value in values:
            if overwrite or key not in config[section]:
                config[section][key] = value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('extends', nargs='?', default='config/env/development.cfg')
    parser.add_argument('-c', '--config', default='buildout.cfg')
    parser.add_argument('-o', '--overwrite', action='store_true', default=False)
    args = parser.parse_args()

    if not os.path.exists(args.extends):
        raise Exception('File %s does not exist.' % args.extends)

    config = configparser.ConfigParser()

    if os.path.exists(args.config):
        config.read(args.config)

    update_config(config, (
        ('buildout',  (
            ('extends', args.extends),
        )),
        ('settings', (
            ('secret_key', get_random_string()),
        )),
    ), args.overwrite)

    with open(args.config, 'w') as f:
        config.write(f)


if __name__ == '__main__':
    main()
