# MA TRẬN SẮC MÀU - BẢN TRỰC TUYẾN

## Mục tiêu
Website chạy trên trình duyệt máy tính, Android và iPhone. Học sinh không cài đặt gì. Giáo viên tạo lớp, câu hỏi, ma trận màu và chia sẻ mã trò chơi. Điểm được lưu ở máy chủ.

## Chạy thử trên máy tính
1. Cài Python 3.11+.
2. Mở terminal tại thư mục gốc của dự án.
3. `pip install -r backend/requirements.txt`
4. Thiết lập `SECRET_KEY` bằng một chuỗi ngẫu nhiên dài, ví dụ `python -c "import secrets; print(secrets.token_urlsafe(48))"` rồi đặt vào biến môi trường.
5. `uvicorn backend.main:app --host 0.0.0.0 --port 8000`
6. Mở `http://localhost:8000`.

## Chạy thử trên điện thoại cùng Wi-Fi
Mở `http://DIA_CHI_IP_MAY_TINH:8000` (máy tính và điện thoại cùng mạng). Cần cho phép kết nối qua tường lửa hệ điều hành. Đây chỉ là thử nghiệm nội bộ, không dùng với dữ liệu thật.

## Đưa lên Internet
Có Dockerfile để triển khai trên dịch vụ hỗ trợ Docker và HTTPS (ví dụ Render). Tạo dịch vụ web từ Git repository; chọn Docker. Thiết lập:
- `APP_ENV=production`
- `SECRET_KEY=<chuỗi ngẫu nhiên dài và riêng tư>`
- `DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:PORT/DBNAME` (PostgreSQL được cấp từ nhà cung cấp dịch vụ)
- `CORS_ORIGINS=https://TEN-MIEN-CUA-BAN`

Phải cung cấp PostgreSQL lưu trữ bền vững trước khi chạy nhiều phiên bản hoặc triển khai chính thức. Không lưu SQLite vào ổ đĩa tạm của hosting. Để truy cập, học sinh chỉ cần đường link `https://TEN-MIEN/?play=MA6KYTU`.

## Hướng dẫn sử dụng
- Giáo viên: chọn Giáo viên > Đăng ký > Quản lý lớp > Tạo lớp và thêm học sinh > Kho trò chơi > Tạo mới > nhập câu hỏi và vẽ tranh > Phát hành.
- Chia sẻ: trong Kho trò chơi, nhấn Sao chép link rồi gửi cho học sinh. Học sinh cũng có thể nhập mã trò chơi.
- Học sinh: nhập tên và mã học sinh nếu lớp có danh sách > trả lời tất cả câu > Nộp bài > xem điểm và tranh bí mật.
- Giáo viên: Kho trò chơi > Xem kết quả > Xuất CSV.

## Hạn chế và an toàn
- Giao diện online không yêu cầu Node/npm; thư mục frontend/ là bản React thử nghiệm cũ, không dùng trong chế độ online này.
- Hiện chưa có mã PIN/đăng nhập riêng cho học sinh, giới hạn số lượt nộp hoặc chống gian lận. Không coi tên/mã HS là xác thực danh tính.
- Chưa có rate limiting đăng nhập, CSRF không áp dụng cho Bearer token nhưng cần tăng cường chống dò mật khẩu, nhật ký và sao lưu trước khi dùng thực tế.
- Chưa kiểm thử trên thiết bị Android/iPhone vật lý và chưa triển khai Internet trong phiên làm việc này.
- Chỉ dùng dữ liệu giả lập cho tới khi hoàn thiện kiểm thử và quy trình bảo vệ dữ liệu học sinh.
