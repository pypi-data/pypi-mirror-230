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

## Python OpenRPC

The RPC server hosted and documented by Tabella is powered
by [Python OpenRPC](https://gitlab.com/mburkard/openrpc). Refer to the Python OpenRPC
docs hosted [here](https://python-openrpc.burkard.cloud/) for advanced use.

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
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

Run this, then open http://127.0.0.1:8000/ in your browser to use the interactive
documentation.

The Open-RPC API will be hosted over HTTP on `http://127.0.0.1:8000/api` and over
WebSockets on `ws://127.0.0.1:8000/api`.

## Further Usage

### Security and Depends Arguments

The `tabella.get_app` function accepts argument, `middleware`, which is a callable that
will be passed HTTP request headers/WebSocket connection headers. The `middleware`
function must return a tuple of two dictionaries, the first will be passed to the
RPC Server as
[Depends Arguments](https://python-openrpc.burkard.cloud/security/depends_arguments)
and the second as .
[Security Arguments](https://python-openrpc.burkard.cloud/security/schemes)

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

Tabella HTTP and WebSocket server hosting is uses
[FastAPI](https://fastapi.tiangolo.com/). The app returned by `tabella.get_app` is a
FastAPI app.

## Inspired By

- [OPEN-RPC Playground](https://playground.open-rpc.org/)
- [Swagger](https://swagger.io/)
- [Redoc](https://github.com/Redocly/redoc)

## Support The Developer

<a href="https://www.buymeacoffee.com/mburkard" target="_blank">
  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-blue.png"
       width="217"
       height="60"
       alt="Buy Me A Coffee">
</a>
