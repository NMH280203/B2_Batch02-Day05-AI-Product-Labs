<<<<<<< HEAD
# Evidence Pack — AI Gợi Ý Món Ăn & Quán Ăn Theo Nhu Cầu
=======
# Evidence Pack — Chat gợi ý món → quán (LLM orchestrator)
>>>>>>> dd83705de56ed3a847a3b2f1061883bfa0979057

Nộp kèm thin SPEC cuối Day 05.

> **Chú thích:** Mục có bọc `*...*` là **nhóm tự điền bằng dữ liệu thật** (screenshot, link, tên, ngày phỏng vấn) trước khi nộp Day 06 / checkpoint M1.

## 1. Nhóm và track

<<<<<<< HEAD
**Tên nhóm:** Nhóm 2A — Batch 02  
**Track:** Food & Local Discovery  
**Product/app đã chọn:** Foody / ShopeeFood (tính năng gợi ý thông minh)  
**Build slice đang nghĩ:** AI hỏi nhanh 2–3 câu (tâm trạng, khẩu vị, khu vực) rồi gợi ý 3 quán phù hợp kèm lý do ngắn, xử lý case "không biết mình muốn ăn gì"

---
=======
**Tên nhóm:** *\[điền tên nhóm thật\]*  
**Track:** Food / Super-app — đặt đồ ăn & khám phá món  
**Product/app đã chọn:** GrabFood *(có thể đổi: ShopeeFood / MoMo F&B — ghi lý do nếu đổi)*  
**Build slice đang nghĩ:** Chat API (`be/`) — LLM orchestrator chọn tool theo ngữ cảnh → gợi ý **2 món trước** → user chọn món → gợi ý **2 quán** có món đó (tool vị trí chỉ khi user muốn "gần").
>>>>>>> dd83705de56ed3a847a3b2f1061883bfa0979057

## 2. Self-use evidence

Nhóm tự dùng app/workflow và ghi lại điểm gãy.

| Observation | Screenshot/link | Path liên quan | Điều học được |
|---|---|---|---|
<<<<<<< HEAD
| Foody hiển thị danh sách quán dài, không lọc theo tâm trạng hay hoàn cảnh (đi một mình, đi hẹn hò, đi nhóm bạn) | Self-use — Foody app lúc 18:30 ngày làm việc | Failure | User phải scroll nhiều, tự đọc rating mà không có lý do cụ thể để chọn |
| ShopeeFood gợi ý theo lịch sử đặt, nhưng khi user muốn thử mới hoàn toàn, không có cách để nói "mình chán đồ cũ rồi" | Self-use — ShopeeFood, tình huống "thứ 6 muốn ăn gì đó khác lạ" | Low-confidence | App không có cơ chế thu thập tâm trạng/ngữ cảnh hiện tại của user |
| Google Maps gợi ý theo vị trí nhưng không phân biệt bữa sáng / trưa / tối và không hiểu "đang vội" vs "muốn ngồi lâu" | Self-use — Google Maps search "quán ăn gần đây" lúc 12h trưa | Low-confidence | Intent thực của user phức tạp hơn chỉ là "gần đây + mở cửa" |
| Khi thử nhập "muốn ăn gì đó nhẹ, không quá 80k, gần đây, đừng cay" vào Foody search — app không hiểu được câu ngôn ngữ tự nhiên | Self-use — Foody search bar | Failure | App chỉ nhận keyword, không xử lý được constraint phức hợp từ natural language |

---
=======
| Biết muốn "healthy" / "ăn nhẹ" nhưng search một từ → danh sách món/quán lệch budget hoặc không đúng cảm giác bữa ăn. | *\[chèn screenshot search "healthy" / "ăn nhẹ"\]* | Failure | User nghĩ **món/intent trước**, app trả danh sách lẫn quán — cần gợi ý món grounded trước. |
| Đã hình dung món (vd. phở, cơm) nhưng không biết quán nào phù hợp ngữ cảnh (giá, chay, gần). | *\[chèn screenshot sau khi search món\]* | Low-confidence | Pain thứ hai là **quán**, không phải chỉ thiếu món. |
| Mô tả thử flow mới: "trưa 1 người 50k không cay" → cần 2 món rõ ràng rồi mới tới quán. | *\[chèn screenshot/wireframe bot nội bộ nếu có\]* | Happy | Luồng **món → quán** khớp cách user suy nghĩ. |
| User nói "gần công ty" — không liên quan GPS bắt buộc; cần hiểu địa điểm dạng text trong ngữ cảnh. | *\[chèn observation ghi chú buổi self-use — ngày \*/\*/2026\]* | Correction | `resolve_location` chỉ khi intent nearby; có thể nhập địa chỉ tay. |
>>>>>>> dd83705de56ed3a847a3b2f1061883bfa0979057

## 3. User / review / social evidence

| Quote / review / observation | Nguồn | User là ai? | Pain/failure mode |
|---|---|---|---|
<<<<<<< HEAD
| "Mỗi ngày mình mất cả 15 phút chỉ để chọn ăn trưa xong rồi vẫn kêu không ngon" | Facebook group "Hội ăn uống Hà Nội", bình luận có 312 like | Nhân viên văn phòng, 23–30 tuổi | Decision fatigue — quá nhiều lựa chọn, không có tiêu chí rõ |
| "App cứ gợi ý mấy quán mình đặt hoài, muốn thử mới mà không biết chỗ nào hợp khẩu vị mình" | Review 2 sao trên App Store — ShopeeFood | User đặt cơm thường xuyên | Gợi ý lặp lại theo lịch sử, thiếu "explore mode" |
| "Đặt cho sếp, phải tìm đồ ăn phù hợp kiêng muối, không cay, không chiên — tìm mãi mà Foody không lọc được" | Review 3 sao trên Google Play — Foody | Nhân viên đặt đồ ăn cho cả nhóm | App thiếu advanced dietary filter, không hỏi về constraint sức khoẻ |
| "Muốn quán có chỗ ngồi làm việc, có wifi, yên tĩnh — app không lọc được mấy cái đó cùng lúc" | Phỏng vấn nhanh bạn học (sinh viên, làm remote), 22 tuổi | Sinh viên/freelancer cần không gian làm việc kết hợp ăn uống | App filter không phản ánh được ngữ cảnh sử dụng quán |
| "Cuối tuần cả nhóm 6 người vote ăn gì mất 30 phút, cuối cùng cũng không ai hài lòng" | Phỏng vấn nhóm 2 bạn học (nhóm đi ăn thường xuyên) | Nhóm bạn đi ăn cuối tuần | Group decision-making — AI không hỗ trợ tổng hợp sở thích nhiều người |

---
=======
| *\[copy quote đầy đủ\]* "Không biết ăn gì, mở app xem mãi không quyết được." | *\[URL Google Play / App Store — GrabFood\]* | NVVP / user đặt thường xuyên | Low-confidence — paralysis |
| *\[copy quote\]* "Tìm healthy toàn món đắt / không đúng ý." | *\[URL review ShopeeFood hoặc GrabFood\]* | User ăn healthy budget vừa | Failure — keyword thiếu ngữ cảnh |
| *\[copy quote\]* "Gợi ý không đúng ăn chay / dị ứng." | *\[URL hoặc link group Facebook/TikTok\]* | User dietary restriction | Failure — dietary |
| *\[copy quote hoặc paraphrase\]* "Quán xa / ship lâu hơn hiển thị." | *\[URL review\]* | User đặt giao hàng | Failure — kỳ vọng quán (khi đã có món) |
| Phỏng vấn nhanh *\[số\]* người: hay mô tả bữa bằng mood + budget trước khi nghĩ quán. | *\[Tên người phỏng vấn / ngày \*/\*/2026 / ghi âm hoặc note\]* | *\[SV / NVVP / …\]* | Insight — context-first |

Nếu chưa có nguồn ngoài nhóm đủ 3 quote, ghi rõ:

```text
*Các quote trên có quote mẫu theo pattern review công khai — nhóm thay bằng link thật trước M1.*
Nhóm sẽ kiểm bằng: tìm 5 review trên CH Play/App Store với từ khóa "không biết ăn gì", "healthy", "chay" trước *\[ngày deadline\]*.
```
>>>>>>> dd83705de56ed3a847a3b2f1061883bfa0979057

## 4. Competitor / analog evidence

| App / mô hình tham khảo | Họ xử lý task này thế nào? | Pattern học được | Có áp dụng trong 1 ngày không? |
|---|---|---|---|
<<<<<<< HEAD
| Google Bard / ChatGPT | User hỏi tự nhiên "gợi ý quán ăn tối nay gần Q1, 2 người, lãng mạn, budget 300k" — AI trả ngay 3 gợi ý có lý do | Conversational constraint gathering — không cần form, hỏi tự nhiên | Có — prototype dạng chat đơn giản |
| Yelp "Nearby Eats" | Kết hợp distance + rating + mood tag (Romantic, Quick Bite, Late Night) | Mood-based tagging giúp user filter nhanh hơn danh sách thuần | Có — có thể làm tag selection thay chatbox |
| Netflix recommendation | Hỏi "Bạn đang muốn xem gì hôm nay?" rồi thu hẹp dần bằng 2–3 lựa chọn | Progressive narrowing — không hỏi hết cùng lúc, từng bước thu nhỏ | Có — áp dụng vào chatbot gợi ý |
| Replika / Woebot | Thu thập tâm trạng trước khi gợi ý | Mood-first approach — biết user đang thế nào mới gợi ý | Có — hỏi "Hôm nay bạn đang cảm thấy thế nào?" làm câu mở đầu |
=======
| GrabFood | Search keyword + filter; gợi ý theo lịch sử đơn. | Mạnh lịch sử; yếu **intent buổi hiện tại**. | Có — slot ngữ cảnh + orchestrator |
| ShopeeFood | Category, banner theo khung giờ. | Gợi ý một phần theo `meal_time`. | Có — slot `meal_time` |
| OpenAI / chatbot ăn uống chung | Trả lời text tự do, dễ hallucination món/giá. | NLU tốt; cần **tool + catalog**. | Có — `food_search` + `ranking` trên JSON |
| Spotify (analog) | Playlist theo mood/context. | **Context/mood** drive discovery. | Có — `mood`, `priority` trong `UserContext` |
>>>>>>> dd83705de56ed3a847a3b2f1061883bfa0979057

---

## 5. Evidence → Insight

```text
Evidence nổi bật nhất:
<<<<<<< HEAD
- User mất trung bình 10–15 phút để chọn chỗ ăn mỗi bữa.
- App hiện tại gợi ý theo lịch sử và vị trí, bỏ qua ngữ cảnh tâm trạng / hoàn cảnh.
- Review và phỏng vấn cho thấy user không thiếu lựa chọn — họ thiếu tiêu chí quyết định.

Insight:
User không chỉ cần "danh sách quán gần đây".
Thật ra họ cần AI giúp thu hẹp lựa chọn dựa trên ngữ cảnh cụ thể hôm nay
(tâm trạng, hoàn cảnh, constraint sức khoẻ/budget/không gian),
vì quá nhiều lựa chọn gây "decision fatigue" — user chọn đại hoặc bỏ cuộc.

Opportunity:
AI có thể giúp bằng cách hỏi 2–3 câu ngắn để thu thập ngữ cảnh hôm nay,
rồi tự động lọc và gợi ý 3 quán phù hợp kèm lý do ngắn gọn,
thay vì để user tự scroll và tự phán đoán từ rating.
=======
- Self-use: user có intent món (healthy, nhẹ, phở…) nhưng app ép search keyword → kết quả lệch.
- Review: "không biết ăn gì", healthy/chay sai, quán/ship không khớp kỳ vọng.
- Phỏng vấn nhanh: mô tả ngữ cảnh bữa (budget, mood, số người) trước khi chọn quán.

Insight:
User không chỉ gặp "không tìm được quán" hay "không tìm được món".
Thật ra họ cần hệ thống hiểu NGỮ CẢNH TÌM KIẾM buổi đó,
rồi gợi ý MÓN trước (quyết định cảm giác/budget/dietary),
sau đó QUÁN có món đó (và lọc gần chỉ khi họ nói "gần").

Opportunity:
LLM orchestrator chọn tool (clarify / location / suggest_dishes / suggest_restaurants)
để augment quyết định — user vẫn xác nhận context và chọn món/quán cuối.
>>>>>>> dd83705de56ed3a847a3b2f1061883bfa0979057
```

---

## 6. Evidence đổi SPEC như thế nào?

<<<<<<< HEAD
- [x] Đổi user chính.
- [x] Đổi pain statement.
- [x] Đổi build slice.
- [x] Đổi Auto/Aug decision.
- [x] Đổi 4 paths.
- [x] Đổi failure mode.
- [x] Đổi owner/test plan.

Ghi rõ 1-2 thay đổi quan trọng:

```text
Trước evidence, nhóm định làm app filter quán ăn theo tag tĩnh (loại đồ ăn, khu vực, giá).

Sau evidence, nhóm đổi thành chatbot hỏi ngữ cảnh tâm trạng/hoàn cảnh trước,
rồi mới lọc và gợi ý có lý do rõ ràng.

Lý do:
Review và self-use cho thấy user không thiếu bộ lọc — Foody đã có đủ filter.
Vấn đề thật là user không biết mình muốn gì và thiếu tiêu chí để chọn.
AI cần đóng vai "người bạn hỏi thêm" thay vì "bộ lọc thụ động".
=======
- [ ] Đổi user chính.
- [x] Đổi pain statement.
- [x] Đổi build slice.
- [ ] Đổi Auto/Aug decision.
- [x] Đổi 4 paths.
- [x] Đổi failure mode.
- [x] Đổi owner/test plan.

```text
Trước evidence, nhóm định: chat gợi ý quán gần (GPS) rồi mới tới món.

Sau evidence, nhóm đổi thành:
- Luồng MÓN → QUÁN, grounded catalog.
- LLM orchestrator + tool theo ngữ cảnh (C1–C12).
- Triển khai FastAPI be/ (orchestrator, food_agent, restaurant_agent).
- Location tool CHỈ khi intent "gần" (text hoặc GPS tùy chọn).

Lý do:
Self-use + review cho thấy user bắt đầu từ "muốn ăn gì / cảm giác thế nào",
không phải lúc nào cũng bắt đầu từ vị trí.
>>>>>>> dd83705de56ed3a847a3b2f1061883bfa0979057
```
