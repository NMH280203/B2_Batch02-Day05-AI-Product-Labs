import os
import json
import sys
import asyncio
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv(override=True)

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemma-4-31b-it")
FALLBACK_MODEL_NAMES = [
    MODEL_NAME,
    "gemini-2.5-flash",
    "gemini-2.0-flash",
]

_raw_key = os.getenv("GEMINI_API_KEY", "")
# Chế độ mock khi chưa có key thật
MOCK_MODE = not _raw_key or _raw_key.startswith("your-")
_client: genai.Client | None = None

if MOCK_MODE:
    print("[INFO] GEMINI_API_KEY chưa có — chạy MOCK MODE, AI sẽ trả dữ liệu demo.", file=sys.stderr)
else:
    _client = genai.Client(api_key=_raw_key)


# ─────────────────────────────────────────────
# Mock data cố định cho demo không cần API key
# ─────────────────────────────────────────────

MOCK_FOOD_RESPONSE = {
    "foods": [
        {
            "name": "Bún riêu cua",
            "category": "Bún",
            "description": "Bún riêu nước trong, vị thanh mát, dễ ăn, nhẹ bụng",
            "estimated_price": 55000,
            "reason": "Phù hợp khi mệt, không quá nặng bụng, dễ tiêu",
            "tags": ["nhẹ", "thanh mát", "dễ ăn"],
        },
        {
            "name": "Cháo gà hành gừng",
            "category": "Cháo",
            "description": "Cháo gà ấm bụng, dễ tiêu hóa, bổ dưỡng",
            "estimated_price": 45000,
            "reason": "Lý tưởng khi cơ thể mệt mỏi — nhẹ dạ dày, ngọt tự nhiên",
            "tags": ["nhẹ dạ dày", "dễ tiêu", "phục hồi sức"],
        },
        {
            "name": "Salad gà trái cây",
            "category": "Salad",
            "description": "Salad gà tươi mát, giàu protein, ít dầu mỡ",
            "estimated_price": 70000,
            "reason": "Ăn nhẹ nhưng đủ no, tốt cho sức khỏe",
            "tags": ["lành mạnh", "ít dầu", "tươi mát"],
        },
    ],
    "food_names": ["Bún riêu cua", "Cháo gà", "Salad gà"],
}

MOCK_FINAL_TEXT = (
    "Mình hiểu bạn đang mệt và muốn ăn nhẹ nhé! 😊\n\n"
    "Dựa trên ngân sách ~80k, mình gợi ý 3 món:\n\n"
    "🍜 **Bún riêu cua** (~55k) — Nước dùng thanh, dễ ăn, không nặng bụng.\n"
    "🍲 **Cháo gà hành gừng** (~45k) — Ấm bụng, dễ tiêu — lý tưởng khi mệt.\n"
    "🥗 **Salad gà** (~70k) — Tươi mát, lành mạnh nhưng vẫn no.\n\n"
    "Bạn muốn mình tìm quán gần bạn không? Cho mình biết vị trí nhé! 📍"
)


# ─────────────────────────────────────────────
# Mock response object để agents xử lý
# ─────────────────────────────────────────────

class _MockPart:
    def __init__(self, text: str = "", function_call=None):
        self.text = text
        self.function_call = function_call

class _MockContent:
    def __init__(self, parts):
        self.parts = parts

class _MockCandidate:
    def __init__(self, parts):
        self.content = _MockContent(parts)

class _MockResponse:
    def __init__(self, text: str = ""):
        self._text = text
        self.candidates = [_MockCandidate([_MockPart(text=text)])]

    @property
    def text(self):
        return self._text


class _MockStream:
    """Stream giả cho mock mode."""
    def __init__(self, text: str):
        self._text = text

    def __iter__(self):
        words = self._text.split(" ")
        for i, word in enumerate(words):
            chunk_text = word + (" " if i < len(words) - 1 else "")
            yield _MockResponse(chunk_text)

    async def __aiter__(self):
        # Stream từng từ để giả lập streaming
        for chunk in self:
            yield chunk


# ─────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────

def _to_genai_messages(system: str, messages: list[dict]) -> list[types.Content]:
    """Chuyển messages list sang google.genai Content format."""
    result: list[types.Content] = []
    for i, msg in enumerate(messages):
        role = "user" if msg["role"] == "user" else "model"
        content = msg["content"]
        if i == 0 and role == "user":
            content = f"[System Instructions]: {system}\n\n{content}"
        result.append(types.Content(role=role, parts=[types.Part(text=content)]))
    return result


async def call(
    system: str,
    messages: list[dict],
    tools: list | None = None,
    stream: bool = False,
) -> any:
    """
    Gọi Gemini API. Nếu MOCK_MODE → trả response giả.
    """
    if MOCK_MODE:
        if stream:
            return _MockStream(MOCK_FINAL_TEXT)
        return _MockResponse(MOCK_FINAL_TEXT)

    contents = _to_genai_messages(system, messages)
    config = types.GenerateContentConfig(
        max_output_tokens=4096,
        temperature=0.7,
    )
    if tools:
        config.tools = tools

    last_error: Exception | None = None
    for model_name in FALLBACK_MODEL_NAMES:
        try:
            if stream:
                return await _client.aio.models.generate_content_stream(
                    model=model_name,
                    contents=contents,
                    config=config,
                )
            return await _client.aio.models.generate_content(
                model=model_name,
                contents=contents,
                config=config,
            )
        except Exception as e:
            last_error = e
            print(f"[WARN] LLM model {model_name} failed: {e}", file=sys.stderr)
            continue

    print(f"[ERROR] LLM call failed after fallbacks: {last_error}", file=sys.stderr)
    raise last_error if last_error else RuntimeError("LLM call failed")


async def call_json(system: str, prompt: str) -> dict:
    """
    Gọi LLM với yêu cầu trả JSON. Nếu MOCK_MODE → trả mock foods.
    """
    if MOCK_MODE:
        return MOCK_FOOD_RESPONSE

    full_prompt = (
        f"{system}\n\n"
        f"{prompt}\n\n"
        "Hãy trả về KẾT QUẢ JSON THUẦN (không có markdown, không có giải thích). "
        "Chỉ trả về JSON object hợp lệ."
    )

    config = types.GenerateContentConfig(
        max_output_tokens=2048,
        temperature=0.3,
        response_mime_type="application/json",
    )

    response = None
    last_error: Exception | None = None
    for model_name in FALLBACK_MODEL_NAMES:
        try:
            response = _client.models.generate_content(
                model=model_name,
                contents=[types.Content(role="user", parts=[types.Part(text=full_prompt)])],
                config=config,
            )
            break
        except Exception as e:
            last_error = e
            print(f"[WARN] call_json model {model_name} failed: {e}", file=sys.stderr)
            continue

    if response is None:
        raise last_error if last_error else RuntimeError("call_json failed")

    try:
        text = response.text.strip() if response.text else "{}"

        if text.startswith("```"):
            lines = text.splitlines()
            start = 1
            end = len(lines) - 1 if lines[-1].strip() == "```" else len(lines)
            text = "\n".join(lines[start:end])

        return json.loads(text)

    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON parse failed: {e}", file=sys.stderr)
        return {}
    except Exception as e:
        print(f"[ERROR] call_json failed: {e}", file=sys.stderr)
        return {}
