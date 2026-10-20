"""
Thin LLM client abstraction.

Every other module calls `get_llm_client().complete_json(...)` or
`.complete_text(...)` - none of them import the `openai` package
directly. That means switching providers (Anthropic, Azure OpenAI,
local model, etc.) only requires editing this file.

If OPENAI_API_KEY is not set, `llm_enabled` is False and callers fall
back to their own rule-based logic so the product still works end to
end without any AI key configured.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from app.config import get_settings

logger = logging.getLogger("app.ai")
settings = get_settings()


class LLMClient:
    def __init__(self):
        self.enabled = settings.llm_enabled
        self._client = None
        if self.enabled:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=settings.OPENAI_API_KEY)
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("Failed to initialize OpenAI client, falling back to rule-based mode: %s", exc)
                self.enabled = False

    def complete_json(self, system_prompt: str, user_prompt: str, max_tokens: int = 1200) -> Optional[Dict[str, Any]]:
        """Ask the LLM for a JSON object. Returns None on any failure so
        callers can fall back gracefully - never raises to the caller."""
        if not self.enabled:
            return None
        try:
            response = self._client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as exc:
            logger.warning("LLM JSON completion failed, falling back: %s", exc)
            return None

    def complete_with_tools(
        self,
        system_prompt: str,
        user_prompt: str,
        tools: List[Dict[str, Any]],
        tool_executor,
        max_iterations: int = 3,
    ) -> Optional[Dict[str, Any]]:
        """Minimal tool-calling loop: the model picks a tool, we execute
        it locally against real data, feed the result back, and let the
        model produce a final natural-language answer. Returns
        {"answer": str, "tool_used": str|None, "evidence": dict} or None
        if the LLM is unavailable/fails (caller should fall back)."""
        if not self.enabled:
            return None
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
            tool_used = None
            evidence: Dict[str, Any] = {}

            for _ in range(max_iterations):
                response = self._client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                    temperature=0.2,
                    max_tokens=900,
                )
                msg = response.choices[0].message
                if not msg.tool_calls:
                    return {"answer": msg.content or "", "tool_used": tool_used, "evidence": evidence}

                messages.append({"role": "assistant", "content": msg.content, "tool_calls": [
                    {"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                    for tc in msg.tool_calls
                ]})

                for tc in msg.tool_calls:
                    tool_used = tc.function.name
                    try:
                        args = json.loads(tc.function.arguments or "{}")
                    except json.JSONDecodeError:
                        args = {}
                    result = tool_executor(tc.function.name, args)
                    evidence = result if isinstance(result, dict) else {"result": result}
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(result, default=str),
                    })

            return {"answer": "I gathered the data but ran out of reasoning steps - please try a more specific question.",
                    "tool_used": tool_used, "evidence": evidence}
        except Exception as exc:
            logger.warning("LLM tool-calling failed, falling back: %s", exc)
            return None


_client_singleton: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    global _client_singleton
    if _client_singleton is None:
        _client_singleton = LLMClient()
    return _client_singleton
