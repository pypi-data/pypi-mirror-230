# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['readability_improver']

package_data = \
{'': ['*']}

install_requires = \
['num2words>=0.5.12,<0.6.0']

entry_points = \
{'console_scripts': ['make-more-readable = '
                     'readability_improver.readability_improver:main']}

setup_kwargs = {
    'name': 'readability-improver',
    'version': '1.0.1',
    'description': 'Remove all your magic numbers and make your code 1000% more readable!',
    'long_description': None,
    'author': 'Eric Udlis',
    'author_email': 'udlis.eric@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
