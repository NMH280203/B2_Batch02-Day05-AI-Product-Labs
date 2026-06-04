import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv(".env")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Định nghĩa tool
func = types.FunctionDeclaration(
    name="search_food_by_criteria",
    description="Gợi ý món ăn theo tiêu chí người dùng.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "meal_time": {"type": "STRING", "description": "breakfast/lunch/dinner/snack"},
            "budget": {"type": "NUMBER", "description": "Ngân sách (VND)"},
            "preferences": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "Sở thích"},
            "weather": {"type": "STRING", "description": "Thời tiết"}
        },
        "required": ["weather"]
    }
)
tools = [types.Tool(function_declarations=[func])]

config = types.GenerateContentConfig(
    tools=tools,
    temperature=0.0
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Tôi muốn ăn trưa món gì đó cay cay với ngân sách 100k, thời tiết bình thường",
    config=config
)

print("Response text:", response.text)
if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
    for part in response.candidates[0].content.parts:
        if part.function_call:
            print("Function Call name:", part.function_call.name)
            print("Function Call args:", part.function_call.args)
