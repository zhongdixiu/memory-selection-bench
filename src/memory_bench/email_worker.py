from __future__ import annotations

import json
import os
import sys
import traceback
from pathlib import Path
from typing import Any


PREFIX = "@@EMAIL_BENCH@@"


def emit(value: dict[str, Any]) -> None:
    print(PREFIX + json.dumps(value, ensure_ascii=False), flush=True)


class DisabledMemory:
    enabled = False

    def search_memory(self, **_: Any) -> str:
        return ""


def build_agent(context: str, user_id: str):
    root = Path(os.environ["MEMORY_BENCH_EMAIL_ROOT"])
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    import agent.email_agent as email_agent
    from agentscope.agent import ReActAgent
    from agentscope.formatter import OpenAIChatFormatter
    from agentscope.memory import InMemoryMemory
    from agentscope.message import TextBlock
    from agentscope.model import OpenAIChatModel
    from agentscope.tool import ToolResponse

    def imap_search_139(subject: str = None, limit: int = 5, start_date: str = None, end_date: str = None, recent: str = None, from_email: str = None) -> ToolResponse:
        """Synthetic benchmark IMAP search; never connects to a mailbox."""
        return ToolResponse(content=[TextBlock(type="text", text="Benchmark mailbox is empty.")])

    def imap_fetch_content(uid: str) -> ToolResponse:
        """Synthetic benchmark IMAP fetch; never connects to a mailbox."""
        return ToolResponse(content=[TextBlock(type="text", text="No synthetic message for this UID.")])

    def smtp_send_139(to: str, subject: str, body: str) -> ToolResponse:
        """Block every SMTP side effect during the benchmark."""
        return ToolResponse(content=[TextBlock(type="text", text="SMTP is disabled by the benchmark.")])

    email_agent.imap_search_139 = imap_search_139
    email_agent.imap_fetch_content = imap_fetch_content
    email_agent.smtp_send_139 = smtp_send_139
    email_agent.DEFAULT_MODEL = os.environ["MEMORY_BENCH_LLM_MODEL"]
    email_agent.init_agentscope()
    model = OpenAIChatModel(
        model_name=os.environ["MEMORY_BENCH_LLM_MODEL"],
        api_key=os.environ["DASHSCOPE_API_KEY"],
        stream=False,
        client_kwargs={"base_url": os.environ["MEMORY_BENCH_LLM_BASE_URL"]},
        generate_kwargs={"temperature": 0.0, "extra_body": {"enable_thinking": False}},
    )
    agent = ReActAgent(
        name="邮件助手",
        sys_prompt=email_agent.compose_system_prompt(session_context=context),
        model=model,
        formatter=OpenAIChatFormatter(),
        toolkit=email_agent.create_toolkit(),
        memory=InMemoryMemory(),
    )
    agent._tool_trace = []
    agent.register_instance_hook("post_acting", "record_tool_trace", email_agent._record_tool_trace)
    agent._profile_user_id = user_id
    return agent


def invoke(payload: dict[str, Any]) -> dict[str, Any]:
    import service
    from tools.memory_tools import configure_memory_runtime

    configure_memory_runtime(repository=service.profile_service.repository, honcho=DisabledMemory())
    agent = build_agent(str(payload.get("context") or ""), str(payload.get("user_id") or "U1"))
    result = service.invoke_agent_with_retry(
        agent,
        str(payload["prompt"]),
        user_id=str(payload.get("user_id") or "U1"),
        session_id=str(payload["session_id"]),
    )
    return {"text": str(result.get("text") or ""), "tool_trace": list(result.get("tool_trace") or []), "skill_route": service.infer_skill_route(str(result.get("text") or ""), list(result.get("tool_trace") or []), message=str(payload["prompt"]))}


def main() -> int:
    try:
        root = Path(os.environ["MEMORY_BENCH_EMAIL_ROOT"])
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
        import service  # noqa: F401 - validates the actual Agent entrypoint
        emit({"ok": True, "ready": True})
    except Exception as exc:
        emit({"ok": False, "error": str(exc), "traceback": traceback.format_exc()})
        return 1
    for line in sys.stdin:
        try:
            emit({"ok": True, "data": invoke(json.loads(line))})
        except Exception as exc:
            emit({"ok": False, "error": str(exc), "traceback": traceback.format_exc()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
