# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'source/packages'}

packages = \
['mojo', 'mojo.errors']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'mojo-errors',
    'version': '0.0.2',
    'description': 'Automation Mojo Errors Module',
    'long_description': '==============================\nAutomation Mojo Errors Package\n==============================\nPython package that provides a common source of error types.\n',
    'author': 'None',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
