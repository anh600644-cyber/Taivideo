# 📥 Video Downloader CLI

Công cụ dòng lệnh (CLI) tải video đa nền tảng, được viết bằng Python.

## ✨ Tính năng

| Tính năng | Mô tả |
|---|---|
| 🌐 **Đa nền tảng** | Hỗ trợ YouTube, Bilibili, TikTok, Douyin |
| 🎬 **Chọn chất lượng** | best, 1080p, 720p, 480p, 360p |
| 🎵 **Tải âm thanh** | Trích xuất audio thành MP3 320kbps |
| 📦 **Tải hàng loạt** | Tải nhiều video từ file danh sách URL |
| 📊 **Thanh tiến trình** | Hiển thị tốc độ, dung lượng, thời gian còn lại |
| 🔍 **Xem thông tin** | Xem thông tin video mà không cần tải |
| 🍪 **Hỗ trợ cookies** | Dùng cookies cho video yêu cầu đăng nhập |

---

## 📋 Yêu cầu hệ thống

- **Python** 3.8 trở lên
- **FFmpeg** (khuyến nghị - cần thiết để ghép video + audio chất lượng cao)

### Cài đặt FFmpeg

<details>
<summary><b>Windows</b></summary>

```bash
# Cách 1: Dùng winget
winget install FFmpeg

# Cách 2: Dùng choco
choco install ffmpeg

# Cách 3: Tải thủ công từ https://ffmpeg.org/download.html
# và thêm vào biến môi trường PATH
```
</details>

<details>
<summary><b>macOS</b></summary>

```bash
brew install ffmpeg
```
</details>

<details>
<summary><b>Linux (Ubuntu/Debian)</b></summary>

```bash
sudo apt update && sudo apt install ffmpeg
```
</details>

---

## 🚀 Cài đặt

### 1. Clone code về máy

```bash
git clone https://github.com/<your-username>/video-downloader-cli.git
cd video-downloader-cli
```

### 2. Tạo môi trường ảo (khuyến nghị)

```bash
# Tạo virtual environment
python -m venv venv

# Kích hoạt (Windows)
venv\Scripts\activate

# Kích hoạt (macOS / Linux)
source venv/bin/activate
```

### 3. Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### 4. Kiểm tra cài đặt

```bash
python video_downloader.py --version
```

---

## 📖 Hướng dẫn sử dụng

### Tải video cơ bản

```bash
python video_downloader.py <URL_VIDEO>
```

**Ví dụ theo từng nền tảng:**

```bash
# YouTube
python video_downloader.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Bilibili
python video_downloader.py "https://www.bilibili.com/video/BV1xx411c7mD"

# TikTok
python video_downloader.py "https://www.tiktok.com/@user/video/1234567890"

# Douyin
python video_downloader.py "https://www.douyin.com/video/1234567890"
```

### Chọn chất lượng video

```bash
# Chất lượng tốt nhất (mặc định)
python video_downloader.py <URL> -q best

# Full HD
python video_downloader.py <URL> -q 1080p

# HD
python video_downloader.py <URL> -q 720p

# SD
python video_downloader.py <URL> -q 480p
```

### Chọn thư mục lưu

```bash
python video_downloader.py <URL> -o "D:\Videos\TaiVe"
```

### Chỉ tải âm thanh (MP3)

```bash
python video_downloader.py <URL> --audio-only
```

### Xem thông tin video (không tải)

```bash
python video_downloader.py <URL> --info
```

### Tải hàng loạt từ file

Tạo file `urls.txt` chứa danh sách URL, mỗi dòng một URL:

```text
# Danh sách video cần tải
# (dòng bắt đầu bằng # sẽ bị bỏ qua)

https://www.youtube.com/watch?v=VIDEO_ID_1
https://www.youtube.com/watch?v=VIDEO_ID_2
https://www.bilibili.com/video/BV...
https://www.tiktok.com/@user/video/...
```

Chạy lệnh tải:

```bash
python video_downloader.py --batch urls.txt -q 720p -o my_videos
```

### Sử dụng cookies (cho video cần đăng nhập)

```bash
python video_downloader.py <URL> --cookies cookies.txt
```

> **Mẹo:** Dùng extension trình duyệt [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc) để xuất cookies.

---

## 🔧 Tham số dòng lệnh

| Tham số | Viết tắt | Mô tả | Mặc định |
|---|---|---|---|
| `url` | | URL video cần tải | *(bắt buộc)* |
| `--output` | `-o` | Thư mục lưu file | `downloads` |
| `--quality` | `-q` | Chất lượng: `best`, `1080p`, `720p`, `480p`, `360p`, `audio` | `best` |
| `--cookies` | | File cookies (Netscape format) | |
| `--batch` | | File chứa danh sách URL | |
| `--audio-only` | | Chỉ tải phần âm thanh (MP3) | |
| `--info` | | Xem thông tin video, không tải | |
| `--version` | | Hiển thị phiên bản | |
| `--help` | `-h` | Hiển thị trợ giúp | |

---

## 📁 Cấu trúc dự án

```
video-downloader-cli/
├── video_downloader.py   # Script chính
├── requirements.txt      # Thư viện phụ thuộc
├── .gitignore            # File ẩn thư mục rác
├── README.md             # Hướng dẫn sử dụng (file này)
└── downloads/            # Thư mục chứa video đã tải (tự động tạo)
```

---

## ❓ Câu hỏi thường gặp

<details>
<summary><b>Video Bilibili không tải được?</b></summary>

Một số video Bilibili yêu cầu đăng nhập. Hãy xuất cookies từ trình duyệt và sử dụng tham số `--cookies`:
```bash
python video_downloader.py <URL_BILIBILI> --cookies cookies.txt
```
</details>

<details>
<summary><b>Link TikTok/Douyin rút gọn không hoạt động?</b></summary>

Hãy mở link rút gọn trong trình duyệt, sao chép URL đầy đủ từ thanh địa chỉ rồi dùng URL đó.
</details>

<details>
<summary><b>Lỗi "ffmpeg not found"?</b></summary>

FFmpeg cần thiết để ghép video và audio chất lượng cao. Xem phần [Cài đặt FFmpeg](#cài-đặt-ffmpeg) ở trên.
</details>

<details>
<summary><b>Muốn cập nhật yt-dlp?</b></summary>

```bash
pip install --upgrade yt-dlp
```
</details>

---

## 📜 Giấy phép

Dự án này sử dụng giấy phép [MIT](https://opensource.org/licenses/MIT).
