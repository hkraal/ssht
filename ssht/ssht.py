import argparse
import json
import logging
import os
import shlex
import subprocess
import sys
from importlib import import_module


def get_log_level():
    if os.getenv('SSHT_DEBUG', None):
        return logging.DEBUG
    return logging.WARNING


logging.basicConfig(level=get_log_level())
logger = logging.getLogger("ssht")


def ssh_connect(host, args):
    logger.debug('args = {0}'.format(args))

    # Connect to IPv6 if forced
    if hasattr(host, 'ipv6') and host.ipv6 and '-6' in args:
        ssh_cmds = shlex.split('ssh {0}'.format(host.ipv6))
        print('Connecting to "{0}" ({1})'.format(host.hostname, host.ipv6))
    # Connect to IPv4 if specified
    elif hasattr(host, 'ipv4') and host.ipv4:
        ssh_cmds = shlex.split('ssh {0}'.format(host.ipv4))
        print('Connecting to "{0}" ({1})'.format(host.hostname, host.ipv4))
    # Connect on host name
    else:
        ssh_cmds = shlex.split('ssh {0}'.format(host.hostname))
        print('Connecting to "{0}"'.format(host.hostname))
    logger.debug('ssh_cmds = {0}'.format(ssh_cmds))

    # Connect to host port
    if hasattr(host, 'port') and host.port is not None and '-p' not in args:
        ssh_cmds += shlex.split('-p {0}'.format(host.port))

    # Connect as user
    if hasattr(host, 'user') and host.user is not None and '-l' not in args:
        ssh_cmds += shlex.split('-l {0}'.format(host.user))

    logger.debug('ssh_cmds = {0}'.format(ssh_cmds + args))
    subprocess.call(ssh_cmds + args)


def select_host(hosts):
    for idx, host in enumerate(hosts):
        if hasattr(host, 'user') and host.user is not None:
            print('{0}) {1}@{2}'.format(idx + 1, host.user, host.hostname))
        else:
            print('{0}) {1}'.format(idx + 1, host.hostname))
    option = get_answer('Connect to: ')
    try:
        return hosts[int(option) - 1]
    except ValueError as ex:
        return


def get_answer(text):  # pragma: nocover
    try:
        return input(text)
    except SyntaxError:
        return ''


def main():  # pragma: nocover
    try:
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument("name", help="name of the host to connect to")
        args, unknown = arg_parser.parse_known_args()

        home_dir = os.path.expanduser('~')
        config_path = os.path.join(home_dir, '.ssht', 'config.json')

        # Read generic config file.
        config = {}
        try:
            logger.debug(f"Reading config {config_path}")
            with open(config_path, 'r') as fh:
                config = json.loads(fh.read())
        except FileNotFoundError as e:
            logger.debug(f'Config file {config_path} is missing')
        except ValueError as ex:
            logger.debug(f'Config file {config_path} contains invalid JSON')

        # Define default parsers for backwards compatibility.
        parsers = [
            "ssht.plugins.JsonParser",
            "ssht.plugins.MySQLParser",
            "ssht.plugins.APIParser",
        ]
        # Use configured parsers if defined.
        if 'parsers' in config:
            parsers = config['parsers']
            logger.debug(f"Loading parsers {parsers}")

        hosts = []
        for module_path in parsers:
            # Split module and class name.
            _module = '.'.join(module_path.split('.')[:-1])
            _class = module_path.split('.')[-1:][0]

            # Dynamically import and execute the parsers.
            parser = getattr(import_module(_module), _class)
            p = parser(os.path.join(home_dir, '.ssht'))
            hosts.extend(p.search(args.name))

        logger.info(hosts)

        host = None
        if len(hosts) == 1:
            host = hosts[0]
        elif len(hosts) > 1:
            host = select_host(hosts)

        if host is None:
            print('No host, exiting.')
            sys.exit(0)

        ssh_connect(host, unknown)
    except KeyboardInterrupt as ex:
        print()
        sys.exit(0)


if __name__ == '__main__':
    main()
