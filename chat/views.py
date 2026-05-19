import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from . import llm

MAX_HISTORY_ITEMS = 10


@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):
    try:
        body = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "請送出正確的 JSON 內容。"}, status=400)

    message = (body.get("message") or "").strip()
    if not message:
        return JsonResponse({"error": "訊息不能是空白。"}, status=400)

    history = request.session.get("aqua_chat_history", [])

    try:
        reply = llm.chat(message, history=history)
    except Exception as exc:  # noqa: BLE001
        return JsonResponse(
            {"error": f"AI 助理暫時無法回應：{type(exc).__name__}: {exc}"},
            status=500,
        )

    history.extend(
        [
            {"role": "user", "content": message},
            {"role": "assistant", "content": reply},
        ]
    )
    request.session["aqua_chat_history"] = history[-MAX_HISTORY_ITEMS:]
    request.session.modified = True

    return JsonResponse({"reply": reply})


@csrf_exempt
@require_http_methods(["POST"])
def reset_chat_api(request):
    request.session.pop("aqua_chat_history", None)
    request.session.modified = True
    return JsonResponse({"ok": True})
