# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['views_dataviz']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'views-dataviz',
    'version': '0.11.0',
    'description': 'Obsolete views package for data visualization',
    'long_description': None,
    'author': 'mihai',
    'author_email': 'mihai.croicu@pcr.uu.se',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
}


setup(**setup_kwargs)
