'''
Created on 17 Dec 2016

@author: Henk Kraal
'''
import argparse
import subprocess
import shlex
import logging

from .plugins import JsonParser, MySQLParser


def ssh_connect(host, args):
    logging.debug('args = {0}'.format(args))
    logging.info('Connecting to "{0}"'.format(host))

    # Connect to host IPv4
    if hasattr(host, 'ipv4') and '-4' in args:
        ssh_cmds = shlex.split('ssh {0}'.format(host.ipv4))
        args.remove('-4')
    elif hasattr(host, 'ipv6') and '-6' in args:
        ssh_cmds = shlex.split('ssh {0}'.format(host.ipv6))
        args.remove('-6')
    else:
        ssh_cmds = shlex.split('ssh {0}'.format(host.hostname))
    logging.debug('ssh_cmds = {0}'.format(ssh_cmds))

    # Connect to host port
    if hasattr(host, 'port') and host.port is not None and '-p' not in args:
        ssh_cmds += shlex.split('-p {0}'.format(host.port))

    # Connect as user
    if hasattr(host, 'user') and host.user is not None and '-l' not in args:
        ssh_cmds += shlex.split('-l {0}'.format(host.user))

    logging.debug('ssh_cmds = {0}'.format(ssh_cmds + args))
    subprocess.call(ssh_cmds + args)


def select_host(hosts):
    for idx, host in enumerate(hosts):
        if hasattr(host, 'user') and host.user is not None:
            print('{0}) {1}@{2}'.format(idx + 1, host.user, host.hostname))
        else:
            print('{0}) {1}'.format(idx + 1, host.hostname))
    option = get_answer('Connect to: ')

    return hosts[int(option)-1]


def get_answer(text):   # pragma: nocover
    return input(text)


def main():     # pragma: nocover
    logging.basicConfig(level=logging.WARNING)

    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="name of the host to connect to")
    args, unknown = parser.parse_known_args()

    jsonparser = JsonParser('/Users/henk/.ssht')
    mysqlparser = MySQLParser('/Users/henk/.ssht')
    hosts = jsonparser.search(args.name) + mysqlparser.search(args.name)
    logging.info(hosts)

    if len(hosts) == 1:
        host = hosts[0]
    else:
        host = select_host(hosts)

    if host is None:
        raise Exception('No host set')

    ssh_connect(host, unknown)
