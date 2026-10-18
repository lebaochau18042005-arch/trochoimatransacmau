# MA TRẬN SẮC MÀU – Mã nguồn khởi tạo

Hệ thống gồm React/Vite (frontend) và FastAPI/SQLAlchemy (backend), hỗ trợ SQLite để thử nghiệm và PostgreSQL khi triển khai.

## Chạy máy chủ

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
# Đặt SECRET_KEY ngẫu nhiên trước khi triển khai công khai
uvicorn main:app --reload --port 8000
```

## Chạy giao diện

```bash
cd frontend
npm install
npm run dev
```

Mở http://localhost:5173. API tại http://localhost:8000/docs.

## Cấu hình triển khai

Backend: `DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DB`, `SECRET_KEY` (giá trị bí mật dài và ngẫu nhiên), `CORS_ORIGINS=https://ten-mien-frontend`.

Frontend: `VITE_API_URL=https://ten-mien-backend` rồi chạy `npm run build`.

Không lưu dữ liệu thật trước khi bổ sung giới hạn tần suất đăng nhập/nộp bài, chống bot, HTTPS, cơ chế đặt lại mật khẩu, sao lưu và chính sách bảo vệ dữ liệu học sinh. Bản khởi tạo này cho phép tham gia bằng tên không cần tài khoản, mã học sinh là tùy chọn và không phải cơ chế xác minh danh tính mạnh. Chưa có import Word/PDF, tự chuyển ảnh thành ma trận hoặc phân quyền quản trị trường.

## Kết quả kiểm thử và giới hạn (bản cập nhật)

Chạy `python -m unittest discover -s tests -v` từ thư mục gốc. Kiểm thử tích hợp API đã xác nhận: đăng ký giáo viên, tạo lớp, thêm học sinh, tạo trò chơi, nộp bài, lưu và đọc kết quả, từ chối truy cập không xác thực. Các trường hợp câu trả lời ngoài phạm vi và thiếu mã học sinh khi đã có danh sách được từ chối.

Chưa biên dịch frontend do `npm install` hết thời gian; chưa kiểm thử giao diện trên trình duyệt/thiết bị thật. Chưa triển khai lên Internet. Không sử dụng dữ liệu học sinh thật trước khi hoàn thiện kiểm thử bảo mật, xác thực danh tính, giới hạn tần suất và sao lưu.

## Cập nhật V2 (19/10/2026)

- Bảng tổng hợp: số học sinh, lượt làm bài, tỉ lệ đúng trung bình, số lượt điểm tối đa.
- Giáo viên có thể đóng/mở trò chơi; trò chơi đóng không cho học sinh xem hoặc nộp bài.
- Liên kết `/?play=MA1234` đưa học sinh tới màn hình nhập mã trò chơi.
- Tối ưu vùng bấm cảm ứng, focus bàn phím và bố cục điện thoại nhỏ.
- Xuất CSV có giảm rủi ro công thức bị thực thi khi mở trong bảng tính.

Đã chạy bài kiểm thử API tự động (xem `tests/test_flow.py`). Chưa build được React do không tải được npm dependencies trong môi trường này; chưa xác minh trên thiết bị thật. Không tuyên bố tương thích mọi thiết bị trước khi kiểm thử trình duyệt và máy chủ thực tế.

## V3 - Báo cáo theo học sinh

- API `GET /api/games/{id}/student-summary` (yêu cầu token giáo viên sở hữu trò chơi).
- Bảng thống kê số lượt, điểm cao nhất, điểm gần nhất và điểm trung bình theo học sinh.
- Kiểm thử bằng `python -m unittest discover -s tests -v`.
- Chưa xác nhận chạy trên mọi trình duyệt và thiết bị thật.


## V4 - Kiểm tra tích hợp và hiển thị thiết bị nhỏ
- API tham gia không trả dữ liệu tranh bí mật trước khi nộp; tranh chỉ trả trong kết quả chấm.
- Cải thiện CSS cho màn hình hẹp, bảng kết quả cuộn ngang và nút cảm ứng.
- Đã thử `npm install` trong môi trường này nhưng hết thời gian, do đó chưa thể xác nhận build React hoặc tương thích trình duyệt thật.
- Trước khi triển khai cần thử trên Chrome Android, Safari iOS, Edge/Chrome desktop và chạy `npm run build`.


## V5 - cấu hình và kiểm thử (19/10/2026)

- Sửa cấu hình API frontend: mặc định gọi `/api` cùng nguồn gốc, Vite proxy sang `http://127.0.0.1:8000`. Tránh lỗi khi học sinh truy cập frontend qua điện thoại nhưng `localhost` lại trỏ vào điện thoại của học sinh.
- Bổ sung `frontend/vite.config.js` và `.env.example`; khi triển khai frontend khác domain, dùng `VITE_API_URL` và cấu hình CORS backend.
- Xử lý lỗi phản hồi JSON không hợp lệ và kiểm tra mã trò chơi rỗng.
- Kiểm thử backend: `python -m unittest discover -s tests -v`.

### Chạy thử bằng điện thoại trong cùng Wi-Fi

1. Chạy backend: `cd backend && uvicorn main:app --host 0.0.0.0 --port 8000`.
2. Chạy frontend: `cd frontend && npm install && npm run dev`.
3. Trên điện thoại truy cập `http://IP_MAY_TINH:5173` (không dùng localhost). Cho phép cổng 5173 trên tường lửa nếu cần.
4. Không mở ứng dụng ra Internet hoặc nhập dữ liệu học sinh thật trước khi hoàn thiện bảo mật, HTTPS và sao lưu.

### Tình trạng xác minh

API test tự động đạt. `npm install` đã thử nhưng quá thời gian trong môi trường này, nên chưa build React hoặc kiểm thử trên trình duyệt/thiết bị thật.
