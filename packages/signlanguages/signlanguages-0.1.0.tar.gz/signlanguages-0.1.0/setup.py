# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['signlanguages']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'signlanguages',
    'version': '0.1.0',
    'description': '',
    'long_description': '# Summarize dataframe\n',
    'author': 'YAYAYru',
    'author_email': 'AlexeyAYAYA@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
