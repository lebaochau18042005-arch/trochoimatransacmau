# Sao lưu dữ liệu WebApp Ma trận sắc màu (miễn phí)

## Trạng thái
WebApp vẫn dùng PostgreSQL Render hiện tại. Không xóa dịch vụ, không đổi DATABASE_URL khi chưa kiểm chứng bản sao lưu và phục hồi.

## Sao lưu lần đầu trên Windows
1. Cài PostgreSQL client tools phiên bản 18 (pg_dump, pg_restore) trên máy cá nhân.
2. Trên Render > PostgreSQL > Info, lấy **External Database URL** (dùng từ máy cá nhân; Internal URL chỉ dùng giữa các dịch vụ Render). Không gửi URL/mật khẩu qua chat, không lưu vào GitHub.
3. Mở PowerShell trong thư mục dự án và thiết lập tạm biến môi trường:
   `$env:DATABASE_URL = Read-Host "Paste External Database URL"`
4. Chạy `python scripts/backup_postgres.py`.
5. Tệp được lưu trong thư mục `private_backups/`. Kiểm tra dung lượng và giữ ít nhất 2 bản sao ở vị trí riêng tư. Xóa biến trong phiên làm việc bằng `Remove-Item Env:DATABASE_URL`.

Lưu ý: Dòng Read-Host không che nội dung khi dán; thực hiện riêng tư, không chụp màn hình. Có thể dùng `Read-Host -AsSecureString` kết hợp chuyển đổi an toàn trong phiên cục bộ nếu cần.

## Kiểm chứng khôi phục
`pg_restore --list private_backups/TEN_FILE.dump` chỉ xác minh tệp đọc được; chưa chứng minh khôi phục thành công. Cần tạo **cơ sở dữ liệu thử nghiệm riêng** rồi khôi phục bằng `pg_restore --no-owner --no-acl --dbname URL_THU_NGHIEM TEN_FILE.dump`. Không chạy restore vào database đang phục vụ học sinh.

## Lưu trữ lâu dài
Render PostgreSQL Free hết hạn sau 30 ngày. Trước khi hết hạn cần chọn nhà cung cấp có gói miễn phí hiện còn áp dụng, đủ hạn mức và có thể xuất/khôi phục PostgreSQL. Chưa được coi là đã chuyển đổi cho đến khi xác nhận kết nối, bản sao lưu, restore và dữ liệu thực tế. Không cam kết miễn phí vĩnh viễn.

## Bảo mật
- Không đưa URL, mật khẩu, dump hoặc dữ liệu học sinh lên repository công khai.
- Sao lưu sau mỗi buổi sử dụng quan trọng và trước mọi thay đổi database.
- Dữ liệu học sinh thật cần có quy trình phân quyền, lưu giữ và xóa dữ liệu.
