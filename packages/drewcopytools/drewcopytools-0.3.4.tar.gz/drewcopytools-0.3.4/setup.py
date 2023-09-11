# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['drewcopytools']

package_data = \
{'': ['*']}

install_requires = \
['pathlib>=1.0.1,<2.0.0', 'pytest>=6.2.5,<7.0.0']

setup_kwargs = {
    'name': 'drewcopytools',
    'version': '0.3.4',
    'description': 'Utility code that I use in many of my python projects.  Most of these functions exist to make python work in a predicatble, cross-platform way.',
    'long_description': None,
    'author': 'Andrew Ritz',
    'author_email': 'andrew.a.ritz@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
