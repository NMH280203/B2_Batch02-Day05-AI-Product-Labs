# Evidence Pack — Chat gợi ý món → quán (LLM orchestrator)


## 1. Nhóm và track

**Tên nhóm:** *\[B2\]*  
**Track:** Food / Super-app — đặt đồ ăn & khám phá món  
**Product/app đã chọn:** GrabFood *(có thể đổi: ShopeeFood / MoMo F&B — ghi lý do nếu đổi)*  
**Build slice đang nghĩ:** Chat API (`be/`) — LLM orchestrator chọn tool theo ngữ cảnh → gợi ý **2 món trước** → user chọn món → gợi ý **2 quán** có món đó (tool vị trí chỉ khi user muốn "gần").

## 2. Self-use evidence

Nhóm tự dùng app/workflow và ghi lại điểm gãy.

| Observation | Screenshot/link | Path liên quan | Điều học được |
|---|---|---|---|
| Biết muốn "healthy" / "ăn nhẹ" nhưng search một từ → danh sách món/quán lệch budget hoặc không đúng cảm giác bữa ăn. | *\[chèn screenshot search "healthy" / "ăn nhẹ"\]* | Failure | User nghĩ **món/intent trước**, app trả danh sách lẫn quán — cần gợi ý món grounded trước. |
| Đã hình dung món (vd. phở, cơm) nhưng không biết quán nào phù hợp ngữ cảnh (giá, chay, gần). | *\[chèn screenshot sau khi search món\]* | Low-confidence | Pain thứ hai là **quán**, không phải chỉ thiếu món. |
| Mô tả thử flow mới: "trưa 1 người 50k không cay" → cần 2 món rõ ràng rồi mới tới quán. | *\[chèn screenshot/wireframe bot nội bộ nếu có\]* | Happy | Luồng **món → quán** khớp cách user suy nghĩ. |
| User nói "gần công ty" — không liên quan GPS bắt buộc; cần hiểu địa điểm dạng text trong ngữ cảnh. | *\[chèn observation ghi chú buổi self-use — ngày \*/\*/2026\]* | Correction | `resolve_location` chỉ khi intent nearby; có thể nhập địa chỉ tay. |

## 3. User / review / social evidence

| Quote / review / observation | Nguồn | User là ai? | Pain/failure mode |
|---|---|---|---|
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

## 4. Competitor / analog evidence

| App / mô hình tham khảo | Họ xử lý task này thế nào? | Pattern học được | Có áp dụng trong 1 ngày không? |
|---|---|---|---|
| GrabFood | Search keyword + filter; gợi ý theo lịch sử đơn. | Mạnh lịch sử; yếu **intent buổi hiện tại**. | Có — slot ngữ cảnh + orchestrator |
| ShopeeFood | Category, banner theo khung giờ. | Gợi ý một phần theo `meal_time`. | Có — slot `meal_time` |
| OpenAI / chatbot ăn uống chung | Trả lời text tự do, dễ hallucination món/giá. | NLU tốt; cần **tool + catalog**. | Có — `food_search` + `ranking` trên JSON |
| Spotify (analog) | Playlist theo mood/context. | **Context/mood** drive discovery. | Có — `mood`, `priority` trong `UserContext` |

## 5. Evidence -> Insight

```text
Evidence nổi bật nhất:
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
```

## 6. Evidence đổi SPEC như thế nào?

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
```