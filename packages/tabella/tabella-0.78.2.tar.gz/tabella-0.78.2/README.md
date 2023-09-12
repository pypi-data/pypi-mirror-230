# Tabella

![](https://img.shields.io/badge/License-ApacheV2-blue.svg)
![](https://img.shields.io/badge/code%20style-black-000000.svg)
![](https://img.shields.io/pypi/v/tabella.svg)

## Open-RPC development framework with builtin interactive documentation.

![Demo](https://gitlab.com/mburkard/tabella/-/raw/main/docs/demo.png)

## Install

Tabella is on PyPI and can be installed with:

```shell
pip install tabella
```

Or with [Poetry](https://python-poetry.org/)

```shell
poetry add tabella
```

## Getting Started

A basic Tabella app:

```python
import tabella
from openrpc import RPCServer
import uvicorn

rpc = RPCServer()


@rpc.method()
def echo(a: str, b: float) -> tuple[str, float]:
    """Echo parameters back in result."""
    return a, b


app = tabella.get_app(rpc)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Run this, then open http://localhost:8000/ in your browser to use the interactive
documentation.

The Open-RPC API will be hosted over HTTP on `http://localhost:8000/api` and over
WebSockets on `ws://localhost:8000/api`.

## Python Open-RPC

The RPC server hosted and documented by Tabella is powered
by [Python OpenRPC](https://gitlab.com/mburkard/openrpc). Refer to the Python OpenRPC
docs hosted [here](https://python-openrpc.burkard.cloud/) for advanced use.

## Further Usage

### Use Request Headers

The `tabella.get_app` function accepts an argument, `depends_middleware`, which is a
callable that will be passed HTTP request headers/WebSocket connection headers.
The `depends_middleware` must return a dictionary, that dictionary will be passed to the
RPC Server as
[Depends Arguments](https://python-openrpc.burkard.cloud/security/authorization#dependent-arguments).

#### Example Using `depends_middleware` to Pass API Key to Methods

So if an API key is being passed as a request header, and you would like to forward it
to a method you can set the `depends_middleware` as such:

```python
app = get_app(rpc, lambda h: {"api_key": h.get("api_key")})
```

Then, methods can get access to that value:

```python
from openrpc import RPCServer, Depends

rpc = RPCServer()


@rpc.method()
def authorized_method(a: int, b: int, api_key: str = Depends) -> int:
    if not my_function_to_check_permission(api_key):
        raise PermissionError("Missing permission to call this method.")
    return a + b
```

### Set Servers

Set RPC servers manually to specify transport and paths to host the RPC server on, e.g.

```python
from openrpc import RPCServer, Server
import tabella

rpc = RPCServer(
    servers=[
        Server(name="HTTP API", url="http://localhost:8000/my/api/path"),
        Server(name="WebSocket API", url="ws://localhost:8000/my/api/path"),
    ]
)
app = tabella.get_app(rpc)
```

This app will host the RPCServer over HTTP and over WebSockets with the
path `/my/api/path`.

### Pydantic

[Pydantic](https://docs.pydantic.dev/latest/) is used for request/response
deserialization/serialization as well as schema generation. Pydantic should be used for
any models as seen here in
the [Python OpenRPC Docs](https://python-openrpc.burkard.cloud/basics#pydantic-for-data-models).

### FastAPI

Tabella HTTP and WebSocket server hosting is done with
[FastAPI](https://fastapi.tiangolo.com/). The app returned by `tabella.get_app` is a
FastAPI app.

## Inspired By

- [OPEN-RPC Playground](https://playground.open-rpc.org/)
- [Swagger](https://swagger.io/)
- [Redoc](https://github.com/Redocly/redoc)
