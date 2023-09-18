# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tabella']

package_data = \
{'': ['*'],
 'tabella': ['static/*',
             'templates/*',
             'templates/modals/*',
             'templates/modals/auth/*',
             'templates/schema/*',
             'templates/schema_form/*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0',
 'case-switcher>=1.3.13,<2.0.0',
 'fastapi>=0.103.0,<0.104.0',
 'jsonrpc2-objects>=3.0.0,<4.0.0',
 'lorem-pysum>=1.4.3,<2.0.0',
 'openrpc>=8.2.9,<9.0.0',
 'openrpcclientgenerator>=0.43.3,<0.44.0']

setup_kwargs = {
    'name': 'tabella',
    'version': '0.91.10',
    'description': 'Open-RPC API hosting and interactive documentation.',
    'long_description': '# Tabella\n\n![](https://img.shields.io/badge/License-ApacheV2-blue.svg)\n![](https://img.shields.io/badge/code%20style-black-000000.svg)\n![](https://img.shields.io/pypi/v/tabella.svg)\n\n## Open-RPC development framework with builtin interactive documentation.\n\n![Demo](https://gitlab.com/mburkard/tabella/-/raw/main/docs/demo.png)\n\n## Install\n\nTabella is on PyPI and can be installed with:\n\n```shell\npip install tabella\n```\n\nOr with [Poetry](https://python-poetry.org/)\n\n```shell\npoetry add tabella\n```\n\n## Python OpenRPC\n\nThe RPC server hosted and documented by Tabella is powered\nby [Python OpenRPC](https://gitlab.com/mburkard/openrpc). Refer to the Python OpenRPC\ndocs hosted [here](https://python-openrpc.burkard.cloud/) for advanced use.\n\n## Getting Started\n\nA basic Tabella app:\n\n```python\nimport tabella\nfrom openrpc import RPCServer\nimport uvicorn\n\nrpc = RPCServer()\n\n\n@rpc.method()\ndef echo(a: str, b: float) -> tuple[str, float]:\n    """Echo parameters back in result."""\n    return a, b\n\n\napp = tabella.get_app(rpc)\n\nif __name__ == "__main__":\n    uvicorn.run(app, host="127.0.0.1", port=8000)\n```\n\nRun this, then open http://127.0.0.1:8000/ in your browser to use the interactive\ndocumentation.\n\nThe Open-RPC API will be hosted over HTTP on `http://127.0.0.1:8000/api` and over\nWebSockets on `ws://127.0.0.1:8000/api`.\n\n## Further Usage\n\n### Security and Depends Arguments\n\nThe `tabella.get_app` function accepts argument, `middleware`, which is a callable that\nwill be passed HTTP request headers/WebSocket connection headers. The `middleware`\nfunction must return a tuple of two dictionaries, the first will be passed to the\nRPC Server as\n[Depends Arguments](https://python-openrpc.burkard.cloud/security/depends_arguments)\nand the second as .\n[Security Arguments](https://python-openrpc.burkard.cloud/security/schemes)\n\n### Set Servers\n\nSet RPC servers manually to specify transport and paths to host the RPC server on, e.g.\n\n```python\nfrom openrpc import RPCServer, Server\nimport tabella\n\nrpc = RPCServer(\n    servers=[\n        Server(name="HTTP API", url="http://localhost:8000/my/api/path"),\n        Server(name="WebSocket API", url="ws://localhost:8000/my/api/path"),\n    ]\n)\napp = tabella.get_app(rpc)\n```\n\nThis app will host the RPCServer over HTTP and over WebSockets with the\npath `/my/api/path`.\n\n### Pydantic\n\n[Pydantic](https://docs.pydantic.dev/latest/) is used for request/response\ndeserialization/serialization as well as schema generation. Pydantic should be used for\nany models as seen here in\nthe [Python OpenRPC Docs](https://python-openrpc.burkard.cloud/basics#pydantic-for-data-models).\n\n### FastAPI\n\nTabella HTTP and WebSocket server hosting is uses\n[FastAPI](https://fastapi.tiangolo.com/). The app returned by `tabella.get_app` is a\nFastAPI app.\n\n## Inspired By\n\n- [OPEN-RPC Playground](https://playground.open-rpc.org/)\n- [Swagger](https://swagger.io/)\n- [Redoc](https://github.com/Redocly/redoc)\n\n## Support The Developer\n\n<a href="https://www.buymeacoffee.com/mburkard" target="_blank">\n  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-blue.png"\n       width="217"\n       height="60"\n       alt="Buy Me A Coffee">\n</a>\n',
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
