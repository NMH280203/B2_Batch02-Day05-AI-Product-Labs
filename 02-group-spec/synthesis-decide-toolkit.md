# Toolkit — Từ Evidence Đến Build Slice
## Chat món → quán · LLM orchestrator · FastAPI `be/`

> **Chú thích:** `*...*` = nhóm tự điền / bổ sung trước nộp.

Dùng sau khi nhóm đã có evidence. Mục tiêu: chốt build slice đủ nhỏ cho Day 06.

---

## 1. Gom evidence thành cụm

| Cụm pain (workflow) | Evidence | Tool / agent |
|---|---|---|
| Không map intent → món cụ thể | Self-use search lệch; C2 healthy | `suggest_dishes` · `food_agent` |
| Đã có món, chưa chọn quán | Self-use; review | `suggest_restaurants` · `restaurant_agent` |
| Ngữ cảnh mơ hồ | Review "không biết ăn gì"; C11 | `clarify_context` · orchestrator |
| Muốn ăn gần | User nói "gần X"; C3,C4,C12 | `resolve_location` · `handlers/places.py` |
| Dietary / chay sai | Review; C10 failure | filter `dietary_tags` + confirm context |
| Ăn nhóm / budget tổng | Self-use Zalo; C6 | `party_size` + món share/set |

---

## 2. Viết insight

```text
User người đặt đồ ăn thường xuyên không chỉ cần "danh sách quán" hay "search keyword".

Họ thật ra cần hệ thống hiểu ngữ cảnh tìm kiếm buổi đó,
gợi ý MÓN trước (đúng cảm giác, budget, dietary),
rồi QUÁN có món đó (lọc gần chỉ khi họ nói "gần"),

vì evidence self-use + review + phỏng vấn *\[ngày \*/\*/2026\]* cho thấy
họ mô tả bữa bằng ngôn ngữ tự nhiên, không phải lúc nào cũng bắt đầu từ GPS.
```

---

## 3. Viết opportunity

```text
Cơ hội là dùng LLM orchestrator (be/agents/orchestrator.py) chọn tool theo intent,
gợi ý 2 món rồi 2 quán grounded trên catalog,

giúp user quyết định trong 3–5 phút chat (SSE),

trong khi kiểm soát parse sai, dietary risk, và hallucination
bằng tool + JSON catalog + user confirm + correction.
```

---

## 4. Ma trận ngữ cảnh C1–C12 → `tool_plan`

| ID | Ví dụ user | Slots chính | `tool_plan` (thứ tự) |
|----|------------|-------------|------------------------|
| C1 | Trưa 1 người 50k không cay no nhanh | meal, party=1, budget, dietary | `suggest_dishes` → *(chọn món)* → `suggest_restaurants` |
| C2 | Healthy ~60k | priority=healthy, budget |`suggest_dishes` → *(chọn món)* → `suggest_restaurants`  |
| C3 | Gần Bitexco trưa 70k | intent_nearby, area_note, budget | `resolve_location` → `suggest_dishes` → … |
| C4 | Ăn gần đây (chưa rõ địa chỉ) | intent_nearby | `clarify_context` → `resolve_location` → … |
| C5 | Tối 2 người đổi gió 150k | party=2, mood=doi_gio | `suggest_dishes` → … |
| C6 | Nhóm 4 ~200k | party=4, budget | dishes tag share/set → restaurants |
| C7 | Rẻ 40k | priority=re, budget thấp | `suggest_dishes` → … |
| C8 | Mệt ăn nhẹ tối | mood=met | dishes light → restaurants |
| C9 | Muốn đồ Nhật | cuisine=nhat | `suggest_dishes` → … |
| C10 | Chay 50k | dietary=chay | **failure test** dietary |
| C11 | Ăn gì ngon | thiếu slot | `clarify_context` only |
| C12 | Gần + healthy + 2 người 120k | nearby + healthy + party=2 | `resolve_location` + filters → dishes → restaurants |

**Luồng cố định:** Món luôn trước quán. Location tool **không** gọi nếu không có `intent_nearby`.

---

## 5. Chọn build slice — 5 câu hỏi

| Câu hỏi | Đạt? | Ghi chú |
|---|---|---|
| User cụ thể? | Có | 22–40, đặt app ≥2 lần/tuần |
| Task hẹp? | Có | 1 chat SSE: context → 2 món → 2 quán |
| AI decision rõ? | Có | Orchestrator + suggest_dishes + suggest_restaurants |
| Failure path? | Có | C10 dietary; C11 clarify |
| Evidence? | *\[Cần link/screenshot thật\]* | Bổ sung trước M1 |

---

## 6. Quyết định scope

| Tình huống | Quyết định nhóm |
|---|---|
| GPS-centric slice cũ | **Đổi** → context-first, món → quán |
| 12 ngữ cảnh | Demo 4–5 (C1, C2, C3, C11, C10) |
| Places API lỗi | Fallback `be/data/restaurants.json` + filter district |
| LLM không có key | Rule orchestrator trong `orchestrator.py` |
| Quá rộng | Backlog: order, payment, weather bắt buộc |

---

## 7. Câu chốt cuối

```text
Dựa trên evidence *\[GrabFood self-use + review URL + phỏng vấn \*/\*/2026\]*,

nhóm sẽ build be/ FastAPI (POST /api/chat SSE, orchestrator + food/restaurant agents),

cho người đặt đồ ăn mô tả ngữ cảnh tìm kiếm tự nhiên,

để giảm paralysis và gợi ý lệch keyword,

bằng LLM augment chọn tool + gợi ý 2 món trước 2 quán,

và test failure path dietary sai (C10).
```

---

## 8. Backlog (không build Day 06)

- Thanh toán / đặt hàng Grab thật
- Auto-order khi đủ context
- Auth, rate limit production
- Weather bắt buộc mọi request *(optional: `handlers/weather.py`)*
- Multi-session memory dài
- FE đẹp full *(MVP: curl/Postman hoặc `fe/` tối thiểu)*

---

## 9. Tool catalog → file `be/`

| Tool | Handler | Agent |
|------|---------|-------|
| `clarify_context` | orchestrator + LLM | orchestrator |
| `resolve_location` | `handlers/places.py` | orchestrator |
| `get_weather_context` | `handlers/weather.py` (optional) | orchestrator |
| `suggest_dishes` | `food_search.py` + `ranking.py` | food_agent |
| `suggest_restaurants` | `places.py` + `ranking.py` | restaurant_agent |

Định nghĩa schema: `be/tools/definitions.py` · Thực thi: `be/tools/executor.py`
