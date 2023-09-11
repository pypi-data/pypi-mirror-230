# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tabella']

package_data = \
{'': ['*'],
 'tabella': ['static/*',
             'templates/*',
             'templates/modals/*',
             'templates/schema/*',
             'templates/schema_form/*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0',
 'case-switcher>=1.3.13,<2.0.0',
 'fastapi>=0.103.0,<0.104.0',
 'httpx>=0.24.1,<0.25.0',
 'jsonrpc2-objects>=3.0.0,<4.0.0',
 'lorem-pysum>=1.4.3,<2.0.0',
 'openrpc>=8.0.1,<9.0.0',
 'openrpcclientgenerator>=0.42.3,<0.43.0',
 'uvicorn>=0.23.2,<0.24.0',
 'websockets>=11.0.3,<12.0.0']

setup_kwargs = {
    'name': 'tabella',
    'version': '0.74.1',
    'description': 'Open-RPC API interactive documentation.',
    'long_description': '# Methodology\n\n![](https://img.shields.io/badge/License-ApacheV2-blue.svg)\n![](https://img.shields.io/badge/code%20style-black-000000.svg)\n\nInteractive documentation for OpenRPC APIs.\n\n![Demo](https://gitlab.com/mburkard/tabella/-/raw/main/docs/demo.png)\n\n## Development Setup\n\n### Requirements\n\n- Python3.10+\n- [Poetry](https://python-poetry.org)\n- Node 18+\n\n### Install Dev Dependencies\n\n#### Python\n\n`poetry install`\n\n#### Node\n\n```shell\ncd node\n. build.sh\n```\n\n### Run Test Server\n\n```shell\npoetry shell\nuvicorn tests.integration.integration_app:app --reload\n```\n\nThen navigate to http://localhost:8000 in your browser.\n\n## Inspired By\n\n- [OPEN-RPC Playground](https://playground.open-rpc.org/)\n- [Swagger](https://swagger.io/)\n- [Redoc](https://github.com/Redocly/redoc)\n',
    'author': 'Matthew Burkard',
    'author_email': 'matthewjburkard@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/mburkard/tabella',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
