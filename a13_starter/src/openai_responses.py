from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from a13_starter.src.settings import (
    get_openai_api_key,
    get_openai_base_url,
    get_openai_model,
    get_openai_timeout_seconds,
    get_llm_provider,
)


class OpenAIResponsesError(RuntimeError):
    pass


class OpenAIResponsesClient:
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        timeout_seconds: int | None = None,
    ) -> None:
        self.api_key = api_key or get_openai_api_key()
        self.model = model or get_openai_model()
        self.base_url = (base_url or get_openai_base_url()).rstrip("/")
        self.timeout_seconds = timeout_seconds or get_openai_timeout_seconds()
        self.provider = get_llm_provider()

        if not self.api_key:
            raise OpenAIResponsesError(
                "LLM API key is not configured. Set OPENAI_API_KEY or DASHSCOPE_API_KEY."
            )

    def create_structured_output(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema_name: str,
        schema: dict[str, Any],
        reasoning_effort: str = "medium",
    ) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "input": self._build_input(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                schema_name=schema_name,
                schema=schema,
            ),
            "store": False,
        }
        if self.provider == "dashscope":
            payload["result_format"] = "message"
        else:
            payload["reasoning"] = {"effort": reasoning_effort}
        if self.provider == "openai":
            payload["text"] = {
                "format": {
                    "type": "json_schema",
                    "name": schema_name,
                    "strict": True,
                    "schema": schema,
                }
            }

        request = urllib.request.Request(
            f"{self.base_url}/responses",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            try:
                error_body = error.read().decode("utf-8")
            except Exception:
                error_body = str(error)
            raise OpenAIResponsesError(f"LLM API error: {error.code} {error_body}") from error
        except urllib.error.URLError as error:
            raise OpenAIResponsesError(f"LLM API connection error: {error}") from error

        output_text = self._extract_output_text(body)
        return self._parse_json_output(output_text)

    def _build_input(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema_name: str,
        schema: dict[str, Any],
    ) -> list[dict[str, str]]:
        if self.provider == "dashscope":
            user_prompt = self._build_dashscope_json_user_prompt(
                user_prompt=user_prompt,
                schema_name=schema_name,
                schema=schema,
            )
        return [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ]

    def _build_dashscope_json_user_prompt(
        self,
        *,
        user_prompt: str,
        schema_name: str,
        schema: dict[str, Any],
    ) -> str:
        schema_text = json.dumps(schema, ensure_ascii=False, indent=2)
        return (
            f"请把下面内容解析成 `{schema_name}` JSON。\n"
            "只允许输出一个 JSON 对象，不要输出 Markdown，不要输出解释，不要使用代码块。\n"
            "字段必须与 schema 一致；没有提到的内容用 null、[] 或合理默认值。\n"
            "请严格保证返回结果可以被 json.loads 直接解析。\n\n"
            f"JSON Schema:\n{schema_text}\n\n"
            f"待解析文本:\n{user_prompt}"
        )

    def _extract_output_text(self, body: dict[str, Any]) -> str:
        error = body.get("error") if isinstance(body, dict) else None
        if isinstance(error, dict) and error.get("message"):
            raise OpenAIResponsesError(str(error["message"]))

        if isinstance(body.get("output_text"), str) and body["output_text"].strip():
            return body["output_text"].strip()

        output = body.get("output", [])
        texts: list[str] = []
        for item in output:
            for content in item.get("content", []):
                if content.get("type") == "output_text" and content.get("text"):
                    texts.append(content["text"])
        if texts:
            return "\n".join(texts).strip()

        raise OpenAIResponsesError("No text output found in model response.")

    def _parse_json_output(self, output_text: str) -> dict[str, Any]:
        candidates = [output_text.strip()]
        stripped = output_text.strip()
        if stripped.startswith("```"):
            lines = stripped.splitlines()
            if len(lines) >= 3:
                candidates.append("\n".join(lines[1:-1]).strip())

        first_brace = stripped.find("{")
        last_brace = stripped.rfind("}")
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            candidates.append(stripped[first_brace : last_brace + 1].strip())

        seen: set[str] = set()
        for candidate in candidates:
            if not candidate or candidate in seen:
                continue
            seen.add(candidate)
            try:
                parsed = json.loads(candidate)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                return parsed

        raise OpenAIResponsesError(f"Model returned non-JSON structured output: {output_text}")

    def chat(self, *, system_prompt: str, user_prompt: str) -> str:
        """调用模型进行普通对话，返回纯文本响应（用于生成非结构化内容）"""
        payload = {
            "model": self.model,
            "input": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "store": False,
        }
        if self.provider == "dashscope":
            payload["result_format"] = "message"
        request = urllib.request.Request(
            f"{self.base_url}/responses",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            try:
                error_body = error.read().decode("utf-8")
            except Exception:
                error_body = str(error)
            raise OpenAIResponsesError(f"LLM API error: {error.code} {error_body}") from error
        except urllib.error.URLError as error:
            raise OpenAIResponsesError(f"LLM API connection error: {error}") from error
        return self._extract_output_text(body)
