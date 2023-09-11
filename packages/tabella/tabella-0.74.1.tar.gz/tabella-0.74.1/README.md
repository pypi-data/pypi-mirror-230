# Methodology

![](https://img.shields.io/badge/License-ApacheV2-blue.svg)
![](https://img.shields.io/badge/code%20style-black-000000.svg)

Interactive documentation for OpenRPC APIs.

![Demo](https://gitlab.com/mburkard/tabella/-/raw/main/docs/demo.png)

## Development Setup

### Requirements

- Python3.10+
- [Poetry](https://python-poetry.org)
- Node 18+

### Install Dev Dependencies

#### Python

`poetry install`

#### Node

```shell
cd node
. build.sh
```

### Run Test Server

```shell
poetry shell
uvicorn tests.integration.integration_app:app --reload
```

Then navigate to http://localhost:8000 in your browser.

## Inspired By

- [OPEN-RPC Playground](https://playground.open-rpc.org/)
- [Swagger](https://swagger.io/)
- [Redoc](https://github.com/Redocly/redoc)
