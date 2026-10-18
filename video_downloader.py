#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║           VIDEO DOWNLOADER - Công cụ tải video CLI          ║
║      Hỗ trợ: YouTube, Bilibili, TikTok, Douyin             ║
╚══════════════════════════════════════════════════════════════╝

Tác giả: Video Downloader CLI
Phiên bản: 1.0.0
"""

import argparse
import os
import sys
import re
import json
import io
from datetime import datetime

# ── Sửa lỗi encoding Unicode trên Windows console ──
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="replace"
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer, encoding="utf-8", errors="replace"
        )

try:
    import yt_dlp
except ImportError:
    print("❌ Lỗi: Thư viện 'yt-dlp' chưa được cài đặt.")
    print("   Chạy lệnh: pip install -r requirements.txt")
    sys.exit(1)


# ──────────────────────────────────────────────────────────────
# Hằng số và cấu hình
# ──────────────────────────────────────────────────────────────

VERSION = "1.0.0"
DEFAULT_OUTPUT_DIR = "downloads"
SUPPORTED_PLATFORMS = {
    "youtube": {
        "name": "YouTube",
        "domains": ["youtube.com", "youtu.be", "youtube-nocookie.com"],
        "emoji": "🔴",
    },
    "bilibili": {
        "name": "Bilibili",
        "domains": ["bilibili.com", "b23.tv", "bilibili.tv"],
        "emoji": "📺",
    },
    "tiktok": {
        "name": "TikTok",
        "domains": ["tiktok.com", "vm.tiktok.com"],
        "emoji": "🎵",
    },
    "douyin": {
        "name": "Douyin",
        "domains": ["douyin.com", "iesdouyin.com"],
        "emoji": "🎶",
    },
}

QUALITY_PRESETS = {
    "best": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
    "1080p": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best[height<=1080]",
    "720p": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best[height<=720]",
    "480p": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best[height<=480]",
    "360p": "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]/best[height<=360]",
    "audio": "bestaudio[ext=m4a]/bestaudio",
}


# ──────────────────────────────────────────────────────────────
# Tiện ích hiển thị
# ──────────────────────────────────────────────────────────────

def print_banner():
    """Hiển thị banner chào mừng."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         📥  VIDEO DOWNLOADER CLI v{version}                  ║
║                                                              ║
║    Hỗ trợ: YouTube │ Bilibili │ TikTok │ Douyin             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """.format(version=VERSION)
    print(banner)


def print_separator(char="─", length=60):
    """In đường kẻ phân cách."""
    print(char * length)


def print_info(message):
    """In thông báo thông tin."""
    print(f"  ℹ️  {message}")


def print_success(message):
    """In thông báo thành công."""
    print(f"  ✅ {message}")


def print_warning(message):
    """In thông báo cảnh báo."""
    print(f"  ⚠️  {message}")


def print_error(message):
    """In thông báo lỗi."""
    print(f"  ❌ {message}")


def format_filesize(size_bytes):
    """Chuyển đổi kích thước byte sang định dạng đọc được."""
    if size_bytes is None:
        return "Không rõ"
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def format_duration(seconds):
    """Chuyển đổi giây sang định dạng HH:MM:SS."""
    if seconds is None:
        return "Không rõ"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


# ──────────────────────────────────────────────────────────────
# Nhận diện nền tảng
# ──────────────────────────────────────────────────────────────

def detect_platform(url):
    """
    Nhận diện nền tảng từ URL.

    Args:
        url: Đường dẫn video cần kiểm tra.

    Returns:
        Tuple (platform_key, platform_info) hoặc (None, None) nếu không nhận diện được.
    """
    url_lower = url.lower()
    for key, info in SUPPORTED_PLATFORMS.items():
        for domain in info["domains"]:
            if domain in url_lower:
                return key, info
    return None, None


# ──────────────────────────────────────────────────────────────
# Hook theo dõi tiến trình tải
# ──────────────────────────────────────────────────────────────

class DownloadProgressHook:
    """Hook hiển thị tiến trình tải video."""

    def __init__(self):
        self.start_time = None

    def __call__(self, d):
        if d["status"] == "downloading":
            if self.start_time is None:
                self.start_time = datetime.now()

            percent = d.get("_percent_str", "N/A").strip()
            speed = d.get("_speed_str", "N/A").strip()
            eta = d.get("_eta_str", "N/A").strip()
            downloaded = format_filesize(d.get("downloaded_bytes", 0))
            total = format_filesize(d.get("total_bytes") or d.get("total_bytes_estimate"))

            progress_bar = self._build_progress_bar(d)
            sys.stdout.write(
                f"\r  📥 {progress_bar} {percent} │ {downloaded}/{total} │ ⚡ {speed} │ ⏱️ ETA: {eta}   "
            )
            sys.stdout.flush()

        elif d["status"] == "finished":
            sys.stdout.write("\n")
            filename = os.path.basename(d.get("filename", ""))
            print_success(f"Tải xong: {filename}")

        elif d["status"] == "error":
            sys.stdout.write("\n")
            print_error("Lỗi trong quá trình tải!")

    @staticmethod
    def _build_progress_bar(d, width=25):
        """Tạo thanh tiến trình ASCII."""
        percent_str = d.get("_percent_str", "0%").strip().replace("%", "")
        try:
            percent = float(percent_str)
        except ValueError:
            percent = 0

        filled = int(width * percent / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"


# ──────────────────────────────────────────────────────────────
# Lớp chính: VideoDownloader
# ──────────────────────────────────────────────────────────────

class VideoDownloader:
    """
    Lớp quản lý tải video từ nhiều nền tảng.

    Attributes:
        output_dir: Thư mục lưu video.
        quality: Chất lượng video mong muốn.
        cookies_file: Đường dẫn file cookies (tuỳ chọn).
    """

    def __init__(self, output_dir=DEFAULT_OUTPUT_DIR, quality="best", cookies_file=None):
        self.output_dir = output_dir
        self.quality = quality
        self.cookies_file = cookies_file
        self._ensure_output_dir()

    def _ensure_output_dir(self):
        """Tạo thư mục đầu ra nếu chưa tồn tại."""
        os.makedirs(self.output_dir, exist_ok=True)

    def _get_base_opts(self):
        """Trả về cấu hình cơ bản cho yt-dlp."""
        format_str = QUALITY_PRESETS.get(self.quality, QUALITY_PRESETS["best"])

        opts = {
            "format": format_str,
            "outtmpl": os.path.join(self.output_dir, "%(title)s.%(ext)s"),
            "progress_hooks": [DownloadProgressHook()],
            "merge_output_format": "mp4",
            "noplaylist": True,
            "consoletitle": False,
            "quiet": True,
            "no_warnings": True,
            # Tránh lỗi chứng chỉ SSL trên một số hệ thống
            "nocheckcertificate": True,
            # Metadata
            "writethumbnail": False,
            "writesubtitles": False,
            # Retry
            "retries": 5,
            "fragment_retries": 5,
        }

        if self.cookies_file and os.path.isfile(self.cookies_file):
            opts["cookiefile"] = self.cookies_file

        return opts

    def _get_platform_opts(self, platform_key):
        """
        Trả về cấu hình riêng cho từng nền tảng.

        Args:
            platform_key: Khoá nhận diện nền tảng (youtube, bilibili, tiktok, douyin).

        Returns:
            Dict cấu hình bổ sung.
        """
        extra = {}

        if platform_key == "bilibili":
            # Bilibili thường cần referer header
            extra["http_headers"] = {
                "Referer": "https://www.bilibili.com",
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
            }

        elif platform_key in ("tiktok", "douyin"):
            extra["http_headers"] = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
            }

        return extra

    def get_video_info(self, url):
        """
        Lấy thông tin video mà không tải về.

        Args:
            url: Đường dẫn video.

        Returns:
            Dict chứa thông tin video, hoặc None nếu thất bại.
        """
        platform_key, platform_info = detect_platform(url)
        opts = self._get_base_opts()
        opts.update(self._get_platform_opts(platform_key))
        opts["quiet"] = True
        opts["no_warnings"] = True

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(url, download=False)
        except Exception as e:
            print_error(f"Không thể lấy thông tin video: {e}")
            return None

    def print_video_info(self, info):
        """Hiển thị thông tin video đã lấy được."""
        if not info:
            return

        print_separator("─")
        print(f"  📋 THÔNG TIN VIDEO")
        print_separator("─")
        print(f"  📌 Tiêu đề  : {info.get('title', 'Không rõ')}")
        print(f"  👤 Kênh     : {info.get('uploader', info.get('channel', 'Không rõ'))}")
        print(f"  ⏱️  Thời lượng: {format_duration(info.get('duration'))}")
        print(f"  👁️  Lượt xem : {info.get('view_count', 'Không rõ'):,}" if isinstance(info.get('view_count'), int) else f"  👁️  Lượt xem : Không rõ")
        print(f"  📅 Ngày đăng: {info.get('upload_date', 'Không rõ')}")
        print(f"  🌐 Nền tảng : {info.get('extractor', 'Không rõ')}")

        # Hiển thị danh sách định dạng nếu có
        formats = info.get("formats", [])
        if formats:
            resolutions = set()
            for f in formats:
                h = f.get("height")
                if h:
                    resolutions.add(h)
            if resolutions:
                res_list = sorted(resolutions, reverse=True)
                res_str = ", ".join(f"{r}p" for r in res_list)
                print(f"  🎬 Chất lượng: {res_str}")

        print_separator("─")

    def download(self, url):
        """
        Tải video từ URL.

        Args:
            url: Đường dẫn video cần tải.

        Returns:
            True nếu tải thành công, False nếu thất bại.
        """
        platform_key, platform_info = detect_platform(url)

        if platform_info:
            emoji = platform_info["emoji"]
            name = platform_info["name"]
            print_info(f"Nền tảng: {emoji} {name}")
        else:
            print_warning("Không nhận diện được nền tảng. Sẽ thử tải bằng yt-dlp mặc định.")

        # Lấy và hiển thị thông tin video
        print_info("Đang lấy thông tin video...")
        info = self.get_video_info(url)
        if info:
            self.print_video_info(info)

        # Bắt đầu tải
        print_info(f"Bắt đầu tải (chất lượng: {self.quality})...")
        print_info(f"Lưu vào: {os.path.abspath(self.output_dir)}")
        print()

        opts = self._get_base_opts()
        if platform_key:
            opts.update(self._get_platform_opts(platform_key))

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            print()
            print_success("🎉 Tải video thành công!")
            return True

        except yt_dlp.utils.DownloadError as e:
            print()
            print_error(f"Lỗi tải video: {e}")
            if platform_key == "bilibili":
                print_warning("Mẹo: Video Bilibili có thể cần cookies. Dùng --cookies <file>")
            elif platform_key in ("tiktok", "douyin"):
                print_warning("Mẹo: Hãy thử dùng URL gốc (không rút gọn).")
            return False

        except KeyboardInterrupt:
            print()
            print_warning("Đã huỷ tải video.")
            return False

        except Exception as e:
            print()
            print_error(f"Lỗi không xác định: {e}")
            return False

    def download_audio_only(self, url):
        """
        Tải chỉ phần âm thanh từ video.

        Args:
            url: Đường dẫn video.

        Returns:
            True nếu thành công, False nếu thất bại.
        """
        original_quality = self.quality
        self.quality = "audio"

        opts = self._get_base_opts()
        # Ghi đè cấu hình cho audio
        opts["format"] = "bestaudio[ext=m4a]/bestaudio"
        opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "320",
        }]
        opts["outtmpl"] = os.path.join(self.output_dir, "%(title)s.%(ext)s")

        platform_key, _ = detect_platform(url)
        if platform_key:
            opts.update(self._get_platform_opts(platform_key))

        print_info("Chế độ: 🎵 Chỉ tải âm thanh (MP3 320kbps)")
        print_info(f"Lưu vào: {os.path.abspath(self.output_dir)}")
        print()

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            print()
            print_success("🎉 Tải âm thanh thành công!")
            self.quality = original_quality
            return True
        except Exception as e:
            print_error(f"Lỗi tải âm thanh: {e}")
            self.quality = original_quality
            return False

    def download_batch(self, urls):
        """
        Tải nhiều video cùng lúc.

        Args:
            urls: Danh sách các URL cần tải.

        Returns:
            Tuple (số thành công, số thất bại).
        """
        total = len(urls)
        success = 0
        failed = 0

        print_info(f"Bắt đầu tải {total} video...")
        print_separator("═")

        for i, url in enumerate(urls, 1):
            url = url.strip()
            if not url or url.startswith("#"):
                continue

            print()
            print(f"  📦 [{i}/{total}] {url[:80]}{'...' if len(url) > 80 else ''}")
            print_separator("─")

            if self.download(url):
                success += 1
            else:
                failed += 1

            print_separator("═")

        print()
        print_separator("═")
        print(f"  📊 KẾT QUẢ: ✅ Thành công: {success} │ ❌ Thất bại: {failed} │ Tổng: {total}")
        print_separator("═")

        return success, failed


# ──────────────────────────────────────────────────────────────
# Hàm đọc file batch
# ──────────────────────────────────────────────────────────────

def read_url_file(filepath):
    """
    Đọc danh sách URL từ file văn bản.
    Mỗi dòng là một URL. Dòng bắt đầu bằng # sẽ bị bỏ qua.

    Args:
        filepath: Đường dẫn file chứa danh sách URL.

    Returns:
        List các URL.
    """
    if not os.path.isfile(filepath):
        print_error(f"Không tìm thấy file: {filepath}")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        urls = [
            line.strip()
            for line in f
            if line.strip() and not line.strip().startswith("#")
        ]

    if not urls:
        print_error("File không chứa URL nào hợp lệ.")
        sys.exit(1)

    return urls


# ──────────────────────────────────────────────────────────────
# Xử lý đối số dòng lệnh
# ──────────────────────────────────────────────────────────────

def create_parser():
    """Tạo parser cho các đối số dòng lệnh."""
    parser = argparse.ArgumentParser(
        prog="video_downloader",
        description=(
            "📥 Video Downloader CLI - Tải video từ YouTube, Bilibili, TikTok, Douyin\n"
            "Sử dụng thư viện yt-dlp"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ sử dụng:
  %(prog)s https://www.youtube.com/watch?v=VIDEO_ID
  %(prog)s https://www.bilibili.com/video/BV... -q 1080p
  %(prog)s https://www.tiktok.com/@user/video/... -o my_videos
  %(prog)s --batch urls.txt -q 720p
  %(prog)s https://youtube.com/watch?v=... --audio-only
  %(prog)s https://youtube.com/watch?v=... --info
        """,
    )

    parser.add_argument(
        "url",
        nargs="?",
        help="URL video cần tải",
    )

    parser.add_argument(
        "-o", "--output",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Thư mục lưu video (mặc định: {DEFAULT_OUTPUT_DIR})",
    )

    parser.add_argument(
        "-q", "--quality",
        default="best",
        choices=list(QUALITY_PRESETS.keys()),
        help="Chất lượng video: best, 1080p, 720p, 480p, 360p, audio (mặc định: best)",
    )

    parser.add_argument(
        "--cookies",
        default=None,
        help="Đường dẫn file cookies (Netscape format) cho video cần đăng nhập",
    )

    parser.add_argument(
        "--batch",
        default=None,
        metavar="FILE",
        help="Tải nhiều video từ file chứa danh sách URL (mỗi dòng 1 URL)",
    )

    parser.add_argument(
        "--audio-only",
        action="store_true",
        help="Chỉ tải âm thanh (MP3 320kbps)",
    )

    parser.add_argument(
        "--info",
        action="store_true",
        help="Chỉ hiển thị thông tin video, không tải",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s v{VERSION}",
    )

    return parser


# ──────────────────────────────────────────────────────────────
# Hàm main
# ──────────────────────────────────────────────────────────────

def main():
    """Điểm vào chính của chương trình."""
    parser = create_parser()
    args = parser.parse_args()

    print_banner()

    # Kiểm tra đầu vào
    if not args.url and not args.batch:
        parser.print_help()
        print()
        print_error("Vui lòng cung cấp URL video hoặc file batch (--batch).")
        sys.exit(1)

    # Khởi tạo downloader
    downloader = VideoDownloader(
        output_dir=args.output,
        quality=args.quality,
        cookies_file=args.cookies,
    )

    # Chế độ batch
    if args.batch:
        urls = read_url_file(args.batch)
        print_info(f"Đã đọc {len(urls)} URL từ file: {args.batch}")
        success, failed = downloader.download_batch(urls)
        sys.exit(0 if failed == 0 else 1)

    # Chế độ xem thông tin
    if args.info:
        info = downloader.get_video_info(args.url)
        if info:
            downloader.print_video_info(info)
        sys.exit(0)

    # Chế độ chỉ tải âm thanh
    if args.audio_only:
        result = downloader.download_audio_only(args.url)
        sys.exit(0 if result else 1)

    # Tải video bình thường
    result = downloader.download(args.url)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
