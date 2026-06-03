# Thin SPEC Cuối Day 05 — AI Food Concierge

Thin SPEC không phải PRD đầy đủ. Đây là bản cam kết đủ rõ để sáng Day 06 nhóm build ngay.

## 1. Track, product/app và user

**Track:** C - Food & Local Delivery  
**Product/app thật:** ShopeeFood / GrabFood / BeFood làm app tham chiếu  
**User cụ thể:** Nhân viên văn phòng hoặc học viên bận, cần chọn món ăn trưa nhanh trong thời gian nghỉ ngắn.  
**Nhóm có phải user thật không? Nếu không, khác ở đâu?** Có. Nhóm cũng là người dùng phổ thông từng đặt đồ ăn qua app. Tuy nhiên nhóm chưa đại diện đầy đủ cho tất cả user như người ăn kiêng nghiêm ngặt, người có dị ứng thực phẩm, người đặt cho nhóm đông người hoặc người dùng ở khu vực ít quán.

---

## 2. Evidence summary

| Evidence | Nguồn | User/pain nói lên điều gì? | SPEC phải đổi gì? |
|---|---|---|---|
| Khi tự dùng app đồ ăn, nhóm phải lướt nhiều món/quán và tự so sánh giá, thời gian giao, rating, khẩu vị. | Self-use ShopeeFood/GrabFood/BeFood | Pain nằm ở bước ra quyết định, không phải thiếu dữ liệu món. | Cắt scope xuống “gợi ý 3 món phù hợp”, không build cả app giao đồ ăn. |
| Người dùng mô tả nhu cầu bằng câu tự nhiên: “dưới 70k, không cay, giao nhanh, healthy”. | Phỏng vấn nhanh nội bộ / bạn bè, cần kiểm thêm 5 người trước M1 Day 06 | Filter hiện tại rời rạc, không phản ánh cách user nghĩ. | AI cần parse câu tự nhiên thành intent có cấu trúc. |
| Nếu không có món phù hợp, user cần biết nên nới điều kiện nào thay vì nhận danh sách rỗng. | Self-use + test giả lập điều kiện hẹp | Failure path quan trọng là không có kết quả hoặc AI bịa món. | Prototype phải không bịa món, chỉ gợi ý từ database và đề xuất nới điều kiện. |
| User muốn sửa nhanh kết quả: “không cay”, “rẻ hơn”, “healthy hơn”. | Observation từ workflow đặt món | User không muốn làm lại search/filter từ đầu. | Bổ sung correction path để cập nhật intent và gợi ý lại. |

---

## 3. Pain statement

```text
User là nhân viên văn phòng/học viên đang gặp khó ở bước chọn món ăn trưa trên app giao đồ ăn,
vì có quá nhiều món/quán và các bộ lọc hiện tại rời rạc, bắt user tự cân nhắc giá, thời gian giao, khẩu vị và nhu cầu cá nhân,
dẫn tới mất thời gian, dễ chọn lại món quen hoặc bỏ qua lựa chọn phù hợp.
Bằng chứng chính là self-use app giao đồ ăn và phỏng vấn nhanh cho thấy người dùng thường phải lướt nhiều kết quả trước khi quyết định.
```

---

## 4. Build slice

```text
Cho nhân viên văn phòng/học viên đang cần chọn món ăn trưa nhanh,
prototype sẽ dùng AI để augment bước chọn món bằng cách hiểu câu nhập tự nhiên, chuyển thành intent có cấu trúc và xếp hạng món từ danh sách có sẵn,
tạo ra top 3 món phù hợp kèm lý do,
và xử lý failure mode “yêu cầu mơ hồ hoặc không có món phù hợp” bằng cách hỏi lại hoặc đề xuất nới điều kiện.
```

Tên prototype:

```text
AI Food Concierge
```

Input mẫu:

```text
Tôi muốn ăn trưa dưới 70k, không cay, giao trong 30 phút, hơi healthy.
```

Output mẫu:

```text
1. Cơm gà luộc — 65.000đ — giao 25 phút
   Lý do: dưới ngân sách, không cay, ít dầu mỡ, phù hợp bữa trưa.

2. Salad ức gà — 69.000đ — giao 28 phút
   Lý do: healthy, đúng ngân sách, thời gian giao phù hợp.

3. Phở bò tái — 55.000đ — giao 22 phút
   Lý do: không cay, giá phù hợp, giao nhanh.
```

---

## 5. Auto/Aug decision

Chọn một:

- [x] **Augmentation:** AI gợi ý/draft/phân loại, user quyết cuối.
- [ ] **Conditional automation:** AI tự làm trong case hẹp; case mơ hồ/rủi ro chuyển người.
- [ ] **Automation:** AI tự quyết và tự hành động.

**Lý do chọn:**  
Chọn augmentation vì món ăn là quyết định cá nhân, phụ thuộc khẩu vị, cảm xúc và ngữ cảnh tại thời điểm đặt. AI chỉ nên thu hẹp lựa chọn và giải thích, không tự đặt món hay tự thanh toán. Cách này cũng giảm rủi ro AI gợi ý sai, bịa món hoặc chọn món user không muốn.

**Human role:**  
Reviewer / decider / trainer.

- Reviewer: xem 3 món AI gợi ý.
- Decider: chọn món cuối cùng hoặc bỏ qua.
- Trainer: sửa điều kiện như “không cay”, “rẻ hơn”, “healthy hơn” để AI gợi ý lại.

---

## 6. Four paths

| Path | Prototype phải thể hiện gì? |
|---|---|
| Happy | User nhập nhu cầu rõ: “ăn trưa dưới 70k, không cay, giao trong 30 phút”. AI parse đúng intent, hệ thống lọc món từ database, trả top 3 món phù hợp kèm lý do. |
| Low-confidence | User nhập mơ hồ: “ăn gì ngon ngon cũng được”. AI không đủ dữ kiện, prototype hỏi lại 1–2 câu: “Bạn muốn khoảng giá bao nhiêu?” / “Bạn có tránh món cay không?”. |
| Failure | User nhập điều kiện quá hẹp: “sushi dưới 30k giao trong 10 phút”. Hệ thống không bịa món, thông báo chưa có món khớp và đề xuất nới điều kiện: tăng ngân sách hoặc tăng thời gian giao. |
| Correction | Sau khi nhận gợi ý, user nói “tôi không ăn cay” hoặc “rẻ hơn”. Prototype cập nhật intent, loại món không phù hợp và gợi ý lại top 3. |

---

## 7. Failure mode nguy hiểm nhất

```text
Nếu user nhập yêu cầu có ràng buộc quan trọng như không cay, ăn chay, dị ứng hoặc ngân sách thấp,
AI có thể gợi ý món không phù hợp hoặc tự bịa món/quán không có trong dữ liệu,
hậu quả là user mất niềm tin, chọn nhầm món hoặc prototype bị đánh giá là không đáng tin.
Prototype sẽ xử lý bằng cách:
1. Không cho AI tự tạo món mới ngoài database.
2. Backend lọc cứng theo các điều kiện quan trọng như maxPrice, avoidSpicy, preferVegetarian, maxDeliveryMinutes.
3. AI chỉ xếp hạng và giải thích trên danh sách món đã lọc.
4. Nếu không đủ dữ liệu hoặc không có món phù hợp, hỏi lại hoặc đề xuất nới điều kiện.
Owner kiểm thử path này là thành viên phụ trách Test / failure path.
```

---

## 8. Owner plan cho sáng Day 06

| Thành viên | Việc phụ trách | Bằng chứng cần có trong repo |
|---|---|---|
| Member 1 | Research / evidence | Screenshot self-use app, notes phỏng vấn nhanh 5 người, bảng evidence. |
| Member 2 | SPEC | File evidence pack, synthesis-decision, thin SPEC bản cuối. |
| Member 3 | Prototype | Source code UI nhập nhu cầu, seed data món/quán, API recommend hoặc mock logic. |
| Member 4 | Test / failure path | Test case happy, low-confidence, failure, correction; kết quả pass/fail. |
| Member 5 | Demo script / repo | Script demo 3–5 phút, README repo, hướng dẫn chạy prototype. |

Nếu nhóm ít hơn 5 người:

| Vai trò | Người phụ trách |
|---|---|
| Research + SPEC | 1 người |
| Prototype | 1–2 người |
| Test + Demo + Repo | 1 người |

---

## 9. Prototype scope Day 06

### In scope

- Màn nhập nhu cầu ăn uống.
- Seed 20–30 món, 5–6 quán.
- AI/mock AI parse intent.
- Rule filter cứng theo giá, cay/không cay, ăn chay, thời gian giao.
- AI/mock AI ranking top 3 và sinh lý do.
- Hiển thị top 3 món.
- Correction input đơn giản.
- Failure message khi không có kết quả.

### Out of scope

- Thanh toán thật.
- Map/định vị thật.
- Shipper/tracking thật.
- Tích hợp API app giao đồ ăn thật.
- Refund/hoàn tiền.
- Voucher/khuyến mãi phức tạp.
- Đăng nhập/phân quyền đầy đủ.

---

## 10. Test case Day 06

| Test case | Input | Expected |
|---|---|---|
| TC01 - Happy | “Ăn trưa dưới 70k, không cay, giao trong 30 phút” | Trả 3 món giá <= 70k, không cay, delivery <= 30 phút. |
| TC02 - Healthy | “Tôi muốn món healthy dưới 100k” | Ưu tiên món healthy như salad, cơm gà luộc. |
| TC03 - Vegetarian | “Tôi ăn chay, dưới 60k” | Chỉ trả món vegetarian hoặc hỏi lại nếu không có. |
| TC04 - Low-confidence | “Ăn gì ngon cũng được” | Không gợi ý bừa, hỏi lại ngân sách/khẩu vị. |
| TC05 - Failure | “Sushi dưới 30k giao trong 10 phút” | Không có món phù hợp, đề xuất nới ngân sách/thời gian. |
| TC06 - Correction | Sau gợi ý user nhập “không cay” | Loại món cay và gợi ý lại. |

---

## 11. Data model tối thiểu

```text
Restaurant
- Id
- Name
- DistanceKm
- Rating
- AverageDeliveryMinutes
- IsActive

FoodItem
- Id
- RestaurantId
- Name
- Description
- Price
- Category
- IsSpicy
- IsHealthy
- IsVegetarian
- PreparationMinutes
- IsAvailable

RecommendationLog
- Id
- UserPrompt
- ParsedIntentJson
- RecommendedResultJson
- CreatedAt
```

---

## 12. API / function tối thiểu

```text
POST /api/food/recommend
```

Request:

```json
{
  "userPrompt": "Tôi muốn ăn trưa dưới 70k, không cay, giao trong 30 phút"
}
```

Response:

```json
{
  "intent": {
    "mealTime": "lunch",
    "maxPrice": 70000,
    "avoidSpicy": true,
    "maxDeliveryMinutes": 30
  },
  "items": [
    {
      "id": 1,
      "name": "Cơm gà luộc",
      "restaurantName": "Cơm Nhà A",
      "price": 65000,
      "deliveryMinutes": 25,
      "score": 95,
      "reason": "Phù hợp ngân sách, không cay và giao nhanh."
    }
  ],
  "message": null
}
```
