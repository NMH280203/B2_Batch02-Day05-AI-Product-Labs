<<<<<<< HEAD
# Thin SPEC — AI Gợi Ý Quán Ăn Theo Ngữ Cảnh

Thin SPEC không phải PRD đầy đủ. Đây là bản cam kết đủ rõ để sáng Day 06 nhóm build ngay.

---

## 1. Track, product/app và user

**Track:** Food & Local Discovery  
**Product/app thật:** Foody / ShopeeFood — tính năng gợi ý thông minh theo ngữ cảnh  
**User cụ thể:** Nhân viên văn phòng 23–30 tuổi tại TP.HCM / Hà Nội, đặt đồ ăn hoặc đi ăn trưa/tối sau giờ làm, thường xuyên rơi vào tình trạng "không biết hôm nay ăn gì"  
**Nhóm có phải user thật không? Nếu không, khác ở đâu?** Nhóm có 2/4 thành viên là user thật (đặt đồ ăn 3–5 lần/tuần). Điểm khác: các thành viên còn lại ít bị decision fatigue hơn vì sống gần nhà và nấu ăn nhiều hơn — cần validate thêm với segment nhân viên văn phòng thuần túy.

---
=======
# Thin SPEC Cuối Day 05 — Chat món → quán + LLM orchestrator (`be/`)

Thin SPEC không phải PRD đầy đủ. Đây là bản cam kết đủ rõ để sáng Day 06 nhóm build ngay.

> **Chú thích:** `*...*` = nhóm tự điền thật trước nộp.

## 1. Track, product/app và user

**Track:** Food / Super-app  
**Product/app thật:** GrabFood *(tham chiếu UX/evidence; API đặt hàng thật không nằm trong slice)*  
**User cụ thể:** Người 22–40, dùng app đặt ăn **≥ 2 lần/tuần**; biết cảm giác/nhu cầu bữa (healthy, nhẹ, rẻ, nhóm, gần…) nhưng khó map sang món + quán cụ thể.  
**Nhóm có phải user thật không? Nếu không, khác ở đâu?** *\[Có / Một phần — mô tả: vd. nhóm đặt Grab 3–5 lần/tuần nhưng demo dùng catalog mock HCM\]*
>>>>>>> dd83705de56ed3a847a3b2f1061883bfa0979057

## 2. Evidence summary

| Evidence | Nguồn | User/pain nói lên điều gì? | SPEC phải đổi gì? |
|---|---|---|---|
<<<<<<< HEAD
| User mất 10–15 phút/bữa để chọn chỗ ăn, cuối cùng vẫn không hài lòng | Self-use + Facebook group (312 likes) | Decision fatigue — quá nhiều lựa chọn, thiếu tiêu chí | Build slice phải giải quyết "chọn nhanh có lý do", không phải "mở rộng lựa chọn" |
| App gợi ý theo lịch sử, không có "explore mode" | Self-use ShopeeFood + Review 2 sao App Store | User muốn thử mới nhưng không có cách nói với app | AI phải hỗ trợ "hôm nay muốn thử gì đó khác" như một intent rõ ràng |
| Filter tĩnh không xử lý được constraint phức hợp (kiêng muối + không cay + không chiên) | Self-use + Review 3 sao Google Play | User có nhu cầu đặc thù không biểu đạt được qua dropdown filter | AI phải hiểu constraint qua ngôn ngữ tự nhiên |
| Competitor (ChatGPT, Yelp) xử lý conversational constraint tốt hơn app chuyên dụng | Competitor analysis | Bài toán gợi ý theo ngữ cảnh đã được giải — cần áp dụng vào local food context | Prototype nên dạng conversational, không phải thêm filter |

---
=======
| Search "healthy" lệch budget | *\[Self-use — link screenshot\]* | Keyword thiếu ngữ cảnh | `suggest_dishes` multi-slot |
| "Không biết ăn gì" | *\[Review URL\]* | Paralysis | Orchestrator + clarify |
| Có món trong đầu, chưa chọn quán | *\[Self-use note\]* | Quán là bước 2 | `suggest_restaurants(dish_id)` |
| "Gần X" là một phần câu | *\[Phỏng vấn / self-use\]* | Không bắt buộc GPS | `resolve_location` conditional |
| Chatbot chung hay hallucination | Competitor / analog | Cần catalog + tool | `be/data/*.json` + handlers |
>>>>>>> dd83705de56ed3a847a3b2f1061883bfa0979057

## 3. Pain statement

```text
<<<<<<< HEAD
Nhân viên văn phòng 23–30 tuổi đang gặp khó ở bước ra quyết định chọn chỗ ăn mỗi bữa,
vì app hiện tại chỉ gợi ý theo vị trí + lịch sử — không hiểu ngữ cảnh hôm nay của user
(đang vội hay muốn thư giãn, đang kiêng hay muốn ăn no, đi một mình hay đi nhóm),
dẫn tới user phải scroll danh sách dài, mất 10–15 phút vẫn không chắc chắn, hoặc chọn đại rồi hối tiếc.
Bằng chứng chính là comment 312 likes trên Facebook group "Hội ăn uống Hà Nội",
review 2–3 sao trên App Store / Google Play của Foody và ShopeeFood,
và self-use trực tiếp cho thấy Foody không hiểu câu nhập tự nhiên "nhẹ, không quá 80k, đừng cay".
=======
User người đặt đồ ăn qua app thường xuyên đang gặp khó khi chuyển từ
"ngữ cảnh bữa ăn tôi muốn" (mood, budget, dietary, số người, gần hay không…)
sang "món cụ thể và quán có món đó",

vì app chủ yếu search keyword/filter rời rạc và gợi ý theo lịch sử đơn cũ,
không có orchestrator hiểu intent và không gợi ý theo thứ tự món → quán,

dẫn tới xem mãi không đặt, gợi ý lệch (healthy đắt, chay sai), hoặc chọn quán không có món phù hợp.

Bằng chứng chính là *\[self-use observation + URL review + ngày phỏng vấn \*/\*/2026\]*.
>>>>>>> dd83705de56ed3a847a3b2f1061883bfa0979057
```

---

## 4. Build slice

```text
<<<<<<< HEAD
Cho nhân viên văn phòng đang ở tình trạng "không biết hôm nay ăn gì" lúc trưa hoặc tối sau giờ làm,
prototype sẽ dùng AI để hỏi 2–3 câu ngắn (tâm trạng / hoàn cảnh / constraint chính),
lọc danh sách mock quán, và augment quyết định bằng cách gợi ý 3 quán kèm lý do cụ thể bằng ngôn ngữ tự nhiên,
và xử lý failure mode "user nói không hợp sau gợi ý đầu" bằng cách
AI hỏi lại nguyên nhân rồi gợi ý lại — không reset toàn bộ flow.
=======
Cho người dùng app đặt đồ ăn mô tả ngữ cảnh tìm kiếm bằng ngôn ngữ tự nhiên,

prototype FastAPI (be/) sẽ dùng LLM orchestrator (agents/orchestrator.py) để
  (1) trích xuất ngữ cảnh và chọn tool_plan phù hợp,
  (2) augment gợi ý 2 món (food_agent + tools/handlers/food_search.py),
  (3) sau khi user chọn món — augment gợi ý 2 quán có món đó
      (restaurant_agent; tools/handlers/places.py nếu intent_nearby),

tạo ra (qua POST /api/chat SSE):
  event context (slots + tool_plan),
  event dishes (2 món + lý do),
  event restaurants (2 quán + lý do),

và xử lý thiếu ngữ cảnh / parse sai dietary / quán không có món
bằng clarify_context, user xác nhận context, correction, disclaimer, không auto-order.
>>>>>>> dd83705de56ed3a847a3b2f1061883bfa0979057
```

---

## 5. Auto/Aug decision

Chọn một:

- [x] **Augmentation:** AI gợi ý/draft/phân loại, user quyết cuối.
- [ ] **Conditional automation:** AI tự làm trong case hẹp; case mơ hồ/rủi ro chuyển người.
- [ ] **Automation:** AI tự quyết và tự hành động.

<<<<<<< HEAD
**Lý do chọn:** Sở thích ăn uống là quyết định cá nhân cao — AI sai ở đây gây khó chịu ngay lập tức (user đặt đồ ăn không ngon). Augmentation phù hợp hơn: AI thu hẹp lựa chọn và đưa lý do, nhưng user luôn là người bấm chọn cuối.  
**Human role:** decider — user chọn từ shortlist AI tạo ra, có thể từ chối và yêu cầu gợi ý lại.

---

## 6. Four paths

| Path | Prototype phải thể hiện gì? |
|---|---|
| Happy | User nhập "hôm nay mệt, muốn ăn nhẹ, khoảng 80k, gần Q1" → AI hỏi thêm "đi một mình hay nhóm?" → Gợi ý 3 quán kèm lý do ngắn → User chọn ngay trong 1 phút |
| Low-confidence | User nhập "ăn gì đó ngon" (quá chung chung) → AI nhận ra thiếu tiêu chí và hỏi lại "bạn đang muốn ăn no hay ăn nhẹ? Có kiêng gì không?" thay vì gợi ý đại |
| Failure | AI gợi ý quán đã đóng cửa hoặc không còn phù hợp do mock data sai → Prototype phải hiển thị disclaimer "thông tin có thể chưa cập nhật, bạn nên kiểm tra lại trước khi đến" |
| Correction | User nói "không hợp, mình không thích cơm" sau khi nhận gợi ý → AI hỏi lại "bạn muốn loại gì thay thế: bún/phở/bánh mì/món Tây?" rồi gợi ý lại — không bắt đầu lại từ đầu |

---
=======
**Lý do chọn:** Dietary và chọn quán có rủi ro; user phải xác nhận `UserContext` + chọn `dish_id` + chọn quán. LLM không được tự đặt hàng.  
**Human role:** **decider** + **corrector** (+ **reviewer** đọc disclaimer)

## 6. Four paths

| Path | Prototype phải thể hiện gì? | Ngữ cảnh test (ID) |
|---|---|---|
| Happy | Đủ context → `context` event → `dishes` (2) → gửi `selected_dish_id` → `restaurants` (2). | C1, C2 |
| Low-confidence | "Ăn gì đó ngon" → `clarify` event, chưa `dishes`. | C11 |
| Failure | Chay + 50k nhưng `dishes` có món thịt (test filter) hoặc quán không có `dish_id`. | C10 |
| Correction | Message "không đúng ý" / đổi context → chạy lại `suggest_dishes` hoặc `suggest_restaurants`. | C3 + correction |
>>>>>>> dd83705de56ed3a847a3b2f1061883bfa0979057

## 7. Failure mode nguy hiểm nhất

```text
<<<<<<< HEAD
Nếu user có dietary restriction quan trọng (dị ứng đậu phộng, đái tháo đường)
và chỉ đề cập lướt qua trong hội thoại,
AI có thể gợi ý quán không phù hợp hoặc bỏ qua constraint đó,
hậu quả là user ăn sai chế độ hoặc trong trường hợp nghiêm trọng có phản ứng dị ứng.
Prototype sẽ xử lý bằng:
- Khi phát hiện keyword liên quan sức khoẻ (dị ứng, tiểu đường, tim mạch),
  AI phải hỏi lại xác nhận và flag rõ "Mình sẽ ưu tiên lọc quán có thông tin món rõ ràng,
  nhưng bạn vẫn nên hỏi trực tiếp quán trước khi đặt."
- Luôn hiển thị disclaimer khi gợi ý liên quan dietary restriction.
Owner kiểm thử path này là: [Thành viên phụ trách test / failure path].
=======
Nếu user nêu dietary (chay, dị ứng, không cay…) trong ngữ cảnh
nhưng orchestrator parse sai hoặc food_search bỏ sót filter,

AI có thể gợi ý món không phù hợp,
hậu quả là đặt nhầm hoặc mất tin (rủi ro sức khỏe với dị ứng).

Prototype xử lý bằng:
- event context hiển thị tool_plan + slots trước dishes;
- rule lọc dietary_tags trên be/data/dishes.json;
- clarify nếu dietary mơ hồ;
- disclaimer trong prompt/stream;
- correction → re-run suggest_dishes;
- không auto-order.

Owner kiểm thử path này là *\[tên thành viên\]*.
>>>>>>> dd83705de56ed3a847a3b2f1061883bfa0979057
```

---

## 8. Owner plan cho sáng Day 06

| Thành viên | Việc phụ trách | Bằng chứng cần có trong repo |
|---|---|---|
<<<<<<< HEAD
| [Tên TV 1] | Research / evidence — hoàn thiện evidence pack, bổ sung thêm 2 review ngoài nhóm nếu thiếu | `02-group-spec/evidence-pack-template.md` đã có đủ 4 cột |
| [Tên TV 2] | SPEC — review thin SPEC, đảm bảo pain statement + build slice nhất quán với evidence | `02-group-spec/thin-spec-template.md` đã fill đủ 8 mục |
| [Tên TV 3] | Prototype — build chatbot flow (mock data 20 quán, 3 câu hỏi ngữ cảnh, hiển thị 3 gợi ý + lý do) | Link prototype (Figma / coded demo / Voiceflow) trong repo |
| [Tên TV 4] | Test / failure path — test đủ 4 paths, đặc biệt Correction và Failure mode dị ứng | File `test-log.md` ghi lại kết quả từng path |
| [Tên TV 1 hoặc TV 2] | Demo script / repo — viết script demo 5 phút, chuẩn bị README tóm tắt cho Day 06 | `README.md` Day 06 có link demo + mô tả build slice |
=======
| *\[Tên\]* | Research / evidence — screenshot + URL review thật | `02-group-spec/evidence-pack-template.md` |
| *\[Tên\]* | SPEC + `prompt/system_prompt.py` | `thin-spec-template.md`, `be/prompt/` |
| *\[Tên\]* | `orchestrator.py`, `tools/executor.py`, `routers/chat.py` | `be/agents/`, `be/routers/chat.py` |
| *\[Tên\]* | `food_agent`, `food_search`, `data/dishes.json` | `be/agents/food_agent.py`, `be/data/` |
| *\[Tên\]* | `restaurant_agent`, `places` handler | `be/agents/restaurant_agent.py`, `be/tools/handlers/places.py` |
| *\[Tên\]* | Test 4 paths + failure C10 | *\[file checklist test / Postman collection\]* |
| *\[Tên\]* | Demo script + README chạy `uvicorn` | `02-group-spec/demo-script.md`, repo README |

## 9. Map triển khai `be/` (tham chiếu Day 06)

| Thành phần | Đường dẫn |
|---|---|
| Entry | `be/main.py` |
| Chat SSE | `be/routers/chat.py` → `POST /api/chat` |
| Catalog | `be/routers/food.py`, `be/routers/restaurants.py` |
| Orchestrator | `be/agents/orchestrator.py` |
| Món trước | `be/agents/food_agent.py` |
| Quán sau | `be/agents/restaurant_agent.py` |
| Tools | `be/tools/definitions.py`, `executor.py`, `handlers/*` |
| LLM | `be/services/llm.py` |
| Data | `be/data/dishes.json`, `restaurants.json` |
| Env | `be/.env` — *\[ANTHROPIC_API_KEY, GOOGLE_PLACES_API_KEY, …\]* |
>>>>>>> dd83705de56ed3a847a3b2f1061883bfa0979057
