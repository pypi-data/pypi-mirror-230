"""Tabella API function definitions."""
__all__ = ("get_app",)

import asyncio
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Callable
from urllib import parse

import caseswitcher
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jsonrpcobjects.objects import (
    ErrorResponse,
    Notification,
    ParamsNotification,
    ParamsRequest,
    Request as RPCRequest,
    ResultResponse,
)
from openrpc import OpenRPC, ParamStructure, RPCServer, Schema, SchemaType, Server
from openrpcclientgenerator import generate, Language
from starlette.responses import FileResponse, JSONResponse, Response

# noinspection PyProtectedMember
from starlette.templating import _TemplateResponse
from starlette.websockets import WebSocket, WebSocketDisconnect

from tabella import _util as util
from tabella._cache import TabellaCache
from tabella._templating_engine import TemplatingEngine

RequestType = ParamsRequest | RPCRequest | ParamsNotification | Notification
DependsMiddleware = Callable[[dict[str, str]], dict[str, Any]] | None

root = Path(__file__).parent

app = FastAPI(docs_url="/swagger")
app.mount("/static", StaticFiles(directory=root / "static"), name="static")
templates = Jinja2Templates(
    directory=root / "templates", lstrip_blocks=True, trim_blocks=True
)

cache = TabellaCache.get_instance()
base_context: dict[str, Any] = {
    "enable_auth": os.environ.get("ENABLE_AUTH"),
    "len": len,
    "str": str,
    "id": lambda x: f"_{x}",
    "any_id": lambda x: f"__{x}",
    "array_item_id": lambda x: f"_array{x}",
    "is_any": util.is_any,
    "is_str": lambda x: isinstance(x, str),
    "is_": lambda x, y: x is y,
    "is_even": lambda input_id: input_id.count("_") % 2 != 0,
    "ParamStructure": ParamStructure,
    "key_schema": Schema(type="string"),
}


def get_app(
    rpc: RPCServer,
    depends_middleware: DependsMiddleware = None,
    *,
    enable_auth: bool = True,
) -> FastAPI:
    # noinspection GrazieInspection
    """Host the Given RPCServer.

    :param rpc: RPC server to host.
    :param depends_middleware: Function to get RPCServer `depends`
        values from request headers.
    :param enable_auth: Enable API key auth from the docs viewer.
    """
    base_context["enable_auth"] = enable_auth
    if not rpc:
        return app

    async def _request_processor(request: str, headers: dict[str, str]) -> str:
        depends = depends_middleware(headers) if depends_middleware else {}
        return await rpc.process_request_async(request, depends) or ""

    servers = []
    if isinstance(rpc.servers, Server) or not rpc.servers:
        parsed_url = parse.urlparse(rpc.servers.url)
        if not parsed_url.scheme and parsed_url.path == "localhost":
            port = "8000"
            for arg in sys.argv:
                if arg == "--port":
                    port = sys.argv[sys.argv.index(arg) + 1]
                    break
            servers.append(
                Server(name="http default", url=f"http://localhost:{port}/api")
            )
            servers.append(Server(name="ws default", url=f"ws://localhost:{port}/api"))
    else:
        servers = rpc.servers
        cache.servers = rpc.servers

    for server in servers:
        parsed_url = parse.urlparse(server.url)
        if parsed_url.scheme.startswith("http"):
            _add_ws_api_url(rpc, parsed_url.path, depends_middleware)
        elif parsed_url.scheme.startswith("ws"):
            _add_http_api_url(rpc, parsed_url.path, depends_middleware)

    api_path = servers[0].url
    # Type ignore because mypy fails to understand unions here.
    cache.set_request_processor(_request_processor, api_path)  # type: ignore
    return app


def _add_ws_api_url(
    rpc: RPCServer, api_path: str, depends_middleware: DependsMiddleware
) -> None:
    @app.websocket(api_path)
    async def ws_process_rpc(websocket: WebSocket) -> None:
        """Process RPC requests through websocket."""
        try:
            await websocket.accept()

            async def _process_rpc(request: str) -> None:
                depends = (
                    depends_middleware({**websocket.headers})
                    if depends_middleware
                    else {}
                )
                rpc_response = await rpc.process_request_async(request, depends)
                if rpc_response is not None:
                    await websocket.send_text(rpc_response)

            while True:
                data = await websocket.receive_text()
                asyncio.create_task(_process_rpc(data))
        except WebSocketDisconnect:
            pass


def _add_http_api_url(
    rpc: RPCServer, api_path: str, depends_middleware: DependsMiddleware
) -> None:
    @app.post(api_path, response_model=ErrorResponse | ResultResponse | None)
    async def http_process_rpc(request: Request, rpc_request: RequestType) -> Response:
        """Process RPC request through HTTP server."""
        depends = depends_middleware({**request.headers}) if depends_middleware else {}
        rpc_response = await rpc.process_request_async(
            rpc_request.model_dump_json(), depends
        )
        return Response(content=rpc_response, media_type="application/json")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> _TemplateResponse:
    """Get interactive docs site."""
    te = await cache.get_templating_engine()
    context = {
        "request": request,
        "disable_api_input": cache.api_url is not None,
        "api_url": te.api_url,
        "te": te,
        "examples": util.get_examples(te.rpc.methods),
        "servers": cache.servers,
    }
    return templates.TemplateResponse("index.html", {**context, **base_context})


@app.get("/docs/get-server", response_class=HTMLResponse)
async def discover(request: Request) -> _TemplateResponse:
    """Get OpenRPC docs."""
    api_url = request.query_params.get("api-url")
    trigger = request.path_params["trigger"]
    te = await cache.get_templating_engine(api_url, refresh=trigger == "click")
    examples = util.get_examples(te.rpc.methods)
    context = {"request": request, "te": te, "examples": examples}
    return templates.TemplateResponse("openrpc_docs.html", {**context, **base_context})


@app.get("/docs/discover-{trigger}", response_class=HTMLResponse)
async def discover(request: Request) -> _TemplateResponse:
    """Get OpenRPC docs."""
    api_url = request.query_params.get("api-url")
    trigger = request.path_params["trigger"]
    te = await cache.get_templating_engine(api_url, refresh=trigger == "click")
    examples = util.get_examples(te.rpc.methods)
    context = {"request": request, "te": te, "examples": examples}
    return templates.TemplateResponse("openrpc_docs.html", {**context, **base_context})


@app.get("/docs/try-it-modal/{method_idx}", response_class=HTMLResponse)
async def try_it(request: Request) -> _TemplateResponse:
    """Get "Try it out" modal for a method."""
    api_url = request.query_params.get("api-url")
    method_idx = request.path_params["method_idx"]
    te = await cache.get_templating_engine(api_url)
    method = te.get_method(int(method_idx))
    context = {
        "request": request,
        "method": method,
        "method_id": method_idx,
        "get_any_default": util.get_any_default,
    }
    return templates.TemplateResponse("modals/try_it.html", {**context, **base_context})


@app.get(
    "/docs/add-{item_type}-item/{method_id}/{param_id}/{input_id}",
    response_class=HTMLResponse,
)
async def add_item(request: Request) -> _TemplateResponse:
    """Get "Try it out" modal for a method."""
    api_url = request.query_params.get("api-url")
    item_count = request.query_params.get("item-count")
    method_id = request.path_params["method_id"]
    param_id = int(request.path_params["param_id"])
    input_id = request.path_params["input_id"]
    item_type = request.path_params["item_type"]
    te = await cache.get_templating_engine(api_url)
    method = te.get_method(int(method_id))

    # Get schema for this param.
    schema: SchemaType = Schema()
    for i, param in enumerate(method.params):
        if i == param_id:
            schema = param.schema_
    schema = schema.items if not isinstance(schema, bool) and schema.items else schema

    # Collections at top level of `any_of` need to be treated as one
    # level deeper.
    input_depth = input_id.removeprefix(f"{method_id}_{param_id}")
    if input_depth.startswith("__"):
        input_depth = f"_{int(input_depth[2])+1}_{input_depth[2:]}"
    # Get input ids to get proper schema in schema tree.
    input_ids = input_depth.split("_")
    # Always `1` for array items because`we don't want items 2+ of an
    # array to be treated as a deeper depth in schema tree.
    input_ids = ["1" if it.startswith("array") else it for it in input_ids if it != ""]
    # Remove `val` prefix from object values.
    input_ids = [it.replace("val", "") for it in input_ids]
    schema = util.get_schema_from_input_ids(schema, map(int, input_ids))

    if item_type != "recursive":
        input_id = f"{input_id}_array{item_count}"

    context = {
        "request": request,
        "method_id": method_id,
        "param_id": str(param_id),
        "schema": schema,
        "input_id": input_id,
        "minimalize": True,
        "get_any_default": util.get_any_default,
    }
    if item_type == "object":
        return templates.TemplateResponse(
            "schema_form/object.html", {**context, **base_context}
        )
    return templates.TemplateResponse(
        "schema_form/form.html", {**context, **base_context}
    )


@app.get("/openrpc.json", response_model=OpenRPC)
async def openrpc_doc(request: Request) -> JSONResponse:
    """Get raw OpenRPC JSON document."""
    api_url = request.query_params.get("api-url")
    te = await cache.get_templating_engine(api_url)
    return JSONResponse(content=await _discover(te))


@app.post("/rpc-api")
async def api_pass_through(request: Request) -> Response:
    """Pass RPC requests to RPC server and get response."""
    api_url = request.query_params.get("api-url")
    te = await cache.get_templating_engine(api_url)
    response = await te.process_request(await request.json(), request.headers)
    return Response(content=response, media_type="application/json")


@app.get("/download-client")
async def api_pass_through(request: Request) -> FileResponse:
    """Download a generated client for this API."""
    # Get RPC data and target language.
    api_url = request.query_params.get("api-url")
    language = request.query_params.get("language")
    te = await cache.get_templating_engine(api_url)
    rpc = OpenRPC(**await _discover(te))
    lang_option = Language.PYTHON if language == "Python" else Language.TYPESCRIPT

    # Make generated out directories if they don't exist.
    out = root.joinpath("static/out")
    out.mkdir(exist_ok=True)
    lang_out = out.joinpath(language.lower())
    lang_out.mkdir(exist_ok=True)
    transport = "http" if api_url.startswith("http") else "ws"
    client_name = caseswitcher.to_kebab(rpc.info.title) + f"{transport}-client"
    client_dir = lang_out.joinpath(client_name)
    filename = f"{client_name}-{rpc.info.version}-{lang_option.value}.zip"
    zip_file = lang_out.joinpath(filename)

    # If client doesn't exist, generate and zip it.
    if not zip_file.exists():
        generate(rpc, lang_option, api_url, out)
        shutil.make_archive(zip_file.as_posix().removesuffix(".zip"), "zip", client_dir)

    # Serve the client zipfile.
    return FileResponse(zip_file, headers={"Content-Disposition": filename})


async def _discover(te: TemplatingEngine) -> dict[str, Any]:
    discover_request = {"id": 1, "method": "rpc.discover", "jsonrpc": "2.0"}
    response = await te.process_request(discover_request)
    return json.loads(response)["result"]
