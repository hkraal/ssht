import fnmatch
import json
import logging
import os

import mysql.connector
import requests


class Host:
    """Class for host presentation."""

    def __init__(self, hostname, port=None, ipv4=None, ipv6=None, user=None):
        """
        Instantiate object.

        Args:
            hostname: Hostname
            port: Optional port (otherwise using the SSH default).
            ipv4: Optional IPv4 address.
            ipv6: Optional IPv6 address.
            user: Optional username to connect with (otherwise using the SSH default).
        """
        self.hostname = hostname
        self.port = port if port else None
        self.ipv4 = ipv4 if ipv4 else None
        self.ipv6 = ipv6 if ipv6 else None
        self.user = user if user else None

    @staticmethod
    def factory(host):
        """Return Host object from tuple or dict."""
        if isinstance(host, tuple):
            return Host(*host)
        if isinstance(host, dict):
            return Host(**host)
        raise ValueError(f"Invalid type passed: {type(host)}")

    @property
    def display(self):
        """Returns hostname with optional username."""
        if self.user:
            return f"{self.user}@{self.hostname}"
        return self.hostname

    def match(self, needle: str) -> bool:
        """
        Check if any of the host attributes matches the needle.

        Args:
            needle: The string we should be looking for, can be Linux styled fnmatch.

        Returns:
            True if the needle matches a host property.
        """
        for search_field in ["hostname", "ipv4", "ipv6"]:
            value = getattr(self, search_field, None)
            if value is not None and (
                fnmatch.fnmatch(value, needle) or needle in value
            ):
                return True
        return False

    def __repr__(self):
        """Print object including IPv4 address if set."""
        if self.ipv4 is not None:
            return f"<Host: hostname={self.hostname}, ipv4={self.ipv4}>"
        return f"<Host: hostname={self.hostname}>"


class Parser:
    """Parent class for parsers."""

    def __init__(self, path):
        """
        Instantiate class with path.

        :param path: The path in which the config files should be looked for.
        """
        self._path = path
        self._hosts = []

    def get_files(self, ext=".json"):
        """
        Get files which match the extension.

        Args:
            ext: The file extension which should be matched.

        Returns:
            List for filenames matching the extension.
        """
        return [x for x in os.listdir(self._path) if x.endswith(ext)]

    def search(self, needle):
        """Return Host objects which have properties matching the needle."""
        results = []
        for host in self._hosts:
            if host.match(needle):
                results.append(host)
        return results

    def _get_file_content(self, path):
        content = ""
        with open(path) as fh:
            content = fh.read()
        return content


class JsonParser(Parser):
    """Class for parsing .json files."""

    def __init__(self, *args, **kwargs):
        """
        Instantiate class for parsing .json files.

        Args:
            *args:
            **kwargs:
        """
        super().__init__(*args, **kwargs)
        self._files = self.get_files(ext=".json")
        self._load_data()

    def _load_data(self):
        """Load parser specific data files."""
        for file_ in self._files:
            path = os.path.join(self._path, file_)
            logging.debug(f'Parsing "{path}"')

            try:
                d = json.loads(self._get_file_content(path))
                logging.debug(f"Got: {d}")
                if "hosts" not in d:
                    return
                for host in d["hosts"]:
                    self._hosts.append(Host.factory(host))
            except ValueError as e:
                logging.info(f"Config error for {path}: {e}")


class MySQLParser(Parser):
    """Class for parsing .mysql files."""

    def __init__(self, *args, **kwargs):
        """
        Instantiate class for parsing .mysql files.

        Args:
            *args:
            **kwargs:
        """
        super().__init__(*args, **kwargs)
        self._files = self.get_files(ext=".mysql")
        self._load_data()

    def _load_data(self):
        """Load parser specific data files."""
        for file_ in self._files:
            path = os.path.join(self._path, file_)
            logging.debug(f'Parsing "{path}"')
            with open(path) as fh:
                d = json.loads(fh.read())
                logging.debug(f"Got: {d}")
                conn = mysql.connector.connect(**d["config"])
                c = conn.cursor()
                c.execute(d["query"])

                for row in c:
                    self._hosts.append(Host.factory(row))


class APIParser(Parser):
    """Class for parsing .api files."""

    def __init__(self, *args, **kwargs):
        """
        Instantiate class for parsing .api files.

        Args:
            *args:
            **kwargs:
        """
        super().__init__(*args, **kwargs)
        self._files = self.get_files(".api")
        self._load_data()

    def _load_data(self):
        for file_ in self._files:
            path = os.path.join(self._path, file_)
            logging.debug(f'Parsing "{path}"')
            with open(path) as fh:
                try:
                    d = json.loads(fh.read())
                except ValueError as ex:
                    print(f"Invalid JSON file: {path}")
                    logging.error(ex)
                if "headers" not in d["config"]:
                    d["config"]["headers"] = {}
                req = requests.get(d["config"]["url"], headers=d["config"]["headers"])
                try:
                    res = req.json()
                except ValueError as ex:
                    print(f"Invalid JSON response for: {path}")
                    logging.error(ex)
                if "hosts" not in res:
                    print(f"No hosts in JSON response for: {path}")
                for host in res["hosts"]:
                    self._hosts.append(Host.factory(host))
