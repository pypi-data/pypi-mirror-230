## Common utilities used in BT testing
This package is used to hold common utilities for BT testing.

## Steps to upload package in PIP
1. Edit `setup.py` and `bttc/__init__.py` to have expected version information.
2. Dump package into gz file:
```
# Confirm to have latest version info
$ grep 'version' setup.py
    version='0.0.2'

# Dump the package into gz file
$ python setup.py sdist
...

# Check the exported gz file
$ ls -hl dist/bttc-0.0.2.tar.gz
```

3. Upload the generated gz file:
```
$ twine upload dist/bttc-0.0.2.tar.gz
...
View at:
https://pypi.org/project/bttc/0.0.2/
```
Ps. For this step to work, make sure you have edit `~/.pypirc` to have correct
credentials

## Steps to run unit test
Execute below command to do unit test:
```
$ make test
```

## Steps to run link
Execute below command to do lint check:
```
$ make lint
```

## Release info
* Release v0.0.53
    - Support iPerf facade.
* Release v0.0.56
    - Support module `wifi_utils` for common WiFi operations (#22).
* Release v0.0.57
    - Support profile AVRCP (#30)
