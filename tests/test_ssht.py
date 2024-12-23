"""
Created on 7 Jan 2017

@author: henk
"""

import logging
import os
import subprocess

from ssht.plugins import Host
from ssht.ssht import ssh_connect, select_host, get_log_level


class TestConnect:
    def test_hostname(self, mocker):
        mocker.patch("subprocess.call")
        ssh_connect(Host(hostname="host01.example.com"), [])
        subprocess.call.assert_called_with(
            ["ssh", "host01.example.com"],
        )

    def test_default_ipv4(self, mocker):
        mocker.patch("subprocess.call")
        ssh_connect(Host(hostname="host01.example.com", ipv4="192.168.0.1"), [])
        subprocess.call.assert_called_with(
            ["ssh", "192.168.0.1"],
        )

    def test_port(self, mocker):
        mocker.patch("subprocess.call")
        ssh_connect(Host(hostname="host01.example.com", port="22022"), [])
        subprocess.call.assert_called_with(
            ["ssh", "host01.example.com", "-p", "22022"],
        )

    def test_ipv4_(self, mocker):
        mocker.patch("subprocess.call")
        ssh_connect(Host(hostname="host01.example.com", ipv4="192.168.1.2"), ["-4"])
        subprocess.call.assert_called_with(
            ["ssh", "192.168.1.2", "-4"],
        )

    def test_ipv6(self, mocker):
        mocker.patch("subprocess.call")
        ssh_connect(Host(hostname="host01.example.com", ipv6="::1"), ["-6"])
        subprocess.call.assert_called_with(["ssh", "::1", "-6"])

    def test_user(self, mocker):
        mocker.patch("subprocess.call")
        ssh_connect(Host(hostname="host01.example.com", user="admin"), [])
        subprocess.call.assert_called_with(["ssh", "host01.example.com", "-l", "admin"])


class TestSsht:
    def test_select_host(self, mocker):
        hosts = [
            Host(hostname="host01.example.com", ipv4="127.0.0.1"),
            Host(hostname="host02.example.com", ipv4="127.0.0.2", user="admin"),
        ]

        mocker.patch("ssht.ssht.get_answer", return_value="1")
        assert select_host(hosts).hostname == "host01.example.com"
        assert select_host(hosts).user is None

        mocker.patch("ssht.ssht.get_answer", return_value="2")
        assert select_host(hosts).hostname == "host02.example.com"
        assert select_host(hosts).user == "admin"

        mocker.patch("ssht.ssht.get_answer", return_value="")
        assert select_host(hosts) is None

    def test_get_log_level_default(self):
        os.unsetenv("SSHT_DEBUG")
        assert logging.WARNING == get_log_level()

    def test_get_log_level_debug(self):
        os.environ["SSHT_DEBUG"] = "1"
        assert logging.DEBUG == get_log_level()
