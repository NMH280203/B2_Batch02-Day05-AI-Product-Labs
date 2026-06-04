import os
from pathlib import Path

# Load BASE_PROMPT dynamically from artifacts/system_prompt.md
_prompt_path = Path(__file__).parent.parent / "artifacts" / "system_prompt.md"
if _prompt_path.exists():
    BASE_PROMPT = _prompt_path.read_text(encoding="utf-8")
else:
    # Fallback in case of path issues
    BASE_PROMPT = """Bạn là trợ lý AI chuyên gợi ý món ăn và nhà hàng tại Việt Nam.
Nhiệm vụ: hiểu nhu cầu ăn uống của người dùng và đưa ra gợi ý phù hợp nhất."""

