# Vietnamese Citizen ID OCR

## 1. Giới thiệu
Dự án sử dụng YOLOv10 để trích xuất thông tin từ căn cước công dân Việt Nam.  
**Lưu ý:** Do dữ liệu sử dụng mang tính nhạy cảm, bạn cần tự thu thập dữ liệu và tiến hành huấn luyện mô hình.

---

## 2. Hướng dẫn cài đặt

### Yêu cầu hệ thống
- **Python**: Phiên bản 3.8.0  
- **Hệ điều hành**: Windows, Linux, hoặc macOS  
- **Thư viện cần thiết**: Liệt kê trong file `requirements.txt`.

---

### Các bước cài đặt

1. **Clone dự án từ GitHub**  
   Chạy lệnh sau trong terminal:
   ```bash
   git clone https://github.com/binh2203/VietnameseCitizenID-OCR.git
   cd VietnameseCitizenID-OCR
2. **Cài đặt các thư viện cần thiết**
   Sử dụng lệnh sau để cài các thư viện từ file requirements.txt:
   ```bash
    pip install -r requirements.txt
3. **Tải mô hình VietOCR**

   Tải mô hình từ link sau:
   ```bash
   https://vocr.vn/data/vietocr/vgg_transformer.pth
Đưa file tải về vào thư mục: models/vietocr/


## 3. Hướng dẫn sử dụng
   Sau khi hoàn tất cài đặt, chạy chương trình bằng lệnh:
   ```bash
    python main.py
