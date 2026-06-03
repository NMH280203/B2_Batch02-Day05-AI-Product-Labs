# Toolkit — Từ Evidence Đến Build Slice
## Chủ đề: AI Gợi Ý Món Ăn & Quán Ăn Theo Nhu Cầu

Dùng sau khi nhóm đã có evidence. Mục tiêu là chốt một build slice đủ nhỏ cho Day 06.

---

## 1. Gom evidence thành cụm

Gom theo **workflow/pain**, không gom theo tên feature.

### Các cụm evidence của nhóm:

- **"Không biết mình muốn ăn gì hôm nay"** — decision fatigue khi có quá nhiều lựa chọn, thiếu tiêu chí thu hẹp
- **"App chỉ gợi ý theo lịch sử, mình muốn thử gì đó mới"** — explore mode bị thiếu, gợi ý lặp lại gây nhàm
- **"Cần lọc theo constraint sức khoẻ / không gian / ngữ cảnh nhưng app không hiểu"** — filter tĩnh không đủ, user cần nói bằng ngôn ngữ tự nhiên
- **"Chọn chỗ ăn cho cả nhóm mất quá nhiều thời gian"** — group decision-making không có công cụ hỗ trợ tổng hợp

---

## 2. Viết insight

Form:

```text
User [segment] không chỉ cần [surface need].
Họ thật ra cần [deeper need],
vì [evidence pattern].
```

**Insight của nhóm:**

```text
Người đi ăn trưa một mình hoặc đặt đồ ăn sau giờ làm không chỉ cần "danh sách quán gần đây".
Họ thật ra cần AI giúp họ ra quyết định nhanh dựa trên ngữ cảnh hôm nay,
vì review và self-use cho thấy vấn đề không phải thiếu lựa chọn — mà là thiếu tiêu chí để chọn.
User bị "decision fatigue" khi phải scroll qua 50+ quán mà không biết cái nào phù hợp với mình lúc này.
```

---

## 3. Viết opportunity

Form:

```text
Cơ hội là dùng AI để [augment/automate hành động hẹp],
giúp user [kết quả],
trong khi vẫn kiểm soát [failure/risk].
```

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

Build slice tốt phải qua 5 câu hỏi:

| Câu hỏi | Đánh giá của nhóm | Đạt? |
|---|---|---|
| User cụ thể chưa? | Nhân viên văn phòng 23–30 tuổi, đặt đồ ăn lúc trưa hoặc tối sau giờ làm, đang trong tình trạng "không biết ăn gì" | ✅ |
| Task đủ hẹp chưa? | Nhập tâm trạng/ngữ cảnh → AI hỏi thêm 1–2 câu → Nhận 3 gợi ý kèm lý do. Demo được trong 3 phút | ✅ |
| AI decision rõ chưa? | AI lọc quán theo constraint và tâm trạng, tạo ra danh sách có thứ tự ưu tiên và kèm lý do | ✅ |
| Failure path rõ chưa? | Case AI gợi ý quán đã đóng cửa, hoặc user nói "không hợp" thì AI làm gì tiếp theo | ✅ |
| Có evidence không? | 5 nguồn evidence (self-use x4, review App Store x2, phỏng vấn x2, competitor analysis x4) | ✅ |

---

## 5. Quyết định: giữ, giảm scope, hay đổi hướng?

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

Những thứ **không build trong Day 06**:

- Tích hợp API quán ăn thật (Foody API / Google Places)
- Tính năng group ordering (tổng hợp sở thích nhiều người)
- Đặt món và thanh toán trong app
- Lưu lịch sử gợi ý và học preference theo thời gian
- Lọc theo chứng nhận sức khoẻ / chế độ ăn đặc biệt (Halal, Vegan, Keto)
- Giao diện mobile native
