import json
import os

from openai import OpenAI

from . import tools

SYSTEM_PROMPT = """你是水井 USR 智慧養殖與風雲客棧服務 AI。
請用繁體中文、清楚、務實地回答。當使用者詢問魚塭、水質、溫度、pH、溶氧、鹽度或異常狀態時，優先使用工具查詢資料，不要憑空編數字。
當使用者詢問課程、活動、故事、USR 成果、科技專案、交通或聯絡資訊時，也要優先使用工具查詢網站資料。
回答時請先講結論，再列出關鍵資料與下一步建議。"""

MAX_TOOL_LOOPS = 5


def _client() -> OpenAI:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("缺少 OPENAI_API_KEY，請在 .env 設定後重新啟動伺服器。")
    return OpenAI(api_key=api_key)


def chat(user_message: str, history: list[dict] | None = None) -> str:
    messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    client = _client()

    for _ in range(MAX_TOOL_LOOPS):
        response = client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            messages=messages,
            tools=tools.TOOL_SCHEMAS,
        )
        msg = response.choices[0].message

        if not msg.tool_calls:
            return msg.content or ""

        messages.append(msg.model_dump(exclude_none=True))
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments or "{}")
            result = tools.dispatch(call.function.name, args)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(result, ensure_ascii=False),
                }
            )

    return "工具查詢次數過多，請把問題縮小一點再試一次。"
