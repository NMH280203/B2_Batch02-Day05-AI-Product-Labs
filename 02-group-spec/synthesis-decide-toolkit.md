# Toolkit — Từ Evidence Đến Build Slice
<<<<<<< HEAD
## Chủ đề: AI Gợi Ý Món Ăn & Quán Ăn Theo Nhu Cầu
=======
## Chat món → quán · LLM orchestrator · FastAPI `be/`
>>>>>>> dd83705de56ed3a847a3b2f1061883bfa0979057

> **Chú thích:** `*...*` = nhóm tự điền / bổ sung trước nộp.

Dùng sau khi nhóm đã có evidence. Mục tiêu: chốt build slice đủ nhỏ cho Day 06.

---

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

<<<<<<< HEAD
### Các cụm evidence của nhóm:

- **"Không biết mình muốn ăn gì hôm nay"** — decision fatigue khi có quá nhiều lựa chọn, thiếu tiêu chí thu hẹp
- **"App chỉ gợi ý theo lịch sử, mình muốn thử gì đó mới"** — explore mode bị thiếu, gợi ý lặp lại gây nhàm
- **"Cần lọc theo constraint sức khoẻ / không gian / ngữ cảnh nhưng app không hiểu"** — filter tĩnh không đủ, user cần nói bằng ngôn ngữ tự nhiên
- **"Chọn chỗ ăn cho cả nhóm mất quá nhiều thời gian"** — group decision-making không có công cụ hỗ trợ tổng hợp

=======
>>>>>>> dd83705de56ed3a847a3b2f1061883bfa0979057
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

<<<<<<< HEAD
**Insight của nhóm:**

```text
Người đi ăn trưa một mình hoặc đặt đồ ăn sau giờ làm không chỉ cần "danh sách quán gần đây".
Họ thật ra cần AI giúp họ ra quyết định nhanh dựa trên ngữ cảnh hôm nay,
vì review và self-use cho thấy vấn đề không phải thiếu lựa chọn — mà là thiếu tiêu chí để chọn.
User bị "decision fatigue" khi phải scroll qua 50+ quán mà không biết cái nào phù hợp với mình lúc này.
```
=======
---
>>>>>>> dd83705de56ed3a847a3b2f1061883bfa0979057

---

## 3. Viết opportunity

```text
Cơ hội là dùng LLM orchestrator (be/agents/orchestrator.py) chọn tool theo intent,
gợi ý 2 món rồi 2 quán grounded trên catalog,

giúp user quyết định trong 3–5 phút chat (SSE),

trong khi kiểm soát parse sai, dietary risk, và hallucination
bằng tool + JSON catalog + user confirm + correction.
```

<<<<<<< HEAD
**Opportunity của nhóm:**

```text
Cơ hội là dùng AI để hỏi 2–3 câu ngắn thu thập ngữ cảnh (tâm trạng, hoàn cảnh, constraint),
rồi lọc và gợi ý 3 quán phù hợp kèm lý do ngắn gọn bằng ngôn ngữ tự nhiên,
giúp user ra quyết định trong dưới 1 phút,
trong khi vẫn để user tự chọn cuối — AI chỉ augment, không quyết thay.
Failure được kiểm soát bằng cách luôn hiển thị lý do gợi ý và cho phép user nói "không hợp, gợi ý khác".
```

---

## 4. Chọn build slice
=======
---
>>>>>>> dd83705de56ed3a847a3b2f1061883bfa0979057

## 4. Ma trận ngữ cảnh C1–C12 → `tool_plan`

<<<<<<< HEAD
| Câu hỏi | Đánh giá của nhóm | Đạt? |
|---|---|---|
| User cụ thể chưa? | Nhân viên văn phòng 23–30 tuổi, đặt đồ ăn lúc trưa hoặc tối sau giờ làm, đang trong tình trạng "không biết ăn gì" | ✅ |
| Task đủ hẹp chưa? | Nhập tâm trạng/ngữ cảnh → AI hỏi thêm 1–2 câu → Nhận 3 gợi ý kèm lý do. Demo được trong 3 phút | ✅ |
| AI decision rõ chưa? | AI lọc quán theo constraint và tâm trạng, tạo ra danh sách có thứ tự ưu tiên và kèm lý do | ✅ |
| Failure path rõ chưa? | Case AI gợi ý quán đã đóng cửa, hoặc user nói "không hợp" thì AI làm gì tiếp theo | ✅ |
| Có evidence không? | 5 nguồn evidence (self-use x4, review App Store x2, phỏng vấn x2, competitor analysis x4) | ✅ |

---
=======
| ID | Ví dụ user | Slots chính | `tool_plan` (thứ tự) |
|----|------------|-------------|------------------------|
| C1 | Trưa 1 người 50k không cay no nhanh | meal, party=1, budget, dietary | `suggest_dishes` → *(chọn món)* → `suggest_restaurants` |
| C2 | Healthy ~60k | priority=healthy, budget |同上 |
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
>>>>>>> dd83705de56ed3a847a3b2f1061883bfa0979057

---

<<<<<<< HEAD
| Tình huống | Quyết định của nhóm |
|---|---|
| Evidence yếu, user mơ hồ | **Không áp dụng** — nhóm có đủ evidence từ nhiều nguồn |
| Ý tưởng quá rộng | **Áp dụng** — cắt xuống một flow duy nhất: "gợi ý cho 1 user, 1 bữa ăn, 1 lần tương tác". Bỏ group-ordering, bỏ đặt hàng tích hợp |
| AI không cần thiết | **Không áp dụng** — bài toán thu thập ngữ cảnh + lọc theo constraint phức hợp cần AI |
| Rủi ro cao | **Áp dụng nhẹ** — chọn Augmentation (user quyết cuối), không automation hoàn toàn vì sở thích ăn uống mang tính cá nhân cao |
| Không demo được trong 1 ngày | **Áp dụng** — bỏ tích hợp API quán thật, dùng mock data 20 quán đủ để demo flow |

---

## 6. Câu chốt cuối

```text
Dựa trên evidence từ self-use app (Foody, ShopeeFood, Google Maps),
review App Store và phỏng vấn nhanh 3 người dùng thực,
cho thấy user mất 10–15 phút/bữa để quyết định chỗ ăn do thiếu tiêu chí,

nhóm sẽ build prototype chatbot gợi ý quán ăn theo ngữ cảnh,
cho nhân viên văn phòng 23–30 tuổi đang ở tình trạng "không biết ăn gì",
để giải quyết decision fatigue khi chọn quán ăn,
bằng cách AI hỏi 2–3 câu về tâm trạng và constraint hôm nay rồi augment quyết định,
và sẽ test failure path: user nói "không hợp" sau gợi ý đầu → AI phải hỏi lại được nguyên nhân và gợi ý lại.
```

---

## 7. Backlog
=======
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
>>>>>>> dd83705de56ed3a847a3b2f1061883bfa0979057

## 8. Backlog (không build Day 06)

<<<<<<< HEAD
- Tích hợp API quán ăn thật (Foody API / Google Places)
- Tính năng group ordering (tổng hợp sở thích nhiều người)
- Đặt món và thanh toán trong app
- Lưu lịch sử gợi ý và học preference theo thời gian
- Lọc theo chứng nhận sức khoẻ / chế độ ăn đặc biệt (Halal, Vegan, Keto)
- Giao diện mobile native
=======
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
>>>>>>> dd83705de56ed3a847a3b2f1061883bfa0979057
