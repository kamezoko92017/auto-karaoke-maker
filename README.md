# Auto-Karaoke Maker 🎤✨

Hệ thống tự động **biến bất kỳ bài hát nào thành Video Karaoke chuyên nghiệp** với chữ chạy highlight đổi màu từng nốt ngân chuẩn như phòng hát dịch vụ!

---

## 🌟 Quy trình 4 bước hoàn toàn tự động

1. **Tách Vocal & Beat sạch sẽ:** Sử dụng AI **Demucs v4** để tách hoàn toàn giọng ca sĩ khỏi beat nhạc gốc, tạo ra bản nhạc nền karaoke (`instrumental.wav`) chất lượng phòng thu.
2. **Căn lời siêu chuẩn mili-giây (Word-level Forced Alignment):** Dùng AI nhận diện chính xác từng từ khi nào bắt đầu được hát và nốt ngân kéo dài bao lâu (`start_time`, `end_time`, `duration`).
3. **Sinh phụ đề Karaoke chuẩn quốc tế (`.ass` & `.lrc`):** Tự động sinh file SubStation Alpha với thẻ `{\k<centiseconds>}` đổi màu chữ từ trắng sang vàng/cyan theo đúng nhịp hát của ca sĩ.
4. **Dựng Video Karaoke MP4 1080p bằng FFmpeg:** Ghép beat nhạc + video/ảnh nền + phụ đề karaoke chạy chữ thành video MP4 sắc nét, sẵn sàng upload YouTube hoặc mở hát trên TV!

---

## 🚀 Hướng dẫn cài đặt & Chạy thử nhanh

### 1. Yêu cầu hệ thống:
- **Python 3.10 - 3.12**
- **FFmpeg** đã thêm vào PATH (dùng để encode video và xử lý âm thanh).

### 2. Cài đặt thư viện:
```bash
# Cài đặt PyTorch (khuyên dùng bản CUDA nếu máy có GPU NVIDIA):
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

# Cài đặt các gói AI:
pip install -r requirements.txt
```

---

## 💻 Cách sử dụng

### 1. Dùng nhanh qua dòng lệnh (CLI):

```bash
# Biến 1 bài hát MP3 + file lời bài hát thành video Karaoke:
python -m auto_karaoke "bai_hat.mp3" \
  --lyrics "loi_bai_hat.txt" \
  --background "video_nen.mp4" \
  --output-dir "output"
```

Video thành phẩm sẽ được lưu tại: `output/bai_hat_karaoke_1080p.mp4`

---

### 2. Sử dụng trong mã nguồn Python:

```python
from auto_karaoke.pipeline import AutoKaraokePipeline

pipeline = AutoKaraokePipeline(use_gpu=True)

lyrics = """
Sáng nay nắng vàng trên mái nhà
Mẹ phơi áo trắng ngoài hiên xa
Con đường quen dẫn về chợ nhỏ
Tiếng rao vang mãi chẳng phai nhoà
"""

result = pipeline.create_karaoke(
    song_audio_path="bai_hat.mp3",
    lyrics_text=lyrics,
    output_dir="output",
    background_media="hinh_nen.jpg"  # hoặc video_nen.mp4
)

print(f"Video Karaoke hoàn tất: {result['video_path']}")
print(f"Beat tách sạch: {result['beat_path']}")
print(f"File phụ đề ASS: {result['ass_path']}")
```

---

## 🎨 Điểm mạnh của định dạng Subtitle `.ass`

File `.ass` do hệ thống tạo ra tương thích 100% với:
- **Aegisub:** Mở lên để chỉnh sửa màu sắc, font chữ, hiệu ứng lấp lánh nâng cao.
- **VLC / PotPlayer:** Mở bài hát lên chọn phụ đề là chữ tự nhảy màu theo nhịp.
- **CapCut / Premiere / DaVinci Resolve:** Import làm phụ đề video ca nhạc.

---

## ⚖️ License
Phát hành theo giấy phép **MIT**.
