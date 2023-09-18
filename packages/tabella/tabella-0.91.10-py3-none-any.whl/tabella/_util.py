"""Misc functions."""
import asyncio
from typing import Any, Awaitable, Callable, Iterable

import lorem_pysum
from jsonrpcobjects.objects import ParamsRequest, Request, ResultResponse
from openrpc import Example, Method, ParamStructure, Schema, SchemaType

_Security = dict[str, list[str]] | None
_Depends = dict[str, Any]
Middleware = Callable[
    [dict[str, str]], tuple[_Depends, _Security] | Awaitable[tuple[_Depends, _Security]]
]
AsyncMiddleware = Callable[[dict[str, str]], Awaitable[tuple[_Depends, _Security]]]
RequestProcessor = Callable[[str, dict[str, Any]], Awaitable[str | None]]


def get_schema_from_input_ids(
    schema: SchemaType, input_ids: Iterable[int]
) -> SchemaType:
    """Get the appropriate schema tree from input ids."""
    for id_ in input_ids:
        schema = _get_schema_from_input_id(schema, id_)
    return schema


def _get_schema_from_input_id(schema: SchemaType, input_id: int) -> SchemaType:
    """Get the appropriate schema from an input id."""
    if isinstance(schema, bool):
        return schema
    if schema.items:
        return schema.items
    if schema.additional_properties:
        return schema.additional_properties
    if schema.any_of:
        return schema.any_of[input_id - 1]
    return schema


def get_examples(methods: list[Method]) -> dict[str, tuple[str, str]]:
    """Get request/response examples for each method with examples.

    The keys in the returned dictionary will be method names, the values
    will be a tuple of (request example, response example).
    """
    examples = {}
    for method in methods:
        if not method.examples:
            continue
        param_example = method.examples[0].params
        result_example = method.examples[0].result
        if param_example is None or result_example is None:
            continue
        examples[method.name] = (
            _get_example_request(method.name, param_example, method.param_structure),
            _get_example_response(result_example),
        )
    return examples


def _get_example_request(
    method: str, examples: list[Example], param_structure: ParamStructure | None
) -> str:
    """Get an example request."""
    if param_structure is ParamStructure.BY_POSITION or not all(
        e.name for e in examples
    ):
        example_params: list | dict = [e.value for e in examples]
    else:
        example_params = {e.name: e.value for e in examples}
    if example_params:
        request: Request | ParamsRequest = lorem_pysum.generate(
            ParamsRequest, overrides={"method": method, "params": example_params}
        )
    else:
        request = lorem_pysum.generate(Request, overrides={"method": method})
    return request.model_dump_json(indent=2, by_alias=True)


def _get_example_response(example: Example) -> str:
    """Get an example request."""
    return lorem_pysum.generate(
        ResultResponse, overrides={"result": example.value}
    ).model_dump_json(indent=2, by_alias=True)


def is_any(schema: SchemaType | None) -> bool:
    """Return true if the given schema is any."""
    if schema is None or schema is True:
        return True
    return schema is False or not any(
        (
            "type" in schema.model_fields_set,
            "ref" in schema.model_fields_set,
            "all_of" in schema.model_fields_set,
            "any_of" in schema.model_fields_set,
            "one_of" in schema.model_fields_set,
            "const" in schema.model_fields_set,
            "enum" in schema.model_fields_set,
            "not_" in schema.model_fields_set,
        )
    )


def get_any_default(schema: Schema) -> int:
    """Get default option of an `anyOf` schema."""
    default = 0
    if isinstance(schema, bool):
        return default
    for i, any_schema in enumerate(schema.any_of or []):
        if isinstance(any_schema, bool):
            continue
        if "default" in schema.model_fields_set and (
            (
                "const" in any_schema.model_fields_set
                and schema.default == any_schema.const
            )
            or (schema.default is None and any_schema.type == "null")
        ):
            default = i
        if any_schema.ref and i == default:
            default += 1
    return default


def get_middleware(middleware: Middleware | None) -> AsyncMiddleware | None:
    # noinspection GrazieInspection
    """Get middleware function as async function."""
    if middleware is None:
        return None

    if asyncio.iscoroutinefunction(middleware):

        async def _async_middleware(
            headers: dict[str, str]
        ) -> tuple[_Depends, _Security]:
            return await middleware(headers)

        return _async_middleware

    async def _middleware(headers: dict[str, str]) -> tuple[_Depends, _Security]:
        # Type ignore here because mypy fails to understand
        # `iscoroutinefunction` check above.
        return middleware(headers)  # type: ignore

    return _middleware
