Bạn là senior Backend Engineer. Hãy implement toàn bộ Backend cho dự án AI Chatbot gợi ý món ăn & nhà hàng theo đúng spec dưới đây. Không hỏi lại, implement trực tiếp.

---

## Tech stack
- Python 3.11+, FastAPI, Uvicorn
- Anthropic SDK (claude-sonnet-4-20250514)
- httpx (gọi external API)
- python-dotenv, pydantic v2
- Không có Auth, không có Database, không có Redis
- Mỗi request hoàn toàn stateless — context và messages nhận từ FE

---

## Cấu trúc thư mục (tạo đúng theo cấu trúc này)

be/
├── main.py
├── routers/
│   ├── chat.py
│   └── restaurants.py
├── agents/
│   ├── orchestrator.py
│   ├── food_agent.py
│   └── restaurant_agent.py
├── tools/
│   ├── definitions.py
│   ├── executor.py
│   └── handlers/
│       ├── weather.py
│       ├── food_search.py
│       ├── places.py
│       └── ranking.py
├── services/
│   ├── llm.py
│   ├── places.py
│   └── weather.py
├── prompt/
│   ├── system_prompt.py
│   └── builder.py
├── models/
│   └── schemas.py
├── .env
└── requirements.txt

---

## Pydantic schemas (models/schemas.py)

class Location(BaseModel):
    lat: float
    lng: float
    address: str | None = None

class UserContext(BaseModel):
    location: Location | None = None
    budget: int | None = None           # VND
    people: int | None = None
    meal_time: Literal["breakfast","lunch","dinner","snack"] | None = None
    purpose: Literal["family","date","friends","work","solo"] | None = None
    preferences: list[str] = []
    allergies: list[str] = []

class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    messages: list[Message]
    context: UserContext

class FoodSuggestion(BaseModel):
    name: str
    category: str
    description: str
    estimated_price: int
    reason: str
    tags: list[str]

class Restaurant(BaseModel):
    place_id: str
    name: str
    address: str
    distance_km: float
    rating: float
    price_level: int
    is_open: bool
    phone: str | None = None
    maps_url: str
    photo_url: str | None = None
    featured_dishes: list[str]
    score: float

class RestaurantQueryParams(BaseModel):
    lat: float
    lng: float
    query: str
    budget: int | None = None
    radius: int = 2000
    limit: int = 5

---

## Tool definitions (tools/definitions.py)

Định nghĩa 3 bộ tools sau dưới dạng list[dict] theo Anthropic tool_use format:

### orchestrator_tools
1. detect_intent
   - intent: enum["food_only","restaurant_only","food_and_restaurant","food_info","clarify"]
   - confidence: number 0.0–1.0
   - missing_context: list[str] — các field còn thiếu

2. run_food_agent
   - context: object (UserContext)

3. run_restaurant_agent
   - context: object (UserContext)
   - food_names: list[str] (kết quả từ food agent, có thể rỗng)

### food_tools
1. get_weather
   - lat: number, lng: number

2. search_food_by_criteria
   - meal_time: string
   - budget: number
   - preferences: list[str]
   - allergies: list[str]
   - weather: enum["hot","cold","rainy","normal"]
   - purpose: string

3. ask_user_for_context
   - field: string
   - message: string

### restaurant_tools
1. search_nearby_restaurants
   - lat: number, lng: number, query: string, radius: number, budget: number

2. get_restaurant_detail
   - place_id: string

3. rank_restaurants
   - restaurants: list (raw từ Places API)
   - food_names: list[str]
   - top_n: number (mặc định 5)

4. ask_user_for_context
   - field: string, message: string

---

## Tool executor (tools/executor.py)

Implement hàm:
  async def execute(tool_name: str, tool_input: dict) -> dict

Map tool_name → handler tương ứng:
- get_weather               → handlers/weather.py
- search_food_by_criteria   → handlers/food_search.py
- search_nearby_restaurants → handlers/places.py
- get_restaurant_detail     → handlers/places.py
- rank_restaurants          → handlers/ranking.py
- ask_user_for_context      → trả về {"ask": True, "field": ..., "message": ...}
- run_food_agent / run_restaurant_agent → các agent tương ứng (gọi từ orchestrator)

---

## Handlers

### handlers/weather.py
Gọi services/weather.py, trả về:
{ "condition": "hot"|"cold"|"rainy"|"normal", "temp_c": float, "description": str }

### handlers/food_search.py
Không gọi API ngoài. Dùng LLM (services/llm.py) với prompt nhỏ để sinh danh sách món:
Input: tiêu chí từ tool_input
Output: { "foods": [ FoodSuggestion dict ] }
Yêu cầu LLM trả về JSON thuần, parse và validate bằng Pydantic.

### handlers/places.py
search: Gọi services/places.py với keyword + location, trả về list raw restaurant dict
detail: Gọi services/places.py lấy chi tiết 1 place_id

### handlers/ranking.py
Tính score = food_match*0.3 + rating*0.25 + distance*0.2 + price*0.15 + reviews*0.1
Sort DESC, trả về top_n quán dưới dạng list[Restaurant dict]
Normalize mỗi yếu tố về 0–1 trước khi tính.

---

## Services

### services/llm.py
Implement 2 hàm:

async def call(system: str, messages: list, tools: list, stream: bool = False) -> Any
  Gọi Anthropic client.messages.create hoặc stream tương ứng
  Model: claude-sonnet-4-20250514
  Max tokens: 4096

async def call_json(system: str, prompt: str) -> dict
  Gọi LLM với yêu cầu trả JSON, parse và trả dict
  Dùng cho food_search handler

### services/places.py
Dùng httpx.AsyncClient gọi:
  GET https://maps.googleapis.com/maps/api/place/nearbysearch/json
    params: location, radius, keyword, key
  GET https://maps.googleapis.com/maps/api/place/details/json
    params: place_id, fields, key

Map response sang Restaurant schema.

### services/weather.py
Gọi OpenWeatherMap:
  GET https://api.openweathermap.org/data/2.5/weather?lat=&lon=&appid=&units=metric
Map về { condition, temp_c, description }
Logic map: temp > 32 → hot, temp < 20 → cold, weather id 5xx → rainy, còn lại → normal

---

## Agents

### agents/food_agent.py
async def run(context: UserContext) -> dict:
  1. Gọi llm.call với food_tools
  2. Vòng lặp tool_use:
     - Với mỗi tool_use block → executor.execute(name, input)
     - Nếu tool trả {"ask": True} → trả về {"ask": True, "field": ..., "message": ...} ngay
     - Append tool_result vào messages, gọi llm lại
  3. Khi stop_reason == "end_turn" → parse foods từ text response
  4. Trả về { "foods": list[FoodSuggestion], "food_names": list[str] }

### agents/restaurant_agent.py
async def run(context: UserContext, food_names: list[str]) -> dict:
  Tương tự food_agent nhưng dùng restaurant_tools
  Trả về { "restaurants": list[Restaurant] }

### agents/orchestrator.py
async def run(messages: list, context: UserContext, stream_callback) -> None:
  1. Gọi llm.call với orchestrator_tools
  2. Vòng lặp tool_use:
     - detect_intent → await stream_callback("thinking", {"status": "..."})
     - run_food_agent → chạy food_agent.run, stream_callback("food_results", {...})
     - run_restaurant_agent → chạy restaurant_agent.run, stream_callback("restaurant_results", {...})
     - Nếu bất kỳ agent trả {"ask": True} → stream_callback("ask_context", {...}) rồi return
  3. Rebuild messages với tool_results, gọi llm.call(stream=True) lần cuối
  4. Stream từng text chunk qua stream_callback("text", {"delta": chunk})
  5. stream_callback("done", {"follow_up_suggestions": [...]})

stream_callback signature: async def callback(event: str, data: dict) -> None

---

## System prompt (prompt/system_prompt.py + prompt/builder.py)

### system_prompt.py
BASE_PROMPT = """
Bạn là trợ lý AI chuyên gợi ý món ăn và nhà hàng tại Việt Nam.
Nhiệm vụ: hiểu nhu cầu ăn uống của người dùng và đưa ra gợi ý phù hợp nhất.

Nguyên tắc:
- Luôn trả lời bằng tiếng Việt, thân thiện và tự nhiên
- Ưu tiên gợi ý món ăn phù hợp thời tiết, thời điểm, ngân sách
- Nếu thiếu thông tin quan trọng (vị trí, ngân sách), hỏi tự nhiên thay vì bỏ qua
- Không bịa đặt thông tin quán ăn — chỉ dùng kết quả từ tool
- Giải thích ngắn gọn lý do gợi ý
- Cuối mỗi response đưa ra 2–3 follow-up suggestions ngắn
"""

### builder.py
def build_system_prompt(context: UserContext) -> str:
  Inject thông tin context vào BASE_PROMPT:
  - Vị trí hiện tại (nếu có)
  - Thời gian trong ngày (suy ra từ giờ hệ thống nếu meal_time None)
  - Ngân sách, số người, mục đích (nếu có)
  - Sở thích và dị ứng (nếu có)

---

## Routers

### routers/chat.py
POST /api/chat
- Nhận ChatRequest
- Tạo StreamingResponse với media_type="text/event-stream"
- Gọi orchestrator.run(messages, context, stream_callback)
- stream_callback format mỗi event:
    f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
- Xử lý exception → stream event: error

### routers/restaurants.py
GET /api/restaurants
- Nhận RestaurantQueryParams qua Query params
- Gọi places.search + ranking.rank
- Trả về { restaurants, total, query_used }

---

## main.py
- Khởi tạo FastAPI app
- CORS: allow origins từ ALLOWED_ORIGINS env (split by comma), allow_credentials=False
- Mount routers với prefix /api
- GET /api/health → { status: "ok", version: "1.0.0" }
- Chạy: uvicorn main:app --reload --port 8000

---

## .env
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_PLACES_API_KEY=AIza...
OPENWEATHER_API_KEY=...
ALLOWED_ORIGINS=http://localhost:3000

---

## requirements.txt
fastapi
uvicorn[standard]
anthropic
httpx
python-dotenv
pydantic

---

## Yêu cầu chung
- Toàn bộ I/O là async
- Mỗi service/handler xử lý lỗi riêng, không để exception chưa catch làm crash toàn request
- Khi GOOGLE_PLACES_API_KEY chưa có, handlers/places.py trả mock data 3 quán giả để dev có thể test
- Khi OPENWEATHER_API_KEY chưa có, handlers/weather.py trả về condition="normal" mặc định
- Log lỗi ra stderr với prefix [ERROR]