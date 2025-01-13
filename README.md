# final_term_computervision
# Hệ thống điểm danh sinh viên tự động bằng nhận diện khuôn mặt

## Giới thiệu

Đây là một hệ thống điểm danh sinh viên tự động sử dụng công nghệ nhận diện khuôn mặt, được phát triển bằng Python và Flask framework. Hệ thống cho phép giáo viên tạo lớp học, tải lên video điểm danh và xem báo cáo điểm danh. Sinh viên có thể tham gia lớp học và tải lên ảnh cá nhân để phục vụ cho việc nhận diện.

## Yêu cầu

### Phần cứng

*   Máy tính với CPU Intel Core i3 trở lên (khuyến nghị i5 trở lên).
*   RAM tối thiểu 4GB (khuyến nghị 8GB trở lên).
*   Card đồ họa rời (tùy chọn, nhưng sẽ giúp tăng tốc độ xử lý).
*   Webcam (để test các chức năng).

### Phần mềm

*   Hệ điều hành: Windows 10/11, macOS, Linux.
*   Python 3.9 trở lên.
*   Các thư viện Python:
    *   Flask
    *   Flask-Session
    *   mysql-connector-python
    *   face-recognition
    *   opencv-python (cv2)
    *   numpy
    *   pandas
    *   Werkzeug
    *   dlib
    *   uuid
    *   openpyxl
*   XAMPP (hoặc WAMP, MAMP tùy hệ điều hành).
*   phpMyAdmin.

## Cài đặt

1.  **Cài đặt Python:** Tải và cài đặt Python phiên bản 3.9 trở lên từ trang chủ [https://www.python.org/downloads/](https://www.python.org/downloads/).
2.  **Cài đặt XAMPP:** Tải và cài đặt XAMPP từ trang chủ [https://www.apachefriends.org/index.html](https://www.apachefriends.org/index.html).
3.  **Tạo cơ sở dữ liệu:**
    *   Khởi động XAMPP Control Panel và start Apache và MySQL.
    *   Truy cập phpMyAdmin (thường là `http://localhost/phpmyadmin`).
    *   Tạo database mới với tên `attendance_system`.
    *   Import file `database/init.sql` để tạo các bảng cần thiết.
4.  **Clone repository:**
    ```bash
    git clone <repository_url>
    cd <repository_folder>
    ```

    Thay thế `<repository_url>` và `<repository_folder>` bằng URL của repository và tên thư mục chứa project.
5.  **Cài đặt các thư viện Python:**
    ```bash
    cd backend
    pip install -r ../requirements.txt
    ```

## Cấu trúc thư mục

![Screenshot 2025-01-13 011627](https://github.com/user-attachments/assets/2fc9c9ab-87f2-484c-bbf8-9cb92498515c)


## Chạy ứng dụng

1.  Mở terminal và di chuyển đến thư mục `backend`:
    ```bash
    cd backend
    ```

2.  Chạy file `app.py`:
    ```bash
    python app.py
    ```

3.  Mở trình duyệt web và truy cập địa chỉ: `http://127.0.0.1:5000`

## Chức năng

### Giáo viên

*   **Đăng ký/Đăng nhập:** Giáo viên có thể tạo tài khoản mới hoặc đăng nhập bằng tài khoản đã có.
*   **Tạo lớp học:** Tạo lớp học mới với các thông tin: `Class ID` (duy nhất), `Class Name`, `Class Password`.
*   **Upload danh sách sinh viên:** Tải lên file Excel chứa danh sách sinh viên (cột `student_id` và `name`) cho từng lớp.
*   **Upload video điểm danh:** Tải lên video quay cảnh lớp học (định dạng `.mp4`) để thực hiện điểm danh tự động. Video sẽ được lưu trong thư mục `uploads/<class_id>`.
*   **Tiến hành điểm danh:** Chọn `Class ID` và nhấn nút "Tiến hành điểm danh". Hệ thống sẽ tự động lấy video mới nhất trong thư mục của lớp học tương ứng, nhận diện khuôn mặt sinh viên có trong video, so sánh với ảnh đã lưu và hiển thị danh sách sinh viên có mặt/vắng mặt.
*   **Xem danh sách sinh viên:** Xem danh sách sinh viên của từng lớp học, có chức năng xóa sinh viên khỏi lớp.
*   **Xem báo cáo điểm danh:** Xem bảng điểm danh của từng lớp học theo từng ngày, hiển thị trạng thái `present` hoặc `absent` cho từng sinh viên.
*   **Tải báo cáo điểm danh:** Tải về báo cáo điểm danh dưới dạng file Excel. Có thể tải báo cáo của từng lớp hoặc toàn bộ dữ liệu điểm danh.

### Sinh viên

*   **Đăng ký/Đăng nhập:** Sinh viên có thể tạo tài khoản mới hoặc đăng nhập bằng tài khoản đã có.
*   **Tham gia lớp học:** Tham gia lớp học bằng cách nhập `Class ID` và `Class Password` do giáo viên cung cấp.
*   **Upload ảnh cá nhân:** Tải lên ảnh khuôn mặt cá nhân (nhiều ảnh được hỗ trợ) để hệ thống sử dụng cho việc nhận diện. Ảnh được lưu trong thư mục `uploads/faces/<student_id>`.
*   **Xem danh sách sinh viên:** Xem danh sách sinh viên cùng lớp.

## Công nghệ sử dụng

*   **Python:** Ngôn ngữ lập trình chính.
*   **Flask:** Micro-framework phát triển web.
*   **Flask-Session:** Quản lý session phía server.
*   **MySQL:** Hệ quản trị cơ sở dữ liệu.
*   **phpMyAdmin:** Công cụ quản lý MySQL.
*   **XAMPP:** Môi trường phát triển web.
*   **face_recognition:** Thư viện nhận diện khuôn mặt, sử dụng dlib.
*   **dlib:** Thư viện C++ cho machine learning và computer vision.
*   **OpenCV (cv2):** Thư viện xử lý ảnh và video.
*   **numpy:** Thư viện hỗ trợ tính toán khoa học.
*   **pandas:** Thư viện xử lý dữ liệu dạng bảng, đọc/ghi file Excel.
*   **Werkzeug:** Thư viện cung cấp các công cụ hữu ích cho WSGI.
*   **uuid:** Thư viện tạo UUID (Universally Unique Identifier).
*   **Bootstrap:** Framework CSS cho giao diện người dùng.
*   **HTML, CSS, JavaScript:** Ngôn ngữ thiết kế web.

## Hướng phát triển

*   Cải thiện độ chính xác của thuật toán nhận diện khuôn mặt.
*   Tối ưu hóa hiệu năng xử lý video.
*   Thêm chức năng điểm danh trực tuyến (real-time).
*   Thêm chức năng thông báo kết quả điểm danh cho sinh viên.
*   Phát triển ứng dụng di động.
*   Thêm chức năng quản lý người dùng, phân quyền.

## Thông tin liên hệ
*   **Nhóm**: Nguyễn Hữu Giáp + Nguyễn Cảnh Hưng + Nguyễn Chí Nhân + Hoàng Thiện Quang
*   **Email**: 22110120@st.vju.ac.vn
