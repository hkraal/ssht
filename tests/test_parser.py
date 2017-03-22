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
        parser._hosts = [Host('host01.example.com', ipv6='fe80::41:dead:beef:cafe'),
                         Host('host02.example.com', ipv6='fe80::41:dead:beef:daff')]
        assert parser.search('dead:beef:cafe')[0].hostname == 'host01.example.com'
        assert len(parser.search('dead:beef:')) == 2


class TestJsonParser:
    pass
    

class TestMySQLParser:
    pass
