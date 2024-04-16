# ssht
SSH client wrapper for easily connecting to hosts

[![Coverage Status](https://coveralls.io/repos/github/hkraal/ssht/badge.svg?branch=master)](https://coveralls.io/github/hkraal/ssht?branch=master)
![](https://img.shields.io/pypi/pyversions/ssht.svg?style=flat)

This wrapper for the well known `ssh` client makes it possible to connect to the right server with just typing a part of the host name. The external sources are queried using the search term and those matching the string will be presented as an option.

Current supported sources:

* JSON file
* MySQL database
* JSON API endpoint
* Custom parser class

### Installation

Install ssht using pip:

    pip3 install ssht

or if you want the latest version:

    pip3 install https://github.com/hkraal/ssht/archive/master.zip


### Usage

    ssht [-h] name [-4] [-6] 
    
    positional arguments:
      name        name of the host to connect to
    
    optional arguments:
      -h, --help  show this help message and exit
      -4          connect using ipv4 (skip dns if ipv4 address is defined)
      -6          connect using ipv6 (skip dns of ipv6 address is defined)

Example of a connection

    $ ssht host01
    1) root@host01.exmaple.com
    2) host01.exmaple.com
    Connect to: 1
    Connecting to "host01.example.com"
    root@host01:~$

### Configuration

Create ssht folder in home directory

    mkdir ~/.ssht

Configure sources in ~/.ssht:

**Define servers in JSON format**:

    {
    	"hosts": [
    	  {
    		"port": "2222",
    		"hostname": "host01.example.com",
    		"ipv4": "192.168.0.2",
    		"user": "root"
    	  },
    	  {
    		"port": "2222",
    		"hostname": "host01.example.com",
    		"ipv4": "192.168.0.2",
    	  }
    	]
    }

**Define servers in MySQL**:

    {
      "config": {
        "host": "localhost",
        "user": "username",
        "password": "passeword",
        "database": "infra"
      },
      "query": "SELECT hostname, port, ipv4, ipv6, user FROM servers"
    }

**Define JSON API endpoint**:

	{
		"config": {
			"url": "http://ssht-api.dev",
			"headers": {
				"Authentication": "bla:huk"
			}
		}
	}

**Define custom class**:

1) Create a Python package containing your class

```
from ssht.plugins import Parser, Host


class ExampleParser(Parser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._files = self.get_files('.custom')

    def search(self, needle):
        return [
            Host(hostname='host01.example.com', ipv4='192.168.0.2'),
        ]
```

2) Enable your class in `~/.ssht/config.json`

```
{
    "parsers":
    [
        "ssht.plugins.JsonParser",
        "ssht_provider.ExampleParser"
    ]
}
```