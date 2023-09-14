"""
This library implements various methods for working with the Google KMS APIs.

## Installation

```console
$ pip install --upgrade gcloud-rest-kms
```

## Usage

We're still working on more complete documentation, but roughly you can do:

```python
from gcloud.rest.kms import KMS
from gcloud.rest.kms import decode
from gcloud.rest.kms import encode

kms = KMS('my-kms-project', 'my-keyring', 'my-key-name')

# encrypt
plaintext = b'the-best-animal-is-the-aardvark'
ciphertext = kms.encrypt(encode(plaintext))

# decrypt
assert decode(kms.decrypt(ciphertext)) == plaintext

# close the HTTP session
# Note that other options include:
# * providing your own session: `KMS(.., session=session)`
# * using a context manager: `with KMS(..) as kms:`
kms.close()
```

## Emulators

For testing purposes, you may want to use `gcloud-rest-kms` along with a local
emulator. Setting the `$KMS_EMULATOR_HOST` environment variable to the address
of your emulator should be enough to do the trick.
"""
import importlib.metadata

from .kms import KMS
from .kms import SCOPES
from .utils import decode
from .utils import encode


__version__ = importlib.metadata.version('gcloud-rest-kms')
__all__ = ['__version__', 'decode', 'encode', 'KMS', 'SCOPES']
