# atlas-rfp
[![PyPI-downloads](https://img.shields.io/pypi/dm/atlas-rfp)](https://pypi.org/project/atlas-rfp)
[![PyPI-version](https://img.shields.io/pypi/v/atlas-rfp)](https://pypi.org/project/atlas-rfp)
[![PyPI-license](https://img.shields.io/pypi/l/atlas-rfp)](https://pypi.org/project/atlas-rfp)
[![Supported python versions](https://img.shields.io/pypi/pyversions/atlas-rfp)](https://pypi.org/project/atlas-rfp)

## Rationale
MIT's reimbursement system is aging. Having a high-performance, statically-typed
interface to the RFP system enables higher-level financial scripts and programs
to be created.

This script uses `touchstone-auth`, another one of my Python packages that is
a Python user-agent capable of properly two-factor authenticating your scripts,
without requiring a browser.

## Install
This package is on Pip, so you can just:
```
pip install atlas-rfp
```

Alternatively, you can get built wheels from the [Releases tab on Github](https://github.com/meson800/atlas-rfp/releases).

## Quickstart
To perform Touchstone authentication, we need a client-side certificate.
Remember to **not hard-code** your credentials!
The example here loads credentials from a json file called `credentials.json`:
```
{
    "certfile": "some_client_credential.p12",
    "password": "horse-battery-staple-correct"
}
```

Then, in your Python file, you can do the following:
```
import json
from touchstone_auth import TouchstoneSession

with open('credentials.json') as cred_file:
    credentials = json.load(cred_file)

with TouchstoneSession(
    base_url='https://atlas.mit.edu',
    pkcs12_filename=credentials['certfile'],
    pkcs12_pass=credentials['password'],
    cookiejar_filename='cookies.pickle') as s:

    response = s.get('https://atlas.mit.edu/atlas/Main.action')
```

For more examples on how to authenticate,
see the [touchstone-auth documentation](https://github.com/meson800/touchstone-auth).

## Complete Examples

## Developer install
If you'd like to hack locally on `atlas-rfp`, after cloning this repository:
```
$ git clone https://github.com/meson800/atlas-rfp.git
$ cd git
```
you can create a local virtual environment, and install `atlas-rfp` in "development mode"
```
$ python -m venv env
$ .\env\Scripts\activate    (on Windows)
$ source env/bin/activate   (on Mac/Linux)
$ pip install -e .
```
After this 'local install', you can use and import `atlas-rfp` freely without
having to re-install after each update.

## Changelog
See the [CHANGELOG](CHANGELOG.md) for detailed changes.
```
## [0.1.7] - 2023-09-10
### Changed
- Added fallback for relative URLs in receipts
```

## License
This is licensed by the MIT license. Use freely!
