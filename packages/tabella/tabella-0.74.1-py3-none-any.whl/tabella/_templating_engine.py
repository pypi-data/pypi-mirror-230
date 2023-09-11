"""Used to handle templating variables and string sanitization."""
import inspect
import json
from copy import copy
from typing import Any

import httpx
import websockets
from openrpc import Contact, Method, OpenRPC, RPCServer, SchemaType, Tag
from starlette.datastructures import Headers

from tabella._util import RequestProcessor

_rpc_server = RPCServer(
    title="Methodology",
    version="1.0.0",
    description="OpenRPC Interactive API Documentation",
    contact=Contact(
        name="Methodology Source Code",
        url="https://gitlab.com/mburkard/tabella",
    ),
)


class TemplatingEngine:
    """Get templating variables."""

    def __init__(
        self, api_url: str | None, request_processor: RequestProcessor | None = None
    ) -> None:
        self.tags: list[Tag] = []
        self.api_url = api_url
        self.request_processor = request_processor
        self.rpc = OpenRPC(**_rpc_server.discover())

    async def init(self) -> None:
        """Init a Templating Engine."""
        if self.api_url is None:
            self.rpc = await self._get_rpc(OpenRPC(**_rpc_server.discover()))
        else:
            self.rpc = await self._get_rpc()
        for method in self.rpc.methods:
            for tag in method.tags or []:
                if tag not in self.tags:
                    self.tags.append(tag)

    def get_tags(self, method: Method) -> list[int]:
        """Gat indexes of tags for the given method."""
        return [
            i for i, tag in enumerate(self.tags or []) if tag in (method.tags or [])
        ]

    def get_method(self, idx: int) -> Method:
        """Gat method with the given index."""
        for i, method in enumerate(self.rpc.methods):
            if i == idx:
                return method
        msg = f"No method at index {idx}."
        raise ValueError(msg)

    async def _get_rpc(self, rpc_doc: OpenRPC | None = None) -> OpenRPC:
        if not rpc_doc:
            discover = {"id": 1, "method": "rpc.discover", "jsonrpc": "2.0"}
            resp = json.loads(await self.process_request(discover))
            rpc_doc = OpenRPC(**resp["result"])
        if rpc_doc.components is None or rpc_doc.components.schemas is None:
            return rpc_doc
        for method in rpc_doc.methods:
            for param in method.params:
                param.schema_ = resolve_references(
                    param.schema_, rpc_doc.components.schemas
                )
            method.result.schema_ = resolve_references(
                method.result.schema_, rpc_doc.components.schemas
            )
        return rpc_doc

    async def process_request(
        self, request: dict[str, Any], headers: Headers | dict | None = None
    ) -> str:
        """Send a request to the RPC API and get a response."""
        headers = headers or {}

        # Get method from methodId.
        if self.rpc:
            for i, method in enumerate(self.rpc.methods):
                if str(i) == request["method"]:
                    request["method"] = method.name
        rpc_request = json.dumps(request)

        # Custom Request Processor.
        if self.request_processor is not None:
            resp = self.request_processor(rpc_request, headers)
            return await resp if inspect.isawaitable(resp) else resp

        # HTTP
        headers = {"Content-Type": "application/json"}
        if api_key := headers.get("api_key"):
            headers["api_key"] = api_key
        if self.api_url and self.api_url.startswith("http"):
            client = httpx.AsyncClient()
            return (
                await client.post(
                    self.api_url,
                    content=rpc_request,
                    headers=headers,
                )
            ).content.decode()

        # Websocket
        if self.api_url and self.api_url.startswith("ws"):
            # Type ignore because `websockets` is bad.
            async with websockets.connect(  # type: ignore
                self.api_url, extra_headers=headers
            ) as websocket:
                await websocket.send(rpc_request)
                return await websocket.recv()
        msg = "Invalid API URL."
        raise ValueError(msg)


def resolve_references(
    schema: SchemaType,
    schemas: dict[str, SchemaType],
    recurring: list[SchemaType] | None = None,
) -> SchemaType:
    """Resolve JSON Schema references."""
    if isinstance(schema, bool):
        return schema

    # Don't mutate original schema, will cause infinite recursion on
    # subsequent `resolve_references` calls with the same root schema.
    schema = copy(schema)

    # Don't mutate original recursion list, if mutated sibling schemas
    # will show as recursive for all but the first one.
    recurring = copy(recurring) if recurring else []

    if schema.ref:
        ref = schema.ref.removeprefix("#/components/schemas/")
        resolved_ref = copy(schemas[ref])
        if isinstance(resolved_ref, bool):
            return resolved_ref
        if schema in recurring:
            # Set `ref` to indicate recursion.
            resolved_ref.ref = schema.ref
            return resolved_ref
        resolved_ref.ref = None
        recurring.append(schema)
        schema = resolved_ref

    # Lists of schemas.
    for attr in ["all_of", "any_of", "one_of", "prefix_items"]:
        resolved = []
        for child_schema in getattr(schema, attr) or []:
            resolved_option = resolve_references(child_schema, schemas, recurring)
            resolved.append(resolved_option)
        if resolved:
            setattr(schema, attr, resolved)

    # Single schemas.
    for attr in [
        "not_",
        "property_names",
        "items",
        "contains",
        "if_",
        "then",
        "else_",
        "additional_properties",
    ]:
        if getattr(schema, attr):
            setattr(
                schema,
                attr,
                resolve_references(getattr(schema, attr), schemas, recurring),
            )

    # Dict of schemas.
    for attr in ["properties", "pattern_properties", "defs", "dependent_schemas"]:
        resolved_dict = {}
        for name, child_schema in (getattr(schema, attr) or {}).items():
            resolved_dict[name] = resolve_references(child_schema, schemas, recurring)
        if resolved_dict:
            setattr(schema, attr, resolved_dict)

    return schema
