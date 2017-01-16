'''
Created on 17 Dec 2016

@author: Henk Kraal
'''
import argparse
import subprocess
import shlex
import logging

from .plugins import JsonParser, MySQLParser
import os
import sys


def ssh_connect(host, args):
    logging.debug('args = {0}'.format(args))

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
    try:
        return hosts[int(option)-1]
    except ValueError as ex:
        return

def get_answer(text):   # pragma: nocover
    return input(text)


def get_log_level():
    if os.getenv('SSHT_DEBUG', None):
        return logging.DEBUG
    return logging.WARNING

def main():     # pragma: nocover
    try:
        logging.basicConfig(level=get_log_level())
    
        parser = argparse.ArgumentParser()
        parser.add_argument("name", help="name of the host to connect to")
        args, unknown = parser.parse_known_args()
    
        home_dir = os.path.expanduser('~')
        jsonparser = JsonParser(os.path.join(home_dir, '.ssht'))
        mysqlparser = MySQLParser(os.path.join(home_dir, '.ssht'))
        hosts = jsonparser.search(args.name) + mysqlparser.search(args.name)
        logging.info(hosts)
    
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