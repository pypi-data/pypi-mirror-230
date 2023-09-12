from setuptools import setup, find_packages

# Package metadata
NAME = 'pyholaclient'
VERSION = 'v0.1.55'
DESCRIPTION = 'An API Wrapper for HolaClient'
URL = 'https://github.com/VienDC/HolaClientPY'
AUTHOR = 'Vien Catigan'
AUTHOR_EMAIL = 'vien@courvix.com'
LICENSE = 'GPL-3.0'

# Dependencies
INSTALL_REQUIRES = [
    'httpx==0.24.1'
]

with open('LICENSE', 'r') as f:
    GPL_LICENSE_TEXT = f.read()

with open('README.md', 'r') as f:
    README = f.read()

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=README,
    long_description_content_type='text/markdown',
    url=URL,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    packages=find_packages(),
    install_requires=INSTALL_REQUIRES,
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
