'''
Created on 13 Jan 2017

@author: henk
'''
from ssht.plugins import Parser, Host, JsonParser


class TestParser:

    def test_get_files(self, mocker):
        mocker.patch('os.listdir', return_value=['test.json', 'test.mysql'])
        parser = Parser('/tmp')
        assert parser.get_files('.json') == ['test.json']
        assert parser.get_files('.mysql') == ['test.mysql']
        assert parser.get_files('.fake') == []

    def test_search_hostname(self):
        parser = Parser('/tmp')
        parser._hosts = [Host('host01.example.com'),
                         Host('host02.example.com')]
        assert parser.search('host01')[0].hostname == 'host01.example.com'
        assert len(parser.search('example.com')) == 2

    def test_search_ipv4(self):
        parser = Parser('/tmp')
        parser._hosts = [Host('host01.example.com', ipv4='192.168.0.1'),
                         Host('host02.example.com', ipv4='192.168.0.2')]
        assert parser.search('192.168.0.1')[0].hostname == 'host01.example.com'
        assert len(parser.search('192.168.0')) == 2

    def test_search_ipv6(self):
        parser = Parser('/tmp')
        parser._hosts = [
            Host('host01.example.com', ipv6='fe80::41:dead:beef:cafe'),
            Host('host02.example.com', ipv6='fe80::41:dead:beef:daff')]
        assert parser.search('dead:beef:cafe')[
                   0].hostname == 'host01.example.com'
        assert len(parser.search('dead:beef:')) == 2

    def test_search_fnmatch_wildcard(self):
        parser = Parser('/tmp')
        parser._hosts = [Host('host01.example.com'),
                         Host('host02.example.com')]
        assert parser.search('host*.example.com')[
                   0].hostname == 'host01.example.com'
        assert len(parser.search('example.com')) == 2

    def test_search_fnmatch_questionmark(self):
        parser = Parser('/tmp')
        parser._hosts = [Host('host01.example.com'),
                         Host('host02.example.com')]
        assert parser.search('host??.example.com')[
                   0].hostname == 'host01.example.com'
        assert len(parser.search('host??.example.com')) == 2


class TestJsonParser:

    def test_load_invalid_data(mocker):
        '''Ensure invalid JSON exceptions are catched properly'''

        def _get_file_content(file_):
            return 'not JSON encoded'

        jsonparser = JsonParser('/tmp')
        jsonparser._files = ['test.json']
        jsonparser._get_file_content = _get_file_content

        assert len(jsonparser._hosts) == 0

    def test_load_valid_data(mocker):
        def _get_file_content(file_):
            return '{ "hosts": [{ "port": "2222", "hostname": \
            "host01.example.com", "ipv4": "192.168.0.2", \
            "user": "root"}] }'

        jsonparser = JsonParser('/tmp')
        jsonparser._files = ['test.json']
        jsonparser._get_file_content = _get_file_content
        jsonparser._load_data()

        assert jsonparser._hosts[0].hostname == 'host01.example.com'


class TestMySQLParser:
    pass


class TestAPIParser:
    pass
