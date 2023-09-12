# PyHolaClient
A HolaClient API Wrapper using Python!

[![Upload Python Package](https://github.com/VienDC/PyHolaClient/actions/workflows/python-publish.yml/badge.svg)](https://github.com/VienDC/PyHolaClient/actions/workflows/python-publish.yml)

## Special Thanks to The HolaClient Team!
- [HolaClient's Github](https://github.com/HolaClient/)
- [CR072's Github (Main Dev)](https://github.com/CR072)

Installation
To install just run
```bash
pip install pyholaclient
```

## Usage
### Setting up Client

```python
from pyholaclient import HolaClient

client = HolaClient("https://foo.bar", "foo")
```

### Getting User's HCID 
``` python
from pyholaclient import HolaClient

client = HolaClient("https://foo.bar", "foo")
hcid = client.user_hcid(1000000000000000) # <= Discord ID
print(hcid)
```

## Getting User Info
``` python
from pyholaclient import HolaClient

client = HolaClient("https://foo.bar", "foo")
hcid = 1000
user = client.user_info(hcid)

print(user.email)
print(user.first_name)
print(user.last_name)
print(user.username)
print(user.id)
print(user.root_admin) # <== True if Admin
# And many more (Read pyholaclient/Classes/user.py)
```

### There are many more
But for the sake of simplicity. Head to our Docs (WIP)