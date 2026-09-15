from __future__ import annotations

from typing import Dict, List, Optional

from mem0.llms.openai import OpenAILLM
from mem0.embeddings.openai import OpenAIEmbedding


class QwenCompatLLM(OpenAILLM):
    """Configuration-only shim that forwards DashScope's thinking switch."""

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        response_format=None,
        tools: Optional[List[Dict]] = None,
        tool_choice: str = "auto",
        **kwargs,
    ):
        extra_body = dict(kwargs.pop("extra_body", {}) or {})
        extra_body.setdefault("enable_thinking", False)
        return super().generate_response(
            messages=messages,
            response_format=response_format,
            tools=tools,
            tool_choice=tool_choice,
            extra_body=extra_body,
            **kwargs,
        )


class SiliconFlowEmbedding(OpenAIEmbedding):
    """OpenAI-compatible embedding without the optional dimensions field.

    BAAI/bge-m3 has a fixed 1024-dimensional output. The dimension remains in
    Mem0's vector-store config, but SiliconFlow does not need a matryoshka
    ``dimensions`` request argument.
    """

    def __init__(self, config=None):
        super().__init__(config)
        self._pass_dimensions_to_api = False
