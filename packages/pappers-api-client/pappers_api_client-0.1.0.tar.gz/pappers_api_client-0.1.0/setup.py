# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pappers_api_client', 'pappers_api_client.resources']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.31.0,<3.0.0']

setup_kwargs = {
    'name': 'pappers-api-client',
    'version': '0.1.0',
    'description': '',
    'long_description': '',
    'author': 'Steven Athouel',
    'author_email': 'sathouel@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
