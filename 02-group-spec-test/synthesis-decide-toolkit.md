# Toolkit — Từ Evidence Đến Build Slice

Dùng sau khi nhóm đã có evidence. Mục tiêu là chốt một build slice đủ nhỏ cho Day 06.

## 1. Gom evidence thành cụm

Gom theo **workflow/pain**, không gom theo tên feature.

### Cụm 1 — Quá nhiều lựa chọn, khó quyết định nhanh

- Người dùng mở app đồ ăn vào giờ trưa và thấy rất nhiều quán/món.
- Người dùng phải tự so sánh giá, khoảng cách, thời gian giao, phí giao, rating, khẩu vị.
- Người dùng dễ quay lại món quen vì không muốn mất thời gian chọn.

**Ý nghĩa:** Pain chính không phải “không tìm được món”, mà là “khó ra quyết định nhanh”.

### Cụm 2 — Filter rời rạc, không hiểu nhu cầu tự nhiên

- Người dùng nghĩ theo câu tự nhiên: “dưới 70k, không cay, giao nhanh, hơi healthy”.
- App thường bắt người dùng tự chọn danh mục/filter/search riêng lẻ.
- Một nhu cầu ăn uống thật thường gồm nhiều ràng buộc cùng lúc.

**Ý nghĩa:** AI có thể tạo giá trị bằng cách chuyển câu tự nhiên thành điều kiện lọc có cấu trúc.

### Cụm 3 — Không có món phù hợp thì trải nghiệm dễ cụt

- Với điều kiện quá hẹp, danh sách có thể rỗng.
- Nếu chỉ báo “không có kết quả”, user không biết nên nới điều kiện nào.
- AI nếu tự bịa món/quán sẽ gây mất tin tưởng.

**Ý nghĩa:** Prototype phải có failure path: không bịa món, đề xuất nới ngân sách/thời gian/loại món.

### Cụm 4 — User muốn sửa nhanh thay vì làm lại từ đầu

- Khi gợi ý sai khẩu vị, user không muốn quay lại search/filter từ đầu.
- Câu sửa thường rất ngắn: “không cay”, “rẻ hơn”, “healthy hơn”, “giao nhanh hơn”.

**Ý nghĩa:** Correction path cần cho phép user cập nhật điều kiện và nhận gợi ý mới.

---

## 2. Viết insight

Form:

```text
User [segment] không chỉ cần [surface need].
Họ thật ra cần [deeper need],
vì [evidence pattern].
```

Insight chốt:

```text
Nhân viên văn phòng đặt đồ ăn trưa không chỉ cần danh sách món/quán.
Họ thật ra cần hỗ trợ ra quyết định nhanh theo ngữ cảnh cá nhân,
vì evidence cho thấy họ phải tự cân nhắc nhiều điều kiện nhỏ như giá, thời gian giao, cay/không cay, healthy và thường mất thời gian lướt danh sách dài.
```

Insight phụ:

```text
Người dùng không cần AI tự đặt món thay họ.
Họ cần AI thu hẹp lựa chọn xuống vài phương án đáng tin,
vì quyết định cuối cùng vẫn phụ thuộc khẩu vị và cảm giác của người ăn tại thời điểm đó.
```

---

## 3. Viết opportunity

Form:

```text
Cơ hội là dùng AI để [augment/automate hành động hẹp],
giúp user [kết quả],
trong khi vẫn kiểm soát [failure/risk].
```

Opportunity chốt:

```text
Cơ hội là dùng AI để augment bước chọn món:
AI hiểu câu nhập tự nhiên, chuyển thành intent có cấu trúc, lọc/xếp hạng món từ database có sẵn,
giúp user nhận 3 lựa chọn phù hợp trong vài giây,
trong khi vẫn kiểm soát rủi ro bằng cách không cho AI bịa món, hỏi lại khi mơ hồ và cho user sửa điều kiện.
```

---

## 4. Chọn build slice

Build slice tốt phải qua 5 câu hỏi:

| Câu hỏi | Đạt khi |
|---|---|
| User cụ thể chưa? | Nhân viên văn phòng/học viên bận, cần chọn món trưa nhanh trong giờ nghỉ. |
| Task đủ hẹp chưa? | Chỉ làm “nhập nhu cầu → gợi ý 3 món → user chọn/correct”, demo được trong 3–5 phút. |
| AI decision rõ chưa? | AI parse intent và xếp hạng 3 món phù hợp từ danh sách món có sẵn. |
| Failure path rõ chưa? | Có case yêu cầu mơ hồ và case không có món phù hợp. |
| Có evidence không? | Có self-use app giao đồ ăn, phỏng vấn nhanh, competitor pattern và plan kiểm chứng 5 người. |

Build slice cuối:

```text
Cho nhân viên văn phòng đang cần chọn món ăn trưa nhanh,
prototype dùng AI để hiểu nhu cầu ăn uống từ câu nhập tự nhiên,
lọc và xếp hạng món từ danh sách có sẵn,
tạo ra 3 món gợi ý kèm lý do,
và xử lý yêu cầu mơ hồ/không có kết quả bằng cách hỏi lại hoặc đề xuất nới điều kiện.
```

---

## 5. Quyết định: giữ, giảm scope, hay đổi hướng?

| Tình huống | Quyết định |
|---|---|
| Evidence yếu, user mơ hồ | Kiểm nhanh 5 người trước M1 Day 06. Nếu không ai thấy pain, đổi sang pain “xử lý đơn lỗi/hoàn tiền”. |
| Ý tưởng quá rộng | Giữ domain Food Delivery, cắt xuống một flow: AI gợi ý món ăn trưa. |
| AI không cần thiết | Nếu rule đủ xử lý, vẫn dùng AI cho parse câu tự nhiên và giải thích ranking; rule giữ vai trò lọc cứng. |
| Rủi ro cao | Chọn augmentation, không automation. User quyết món cuối, AI không tự đặt đơn. |
| Không demo được trong 1 ngày | Bỏ thanh toán, shipper, map, refund, voucher; chỉ seed data + recommendation UI. |

Quyết định chốt:

```text
Giữ domain C - Food & Local Delivery.
Giảm scope từ “AI assistant cho đặt đồ ăn” xuống “AI gợi ý 3 món ăn trưa phù hợp”.
Chọn Augmentation: AI gợi ý, user quyết định.
```

---

## 6. Câu chốt cuối

Điền câu này trước khi rời lớp:

```text
Dựa trên self-use app giao đồ ăn, phỏng vấn nhanh người dùng và pattern competitor,
nhóm sẽ build prototype slice “AI Food Concierge — gợi ý món ăn trưa”,
cho nhân viên văn phòng/học viên bận,
để giải quyết pain khó chọn món nhanh vì quá nhiều lựa chọn và filter rời rạc,
bằng cách AI augment bước chọn món: parse nhu cầu tự nhiên, lọc/xếp hạng món có sẵn và giải thích top 3,
và sẽ test failure path khi yêu cầu quá mơ hồ hoặc không có món phù hợp.
```

---

## 7. Backlog

Những thứ **không build trong Day 06**:

- Thanh toán thật.
- Định vị/map thật.
- Shipper/tracking giao hàng thật.
- Tích hợp API ShopeeFood/GrabFood/BeFood thật.
- Refund/complaint flow.
- Voucher/khuyến mãi phức tạp.
- Recommendation theo lịch sử dài hạn.
- Multi-user/group order.
- Quản trị nhà hàng đầy đủ.
- Tối ưu tuyến giao nhận.
- Push notification.
- Đánh giá món sau khi ăn.
