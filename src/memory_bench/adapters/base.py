from __future__ import annotations

from typing import Protocol

from memory_bench.contracts import Principal, SearchRequest, SearchResult, Track, WriteReceipt, WriteRequest


class MemoryAdapter(Protocol):
    candidate: str
    track: Track

    async def start(self) -> None: ...
    async def close(self) -> None: ...
    async def health(self) -> dict: ...
    async def write(self, request: WriteRequest, principal: Principal) -> WriteReceipt: ...
    async def search(self, request: SearchRequest, principal: Principal) -> SearchResult: ...

