# Thin SPEC — AI Gợi Ý Quán Ăn Theo Ngữ Cảnh

Thin SPEC không phải PRD đầy đủ. Đây là bản cam kết đủ rõ để sáng Day 06 nhóm build ngay.

---

## 1. Track, product/app và user

**Track:** Food & Local Discovery  
**Product/app thật:** Foody / ShopeeFood — tính năng gợi ý thông minh theo ngữ cảnh  
**User cụ thể:** Nhân viên văn phòng 23–30 tuổi tại TP.HCM / Hà Nội, đặt đồ ăn hoặc đi ăn trưa/tối sau giờ làm, thường xuyên rơi vào tình trạng "không biết hôm nay ăn gì"  
**Nhóm có phải user thật không? Nếu không, khác ở đâu?** Nhóm có 2/4 thành viên là user thật (đặt đồ ăn 3–5 lần/tuần). Điểm khác: các thành viên còn lại ít bị decision fatigue hơn vì sống gần nhà và nấu ăn nhiều hơn — cần validate thêm với segment nhân viên văn phòng thuần túy.

---

## 2. Evidence summary

| Evidence | Nguồn | User/pain nói lên điều gì? | SPEC phải đổi gì? |
|---|---|---|---|
| User mất 10–15 phút/bữa để chọn chỗ ăn, cuối cùng vẫn không hài lòng | Self-use + Facebook group (312 likes) | Decision fatigue — quá nhiều lựa chọn, thiếu tiêu chí | Build slice phải giải quyết "chọn nhanh có lý do", không phải "mở rộng lựa chọn" |
| App gợi ý theo lịch sử, không có "explore mode" | Self-use ShopeeFood + Review 2 sao App Store | User muốn thử mới nhưng không có cách nói với app | AI phải hỗ trợ "hôm nay muốn thử gì đó khác" như một intent rõ ràng |
| Filter tĩnh không xử lý được constraint phức hợp (kiêng muối + không cay + không chiên) | Self-use + Review 3 sao Google Play | User có nhu cầu đặc thù không biểu đạt được qua dropdown filter | AI phải hiểu constraint qua ngôn ngữ tự nhiên |
| Competitor (ChatGPT, Yelp) xử lý conversational constraint tốt hơn app chuyên dụng | Competitor analysis | Bài toán gợi ý theo ngữ cảnh đã được giải — cần áp dụng vào local food context | Prototype nên dạng conversational, không phải thêm filter |

---

## 3. Pain statement

```text
Nhân viên văn phòng 23–30 tuổi đang gặp khó ở bước ra quyết định chọn chỗ ăn mỗi bữa,
vì app hiện tại chỉ gợi ý theo vị trí + lịch sử — không hiểu ngữ cảnh hôm nay của user
(đang vội hay muốn thư giãn, đang kiêng hay muốn ăn no, đi một mình hay đi nhóm),
dẫn tới user phải scroll danh sách dài, mất 10–15 phút vẫn không chắc chắn, hoặc chọn đại rồi hối tiếc.
Bằng chứng chính là comment 312 likes trên Facebook group "Hội ăn uống Hà Nội",
review 2–3 sao trên App Store / Google Play của Foody và ShopeeFood,
và self-use trực tiếp cho thấy Foody không hiểu câu nhập tự nhiên "nhẹ, không quá 80k, đừng cay".
```

---

## 4. Build slice

```text
Cho nhân viên văn phòng đang ở tình trạng "không biết hôm nay ăn gì" lúc trưa hoặc tối sau giờ làm,
prototype sẽ dùng AI để hỏi 2–3 câu ngắn (tâm trạng / hoàn cảnh / constraint chính),
lọc danh sách mock quán, và augment quyết định bằng cách gợi ý 3 quán kèm lý do cụ thể bằng ngôn ngữ tự nhiên,
và xử lý failure mode "user nói không hợp sau gợi ý đầu" bằng cách
AI hỏi lại nguyên nhân rồi gợi ý lại — không reset toàn bộ flow.
```

---

## 5. Auto/Aug decision

Chọn một:

- [x] **Augmentation:** AI gợi ý/draft/phân loại, user quyết cuối.
- [ ] **Conditional automation:** AI tự làm trong case hẹp; case mơ hồ/rủi ro chuyển người.
- [ ] **Automation:** AI tự quyết và tự hành động.

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

## 7. Failure mode nguy hiểm nhất

```text
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
```

---

## 8. Owner plan cho sáng Day 06

| Thành viên | Việc phụ trách | Bằng chứng cần có trong repo |
|---|---|---|
| [Tên TV 1] | Research / evidence — hoàn thiện evidence pack, bổ sung thêm 2 review ngoài nhóm nếu thiếu | `02-group-spec/evidence-pack-template.md` đã có đủ 4 cột |
| [Tên TV 2] | SPEC — review thin SPEC, đảm bảo pain statement + build slice nhất quán với evidence | `02-group-spec/thin-spec-template.md` đã fill đủ 8 mục |
| [Tên TV 3] | Prototype — build chatbot flow (mock data 20 quán, 3 câu hỏi ngữ cảnh, hiển thị 3 gợi ý + lý do) | Link prototype (Figma / coded demo / Voiceflow) trong repo |
| [Tên TV 4] | Test / failure path — test đủ 4 paths, đặc biệt Correction và Failure mode dị ứng | File `test-log.md` ghi lại kết quả từng path |
| [Tên TV 1 hoặc TV 2] | Demo script / repo — viết script demo 5 phút, chuẩn bị README tóm tắt cho Day 06 | `README.md` Day 06 có link demo + mô tả build slice |
