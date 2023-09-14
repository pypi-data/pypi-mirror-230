# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['zit', 'zit.dataset', 'zit.routes', 'zit.routes.dataset']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'duckdb>=0.8.1,<0.9.0',
 'fastapi>=0.95.1,<0.96.0',
 'httpx[socks]>=0.24.1,<0.25.0',
 'pandas>=2.0.2,<3.0.0',
 'pillow>=9.5.0,<10.0.0',
 'python-multipart>=0.0.6,<0.0.7',
 'typer[all]>=0.7.0,<0.8.0',
 'websocket-client>=1.5.1,<2.0.0']

entry_points = \
{'console_scripts': ['zit = zit.main:app']}

setup_kwargs = {
    'name': 'zit',
    'version': '0.0.5a1',
    'description': 'ZitySpace CLI tool',
    'long_description': 'None',
    'author': 'Rui Zheng',
    'author_email': 'rui@zityspace.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
