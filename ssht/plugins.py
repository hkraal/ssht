import fnmatch
import json
import logging
import os

import mysql.connector
import requests

logger = logging.getLogger(__name__)


class Host(object):
    def __init__(self, hostname, port=None, ipv4=None, ipv6=None, user=None):
        self.hostname = hostname
        self.port = port if port else None
        self.ipv4 = ipv4 if ipv4 else None
        self.ipv6 = ipv6 if ipv6 else None
        self.user = user if user else None

    @staticmethod
    def factory(host):
        if isinstance(host, tuple):
            return Host(*host)
        if isinstance(host, dict):
            return Host(**host)
        raise ValueError('Invalid type passed: {0}'.format(type(host)))

    @property
    def display(self):
        if self.user:
            return '{0}@{1}'.format(self.user, self.hostname)
        return self.hostname

    def match(self, needle):
        for search_field in ['hostname', 'ipv4', 'ipv6']:
            value = getattr(self, search_field, None)
            if value is not None and (
                fnmatch.fnmatch(value, needle) or needle in value
            ):
                return True
        return False

    def __repr__(self):
        if self.ipv4 is not None:
            return '<Host: hostname={0}, ipv4={1}>'.format(self.hostname, self.ipv4)
        return '<Host: hostname={0}>'.format(self.hostname)


class Parser(object):
    def __init__(self, path):
        '''

        :param path:
        '''
        self._path = path
        self._hosts = []

    def get_files(self, ext='.json'):
        return [x for x in os.listdir(self._path) if x.endswith(ext)]

    def search(self, needle):
        '''
        Return Host objects which have properties matching the needle
        '''
        results = []
        for host in self._hosts:
            if host.match(needle):
                results.append(host)
        return results

    def _get_file_content(self, path):  # pragma: nocover
        content = ''
        with open(path, 'r') as fh:
            content = fh.read()
        return content


class JsonParser(Parser):
    def __init__(self, *args, **kwargs):
        super(JsonParser, self).__init__(*args, **kwargs)
        self._files = self.get_files(ext='.json')
        self._load_data()

    def _load_data(self):
        """
        Load parser specific data files
        """
        for file_ in self._files:
            path = os.path.join(self._path, file_)
            logger.debug('Parsing "{0}"'.format(path))

            try:
                d = json.loads(self._get_file_content(path))
                logger.debug('Got: {0}'.format(d))
                if not 'hosts' in d:
                    return
                for host in d['hosts']:
                    self._hosts.append(Host.factory(host))
            except ValueError as ex:  # pragma: nocover
                logger.info(f'Config file {path} contains invalid JSON')


class MySQLParser(Parser):  # pragma: nocover
    def __init__(self, *args, **kwargs):
        super(MySQLParser, self).__init__(*args, **kwargs)
        self._files = self.get_files(ext='.mysql')
        self._load_data()

    def _load_data(self):
        '''
        Load parser specific data files
        '''
        for file_ in self._files:
            path = os.path.join(self._path, file_)
            logger.debug('Parsing "{0}"'.format(path))
            with open(path, 'r') as fh:
                d = json.loads(fh.read())
                logger.debug('Got: {0}'.format(d))
                conn = mysql.connector.connect(**d['config'])
                c = conn.cursor()
                c.execute(d['query'])

                for row in c:
                    self._hosts.append(Host.factory(row))


class APIParser(Parser):
    def __init__(self, *args, **kwargs):
        super(APIParser, self).__init__(*args, **kwargs)
        self._files = self.get_files('.api')
        self._load_data()

    def _load_data(self):
        for file_ in self._files:
            path = os.path.join(self._path, file_)
            logger.debug('Parsing "{0}"'.format(path))
            with open(path, 'r') as fh:
                try:
                    d = json.loads(fh.read())
                except ValueError as ex:
                    print('Invalid JSON file: {0}'.format(path))
                    logger.error(ex)
                if 'headers' not in d['config']:
                    d['config']['headers'] = {}
                req = requests.get(d['config']['url'], headers=d['config']['headers'])
                try:
                    res = req.json()
                except ValueError as ex:
                    logger.error('Error loading JSON response from {0}'.format(path))
                if 'hosts' not in res:
                    logger.info('No hosts found in {0}'.format(path))
                for host in res['hosts']:
                    self._hosts.append(Host.factory(host))
