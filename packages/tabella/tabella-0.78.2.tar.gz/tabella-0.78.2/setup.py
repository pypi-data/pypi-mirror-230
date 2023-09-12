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
 'openrpc>=8.1.0,<9.0.0',
 'openrpcclientgenerator>=0.43.0,<0.44.0',
 'uvicorn>=0.23.2,<0.24.0',
 'websockets>=11.0.3,<12.0.0']

setup_kwargs = {
    'name': 'tabella',
    'version': '0.78.2',
    'description': 'Open-RPC API interactive documentation.',
    'long_description': '# Tabella\n\n![](https://img.shields.io/badge/License-ApacheV2-blue.svg)\n![](https://img.shields.io/badge/code%20style-black-000000.svg)\n![](https://img.shields.io/pypi/v/tabella.svg)\n\n## Open-RPC development framework with builtin interactive documentation.\n\n![Demo](https://gitlab.com/mburkard/tabella/-/raw/main/docs/demo.png)\n\n## Install\n\nTabella is on PyPI and can be installed with:\n\n```shell\npip install tabella\n```\n\nOr with [Poetry](https://python-poetry.org/)\n\n```shell\npoetry add tabella\n```\n\n## Getting Started\n\nA basic Tabella app:\n\n```python\nimport tabella\nfrom openrpc import RPCServer\nimport uvicorn\n\nrpc = RPCServer()\n\n\n@rpc.method()\ndef echo(a: str, b: float) -> tuple[str, float]:\n    """Echo parameters back in result."""\n    return a, b\n\n\napp = tabella.get_app(rpc)\n\nif __name__ == "__main__":\n    uvicorn.run(app, host="0.0.0.0", port=8000)\n```\n\nRun this, then open http://localhost:8000/ in your browser to use the interactive\ndocumentation.\n\nThe Open-RPC API will be hosted over HTTP on `http://localhost:8000/api` and over\nWebSockets on `ws://localhost:8000/api`.\n\n## Python Open-RPC\n\nThe RPC server hosted and documented by Tabella is powered\nby [Python OpenRPC](https://gitlab.com/mburkard/openrpc). Refer to the Python OpenRPC\ndocs hosted [here](https://python-openrpc.burkard.cloud/) for advanced use.\n\n## Further Usage\n\n### Use Request Headers\n\nThe `tabella.get_app` function accepts an argument, `depends_middleware`, which is a\ncallable that will be passed HTTP request headers/WebSocket connection headers.\nThe `depends_middleware` must return a dictionary, that dictionary will be passed to the\nRPC Server as\n[Depends Arguments](https://python-openrpc.burkard.cloud/security/authorization#dependent-arguments).\n\n#### Example Using `depends_middleware` to Pass API Key to Methods\n\nSo if an API key is being passed as a request header, and you would like to forward it\nto a method you can set the `depends_middleware` as such:\n\n```python\napp = get_app(rpc, lambda h: {"api_key": h.get("api_key")})\n```\n\nThen, methods can get access to that value:\n\n```python\nfrom openrpc import RPCServer, Depends\n\nrpc = RPCServer()\n\n\n@rpc.method()\ndef authorized_method(a: int, b: int, api_key: str = Depends) -> int:\n    if not my_function_to_check_permission(api_key):\n        raise PermissionError("Missing permission to call this method.")\n    return a + b\n```\n\n### Set Servers\n\nSet RPC servers manually to specify transport and paths to host the RPC server on, e.g.\n\n```python\nfrom openrpc import RPCServer, Server\nimport tabella\n\nrpc = RPCServer(\n    servers=[\n        Server(name="HTTP API", url="http://localhost:8000/my/api/path"),\n        Server(name="WebSocket API", url="ws://localhost:8000/my/api/path"),\n    ]\n)\napp = tabella.get_app(rpc)\n```\n\nThis app will host the RPCServer over HTTP and over WebSockets with the\npath `/my/api/path`.\n\n### Pydantic\n\n[Pydantic](https://docs.pydantic.dev/latest/) is used for request/response\ndeserialization/serialization as well as schema generation. Pydantic should be used for\nany models as seen here in\nthe [Python OpenRPC Docs](https://python-openrpc.burkard.cloud/basics#pydantic-for-data-models).\n\n### FastAPI\n\nTabella HTTP and WebSocket server hosting is done with\n[FastAPI](https://fastapi.tiangolo.com/). The app returned by `tabella.get_app` is a\nFastAPI app.\n\n## Inspired By\n\n- [OPEN-RPC Playground](https://playground.open-rpc.org/)\n- [Swagger](https://swagger.io/)\n- [Redoc](https://github.com/Redocly/redoc)\n',
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
