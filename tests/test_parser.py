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

    def test_search(self):
        parser = Parser('/tmp')
        parser._hosts = [Host('host01.example.com'),
                         Host('host02.example.com')]
        assert parser.search('host01')[0].hostname == 'host01.example.com'
        assert len(parser.search('example.com')) == 2


class TestJsonParser:
    pass
    

class TestMySQLParser:
    pass
