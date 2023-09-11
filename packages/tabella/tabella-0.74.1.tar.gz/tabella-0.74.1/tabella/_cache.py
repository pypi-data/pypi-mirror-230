"""Provides RPCInterface to communicate with RPC server."""
import os
from typing import Optional

from tabella._templating_engine import TemplatingEngine
from tabella._util import RequestProcessor


class MethodologyCache:
    """Handle communication with RPC server."""

    _instance: Optional["MethodologyCache"] = None

    def __init__(self) -> None:
        if MethodologyCache._instance:
            msg = "Do not instantiate RPCInterface directly, call `get_instance()`"
            raise ValueError(msg)
        self.api_url: str | None = os.environ.get("API_URL")
        self.cache: dict[str | None, TemplatingEngine] = {}
        self.request_processor: RequestProcessor | None = None

    @staticmethod
    def get_instance() -> "MethodologyCache":
        """Get or create instance of RPCInterface."""
        if MethodologyCache._instance:
            return MethodologyCache._instance
        MethodologyCache._instance = MethodologyCache()
        return MethodologyCache._instance

    def set_request_processor(
        self, request_processor: RequestProcessor, url: str
    ) -> None:
        """Set RPCServer to use for discovery and request processing."""
        self.request_processor = request_processor
        self.api_url = url

    async def get_templating_engine(
        self, api_url: str | None = None, *, refresh: bool = False
    ) -> TemplatingEngine:
        """Get a templating engine for the given API URL."""
        api_url = self.api_url or api_url
        if (te := self.cache.get(api_url)) and not refresh:
            return te
        if self.api_url and self.request_processor:
            self.cache[api_url] = TemplatingEngine(self.api_url, self.request_processor)
        elif api_url is None:
            self.cache[api_url] = TemplatingEngine(None)
        else:
            self.cache[api_url] = TemplatingEngine(api_url)
        await self.cache[api_url].init()
        return self.cache[api_url]
