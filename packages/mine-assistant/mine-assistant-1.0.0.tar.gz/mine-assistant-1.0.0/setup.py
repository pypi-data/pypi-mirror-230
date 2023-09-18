"""Personal custom supporting package"""

import sys
import setuptools


# Python version check
if sys.version_info < (3, 8):
    raise ValueError('This package requires Python 3.8 or newer')


# Package metadata
__project__ = "mine-assistant"
__version__ = "1.0.0"
__license__ = "MIT License"
__name__ = "Lovesh Kumrawat"
__email__ = "kumrawat.lovesh@gmail.com"
__url__ = "https://github.com/lovesh-kumrawat/mine.git"
__download_url__ = "https://pypi.org/project/mine-assistant/"
__platforms__ = "ALL"

__classifiers__ = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    f'License :: OSI Approved :: {__license__}',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3.8',
    'Topic :: Software Development'
]

__keywords__ = [
    "mine",
    "api-keys",
    "key-store",
    "env-setup",
    "llm-keys",
    "secure-keys"
]

with open("README.md", "r") as fh:
    __long_description__ = fh.read()


setuptools.setup(
    name             = __project__,
    version          = __version__,
    description      = __doc__,
    long_description = __long_description__,
    author           = __name__,
    author_email     = __email__,
    maintainer       = __name__,
    maintainer_email = __email__,
    license          = __license__,
    platforms        = __platforms__,
    url              = __url__,
    download_url     = __download_url__,
    classifiers      = __classifiers__,
    keywords         = __keywords__,
    packages         = setuptools.find_packages(),
)
