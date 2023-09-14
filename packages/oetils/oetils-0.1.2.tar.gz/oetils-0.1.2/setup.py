# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['oetils']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.7.1,<4.0.0',
 'numpy>=1.24.2,<2.0.0',
 'scienceplots>=2.1.0,<3.0.0']

setup_kwargs = {
    'name': 'oetils',
    'version': '0.1.2',
    'description': 'A collection of useful functions and classes',
    'long_description': '# Ötils\nA collection of useful functions and classes for my research.',
    'author': 'Onno Eberhard',
    'author_email': 'onnoeberhard@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/onnoeberhard/oetils',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
