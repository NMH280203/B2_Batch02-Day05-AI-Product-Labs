from datetime import datetime
from models.schemas import UserContext
from prompt.system_prompt import BASE_PROMPT


def build_system_prompt(context: UserContext) -> str:
    parts = [BASE_PROMPT]

    # Thời gian hiện tại
    hour = datetime.now().hour
    if context.meal_time:
        meal_map = {
            "breakfast": "bữa sáng",
            "lunch": "bữa trưa",
            "dinner": "bữa tối",
            "snack": "bữa nhẹ/snack",
        }
        parts.append(f"Thời điểm: {meal_map[context.meal_time]}.")
    else:
        if 5 <= hour < 10:
            parts.append("Thời điểm hiện tại: buổi sáng (phù hợp bữa sáng).")
        elif 10 <= hour < 14:
            parts.append("Thời điểm hiện tại: buổi trưa.")
        elif 14 <= hour < 18:
            parts.append("Thời điểm hiện tại: buổi chiều (phù hợp snack hoặc bữa nhẹ).")
        else:
            parts.append("Thời điểm hiện tại: buổi tối.")

    if context.location:
        addr = context.location.address or f"tọa độ ({context.location.lat:.4f}, {context.location.lng:.4f})"
        parts.append(f"Vị trí người dùng: {addr}.")

    if context.budget:
        parts.append(f"Ngân sách: khoảng {context.budget:,} VND mỗi người.")

    if context.people:
        parts.append(f"Số người: {context.people} người.")

    if context.purpose:
        purpose_map = {
            "family": "ăn cùng gia đình",
            "date": "hẹn hò",
            "friends": "đi với bạn bè",
            "work": "gặp gỡ công việc",
            "solo": "ăn một mình",
        }
        parts.append(f"Mục đích: {purpose_map[context.purpose]}.")

    if context.preferences:
        parts.append(f"Sở thích ăn uống: {', '.join(context.preferences)}.")

    if context.allergies:
        parts.append(
            f"⚠️ DỊ ỨNG / KIÊNG KỊ QUAN TRỌNG: {', '.join(context.allergies)}. "
            "Luôn lưu ý và cảnh báo user kiểm tra lại với quán trước khi đặt."
        )

    return "\n".join(parts)
