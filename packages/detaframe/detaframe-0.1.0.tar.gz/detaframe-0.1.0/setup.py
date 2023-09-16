# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['detaframe', 'detaframe.dev']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0',
 'Unidecode>=1.3.6,<2.0.0',
 'aiohttp>=3.8.5,<4.0.0',
 'deta[async]>=1.2.0,<2.0.0',
 'itsdangerous>=2.1.2,<3.0.0',
 'pydantic>=2.3.0,<3.0.0',
 'python-multipart>=0.0.6,<0.0.7',
 'starlette-csrf>=3.0.0,<4.0.0',
 'starlette>=0.31.1,<0.32.0',
 'typing-extensions>=4.7.1,<5.0.0',
 'uvicorn>=0.23.2,<0.24.0']

setup_kwargs = {
    'name': 'detaframe',
    'version': '0.1.0',
    'description': 'Framework for DetaSpace using Pydantic and Starlette.',
    'long_description': None,
    'author': 'Daniel Arantes',
    'author_email': 'arantesdv@me.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
