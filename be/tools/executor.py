import sys
from tools import TOOL_HANDLERS


async def execute(tool_name: str, tool_input: dict) -> dict:
    """
    Route tool_name tới handler tương ứng dựa trên TOOL_HANDLERS.
    """
    try:
        # Xử lý các trường hợp đặc biệt không chạy trực tiếp handler
        if tool_name == "ask_user_for_context":
            return {
                "ask": True,
                "field": tool_input.get("field", ""),
                "message": tool_input.get("message", "Bạn có thể cho tôi biết thêm không?"),
            }
        elif tool_name in ("run_food_agent", "run_restaurant_agent"):
            return {"status": f"delegated_to_{tool_name.split('_')[1]}_agent"}

        handler = TOOL_HANDLERS.get(tool_name)
        if not handler:
            print(f"[ERROR] Unknown tool: {tool_name}", file=sys.stderr)
            return {"error": f"Unknown tool: {tool_name}"}

        return await handler(tool_input)

    except Exception as e:
        print(f"[ERROR] Tool executor failed for {tool_name}: {e}", file=sys.stderr)
        return {"error": str(e)}

