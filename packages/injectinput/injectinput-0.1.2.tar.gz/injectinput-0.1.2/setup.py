# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['injectinput']

package_data = \
{'': ['*']}

install_requires = \
['evdev>=1.4.0,<2.0.0']

entry_points = \
{'console_scripts': ['injectinput = injectinput.injectinput:main']}

setup_kwargs = {
    'name': 'injectinput',
    'version': '0.1.2',
    'description': 'Inject input',
    'long_description': 'None',
    'author': 'Dick Marinus',
    'author_email': 'dick@mrns.nl',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
