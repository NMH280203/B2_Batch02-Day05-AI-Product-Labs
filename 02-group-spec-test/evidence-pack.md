# Evidence Pack — AI Food Concierge

Nộp kèm thin SPEC cuối Day 05.

## 1. Nhóm và track

**Tên nhóm:** Nhóm B2  
**Track:** C - Food & Local Delivery  
**Product/app đã chọn:** ShopeeFood / GrabFood / BeFood làm app tham chiếu  
**Build slice đang nghĩ:** AI gợi ý 3 món ăn phù hợp từ câu nhập tự nhiên của người dùng, dựa trên ngân sách, khẩu vị, thời gian giao và ràng buộc cá nhân.

Build slice chốt:

```text
Cho nhân viên văn phòng đang cần chọn món ăn trưa nhanh,
prototype dùng AI để hiểu nhu cầu ăn uống từ câu nhập tự nhiên,
lọc và xếp hạng món từ danh sách có sẵn,
tạo ra 3 gợi ý món phù hợp kèm lý do,
và xử lý trường hợp mơ hồ hoặc không có món phù hợp bằng cách hỏi lại / đề xuất nới điều kiện.
```

---

## 2. Self-use evidence

Nhóm tự dùng app/workflow và ghi lại điểm gãy.

| Observation | Screenshot/link | Path liên quan | Điều học được |
|---|---|---|---|
| Khi mở app đặt đồ ăn vào giờ trưa, người dùng thấy quá nhiều quán/món. Việc chọn món phải tự so sánh nhiều yếu tố như giá, khoảng cách, phí giao, thời gian giao, món cay/không cay, healthy/không healthy. | Screenshot cần bổ sung: màn danh sách món/quán trên ShopeeFood/GrabFood | Happy | Vấn đề không phải thiếu món, mà là quá nhiều lựa chọn và thiếu hỗ trợ ra quyết định theo ngữ cảnh cá nhân. |
| Bộ lọc hiện tại thường là filter rời rạc như món, quán, giá, khuyến mãi, thời gian giao. App chưa hiểu tốt câu tự nhiên kiểu “ăn trưa dưới 70k, không cay, giao nhanh”. | Screenshot cần bổ sung: màn filter/search | Low-confidence | AI có thể tạo giá trị bằng cách parse nhu cầu tự nhiên thành điều kiện lọc có cấu trúc. |
| Khi yêu cầu quá hẹp như “sushi dưới 30k giao trong 10 phút”, app thường chỉ trả danh sách rỗng hoặc kết quả không rõ vì sao không khớp. | Screenshot cần bổ sung: màn không có kết quả / ít kết quả | Failure | Prototype cần có path không tìm thấy món phù hợp và đề xuất nới điều kiện, thay vì trả kết quả rỗng. |
| Khi app gợi ý món không đúng khẩu vị, người dùng phải tự quay lại lọc/tìm lại từ đầu. | Screenshot cần bổ sung: thao tác back/search lại | Correction | Prototype cần có correction path: user nói “tôi không ăn cay” hoặc “rẻ hơn”, hệ thống cập nhật điều kiện và gợi ý lại. |

---

## 3. User / review / social evidence

Nguồn có thể là review App Store/Play, group, comment, phỏng vấn nhanh, hoặc nguồn public khác.

| Quote / review / observation | Nguồn | User là ai? | Pain/failure mode |
|---|---|---|---|
| “Mình mất khá lâu để chọn món trưa vì phải xem giá, món nào gần, món nào giao nhanh và không bị cay.” | Phỏng vấn nhanh nội bộ nhóm / bạn học, cần ghi tên hoặc mã người tham gia trước M1 Day 06 | Nhân viên văn phòng / học viên dùng app đặt đồ ăn | User cần ra quyết định nhanh, không muốn tự lọc nhiều lần. |
| “Có hôm không biết ăn gì, mở app lên lướt một lúc rồi lại đặt món quen.” | Phỏng vấn nhanh nội bộ nhóm / bạn bè | Người dùng đặt đồ ăn thường xuyên | Choice overload; app có nhiều món nhưng không giúp quyết định theo ngữ cảnh. |
| “Nếu app hỏi vài câu rồi gợi ý 3 món hợp túi tiền và khẩu vị thì dễ chọn hơn.” | Phỏng vấn nhanh nội bộ nhóm / bạn bè | Người dùng bận, cần đặt nhanh | Cần AI augmentation: gợi ý có kiểm soát, user vẫn quyết cuối. |

Nếu chưa có nguồn ngoài nhóm, ghi rõ:

```text
Một phần evidence hiện tại là giả định dựa trên self-use và phỏng vấn nhanh nội bộ.
Nhóm sẽ kiểm bằng cách hỏi nhanh ít nhất 5 người từng dùng ShopeeFood/GrabFood trước checkpoint M1 Day 06.

Câu hỏi kiểm chứng:
1. Bạn thường mất bao lâu để chọn món khi đặt đồ ăn?
2. Lý do khiến bạn khó chọn món là gì?
3. Bạn có muốn nhập một câu như “dưới 70k, không cay, giao nhanh” để app gợi ý món không?
4. Nếu app gợi ý 3 món có lý do rõ ràng, bạn có sẵn sàng chọn một trong số đó không?
```

---

## 4. Competitor / analog evidence

| App / mô hình tham khảo | Họ xử lý task này thế nào? | Pattern học được | Có áp dụng trong 1 ngày không? |
|---|---|---|---|
| ShopeeFood / GrabFood / BeFood | Cho tìm kiếm, danh mục, quán gần, khuyến mãi, rating, danh sách món. Người dùng vẫn phải tự ghép nhiều tiêu chí để quyết định. | Có nhiều dữ liệu món/quán nhưng thiếu lớp “decision support” theo câu tự nhiên. | Có. Prototype chỉ cần seed 20–30 món và lọc/xếp hạng theo intent. |
| ChatGPT / AI chatbot | Hiểu câu tự nhiên tốt, có thể hỏi lại khi thiếu thông tin, nhưng nếu không giới hạn dữ liệu thì dễ bịa món/quán. | AI nên dùng để parse intent và giải thích/xếp hạng, không tự tạo món ngoài database. | Có. Backend gửi danh sách món đã lọc cho AI, AI chỉ ranking. |
| Netflix / Spotify recommendation | Gợi ý ít lựa chọn phù hợp, có lý do/nhóm ngữ cảnh, giảm thời gian quyết định. | Không cần show tất cả kết quả; top 3–5 gợi ý tốt hơn danh sách dài. | Có. Prototype show top 3 món kèm lý do. |

---

## 5. Evidence -> Insight

```text
Evidence nổi bật nhất:
Người dùng đặt đồ ăn không thiếu lựa chọn. Điểm gãy nằm ở bước quyết định ăn gì khi có quá nhiều món/quán và nhiều điều kiện nhỏ phải tự cân nhắc: giá, thời gian giao, cay/không cay, healthy, món quen hay món mới.

Insight:
User không chỉ gặp vấn đề “tìm món ăn”.
Thật ra họ cần hỗ trợ ra quyết định nhanh theo ngữ cảnh cá nhân,
vì self-use và phỏng vấn nhanh cho thấy người dùng thường phải tự lọc nhiều lần và vẫn quay lại món quen.

Opportunity:
AI có thể giúp bằng cách augment hành động hẹp: hiểu câu nhập tự nhiên, chuyển thành điều kiện lọc, xếp hạng 3 món phù hợp từ danh sách có sẵn, giải thích lý do và hỏi lại khi thiếu thông tin.
```

---

## 6. Evidence đổi SPEC như thế nào?

- [ ] Đổi user chính.
- [x] Đổi pain statement.
- [x] Đổi build slice.
- [x] Đổi Auto/Aug decision.
- [x] Đổi 4 paths.
- [x] Đổi failure mode.
- [ ] Đổi owner/test plan.

Ghi rõ 1-2 thay đổi quan trọng:

```text
Trước evidence, nhóm định làm “AI assistant cho Food Delivery” khá rộng, có thể bao gồm tìm quán, xử lý đơn lỗi, hoàn tiền, tối ưu giao nhận.

Sau evidence, nhóm đổi thành một build slice hẹp:
“AI gợi ý 3 món ăn trưa phù hợp từ câu nhập tự nhiên”.

Lý do:
Day 06 chỉ cần chứng minh một lát cắt nhỏ có AI decision rõ. Self-use cho thấy pain rõ nhất là bước chọn món nhanh, không phải toàn bộ quy trình đặt đồ ăn. Slice này demo được trong 3–5 phút, có happy path, low-confidence, failure và correction path rõ ràng.
```

---

## Appendix — Test evidence cần thu trước Day 06

| Test | Cách làm | Kỳ vọng |
|---|---|---|
| Test 5 người | Cho 5 người nhập nhu cầu ăn trưa thật | Ít nhất 3/5 người thấy top 3 gợi ý có món chọn được |
| Test time-to-decision | So sánh chọn món thủ công và chọn qua AI | AI giúp giảm thời gian chọn món |
| Test failure | Nhập điều kiện quá hẹp | Prototype không bịa món, đề xuất nới điều kiện |
| Test correction | User sửa “không cay”, “rẻ hơn”, “healthy hơn” | Prototype cập nhật filter và gợi ý lại |
