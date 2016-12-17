'''
Created on 13 Jan 2017

@author: henk
'''
from ssht.plugins import Host


class TestHost:

    def test_default(self):
        x = Host(hostname='host01.example.com')
        assert x.display == 'host01.example.com'
    
    def test_user(self):
        x = Host(hostname='host01.example.com',
                 user='admin')
        assert x.display == 'admin@host01.example.com'

    def test_factory_dict(self):
        host = Host.factory(dict(hostname='host01.example.com'))
        assert host.hostname == 'host01.example.com'

    def test_factory_tuple(self):
        host = Host.factory(('host01.example.com',))
        assert host.hostname == 'host01.example.com'
