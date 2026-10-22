# Auto-Karaoke Maker 🎤✨

Hệ thống tự động **biến bất kỳ bài hát nào thành Video Karaoke chuyên nghiệp** với chữ chạy highlight đổi màu từng nốt ngân chuẩn xác như phòng hát dịch vụ!

---

## 🌟 Quy trình 4 bước hoàn toàn tự động

1. **Tách Vocal & Beat sạch sẽ:** Sử dụng AI **Demucs v4** của Meta để tách hoàn toàn giọng ca sĩ khỏi beat gốc, tạo ra bản nhạc nền karaoke (`instrumental.wav`) chất lượng phòng thu.
2. **Căn lời siêu chuẩn mili-giây (Word-level Forced Alignment):** Dùng AI nhận diện chính xác từng từ bắt đầu khi nào và nốt ngân kéo dài bao lâu (`start_time`, `end_time`, `duration`).
3. **Sinh phụ đề Karaoke chuẩn quốc tế (`.ass` & `.lrc`):** Tự động sinh file SubStation Alpha với thẻ `{\\k<centiseconds>}` đổi màu chữ từ trắng sang vàng/cyan theo đúng nhịp hát của ca sĩ.
4. **Dựng Video Karaoke MP4 1080p bằng FFmpeg:** Ghép beat nhạc + video/ảnh nền + phụ đề karaoke chạy chữ thành video MP4 sắc nét, sẵn sàng upload YouTube hoặc mở hát trên TV!

---

## 🧠 Phân tích chuyên sâu: Thư viện AI nào tốt nhất cho Tiếng Việt & Tiếng Nước Ngoài?

Để làm Karaoke chất lượng cao, bài toán khó nhất là **bắt đúng nốt ngân của ca sĩ** (ví dụ ca sĩ hát *"thương... ư... ư..."* kéo dài 3 giây thì chữ *"thương"* phải giữ màu highlight đúng 3 giây, không được ngắt sớm).

Dưới đây là so sánh chi tiết giữa 2 công nghệ căn lời hàng đầu được tích hợp sẵn trong repo:

| Tiêu chí so sánh | 🇻🇳 Meta MMS:FA (`--aligner mms`) | 🌍 Faster-Whisper / Stable-ts (`--aligner whisper`) |
| :--- | :--- | :--- |
| **Công nghệ cốt lõi** | **CTC Forced Alignment** (Mô hình Wav2Vec2 của Meta) | **Encoder-Decoder Cross-Attention** (OpenAI Whisper) |
| **Ngôn ngữ khuyên dùng** | **CỰC TỐT CHO TIẾNG VIỆT** (`vi`) & các tiếng chữ cái Latin | **CỰC TỐT CHO TIẾNG NƯỚC NGOÀI** (Anh, Trung, Nhật, Hàn...) |
| **Nguyên lý hoạt động** | Ép trực tiếp file lời bài hát chuẩn vào sóng âm thanh qua ma trận xác suất CTC | Nghe lại bài hát (ASR) rồi ước lượng vị trí xuất hiện của từng từ |
| **Nguy cơ nghe nhầm từ (Hallucination)** | **0% (Không bao giờ nhầm)** vì dùng chính xác lời bài hát do bạn cung cấp | **Có thể xảy ra** nếu ca sĩ hát luyến, hát giọng địa phương hoặc bè |
| **Bắt nốt ngân dài (Hold note)** | **Rất chuẩn** nhờ theo dõi energy & phoneme đến khi tắt tiếng | Dễ bị cắt ngắn nốt ngân (cần có `stable-ts` để ghim mốc kết thúc) |
| **Xử lý chữ tượng hình (Hán tự, Kana)** | Cần chuyển sang phiên âm Pinyin/Romaji trước khi căn chỉnh | **Hiểu trực tiếp chữ Hán, Hiragana, Katakana, Hangul** mà không cần phiên âm |
| **Khi không có sẵn lời bài hát** | Bắt buộc phải có text lời bài hát trước | **Tự động chép lời (Auto-transcribe)** rồi căn nhịp luôn |

### 📌 Khuyến nghị thực tế từ đội ngũ kỹ thuật:

1. **Hát nhạc Việt Nam (Nhạc Trẻ, Bolero, Rap Việt, Trữ Tình):**
   - **NÊN CHỌN:** `--aligner mms` (Meta MMS:FA).
   - **Lý do:** Tiếng Việt là ngôn ngữ **đơn âm tiết** (mỗi từ là 1 âm tiết có thanh điệu rõ rệt: *Em - thương - ai*). Thuật toán CTC Trellis của Meta MMS:FA quét với độ phân giải **20ms/frame** sẽ ghim nốt ngân từng từ tiếng Việt mượt mà nhất.
   
2. **Hát nhạc Quốc Tế (US-UK, Nhạc Hoa, K-Pop, J-Pop):**
   - **NÊN CHỌN:** `--aligner whisper` (Faster-Whisper + `stable-ts`).
   - **Lý do:** Tiếng Anh có từ đa âm tiết (*beau-ti-ful*, *to-ge-ther*), nối âm (*singing in* -> *sing-ing-in*); Tiếng Trung/Nhật là chữ tượng hình. Whisper được huấn luyện trên 680.000 giờ audio toàn cầu nên phân tích ngữ điệu đa ngôn ngữ và ngắt từ quốc tế chuẩn xác hơn.

---

## 🚀 Hướng dẫn cài đặt

### 1. Yêu cầu hệ thống:
- **Python 3.10 - 3.12**
- **FFmpeg** đã thêm vào PATH (dùng để encode video và xử lý âm thanh).

### 2. Cài đặt thư viện:
```bash
# Cài đặt PyTorch (khuyên dùng bản CUDA nếu máy có GPU NVIDIA):
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

# Cài đặt các gói AI chuyên dụng:
pip install -r requirements.txt
```

---

## 💻 Cách sử dụng

### 1. Căn lời bài hát Tiếng Việt (Khuyên dùng Meta MMS:FA):
```bash
python -m auto_karaoke "em_cua_ngay_hom_qua.mp3" \
  --lyrics "loi_bai_hat.txt" \
  --aligner mms \
  --lang vi \
  --background "mv_background.mp4" \
  --output-dir "output"
```

### 2. Căn lời bài hát Tiếng Anh / US-UK (Dùng Faster-Whisper):
```bash
python -m auto_karaoke "shape_of_you.mp3" \
  --lyrics "shape_of_you_lyrics.txt" \
  --aligner whisper \
  --lang en \
  --background "bg.jpg" \
  --output-dir "output"
```

### 3. Căn lời bài hát Tiếng Trung (Nhạc Hoa Lời Hoa):
```bash
python -m auto_karaoke "su_thanh.mp3" \
  --lyrics "chinese_lyrics.txt" \
  --aligner whisper \
  --lang zh \
  --output-dir "output"
```

Video thành phẩm sẽ được lưu tại: `output/<tên_bài_hát>_karaoke_1080p.mp4`

---

## 🐍 Sử dụng trong mã nguồn Python

```python
from auto_karaoke.pipeline import AutoKaraokePipeline

# Chọn 'mms' cho tiếng Việt, hoặc 'whisper' cho tiếng Anh/quốc tế
pipeline = AutoKaraokePipeline(engine="mms", language="vi", use_gpu=True)

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
print(f"Beat tách sạch (Demucs): {result['beat_path']}")
print(f"File phụ đề ASS: {result['ass_path']}")
```

---

## 🎨 Điểm mạnh của định dạng Subtitle `.ass`

File `.ass` do hệ thống tạo ra tương thích 100% với:
- **Aegisub:** Mở lên để chỉnh sửa màu sắc, font chữ, hiệu ứng lấp lánh (sparkles) nâng cao.
- **VLC / PotPlayer:** Mở bài hát lên chọn phụ đề là chữ tự nhảy màu theo nhịp.
- **CapCut / Premiere / DaVinci Resolve:** Import làm phụ đề video ca nhạc.

---

## ⚖️ License
Phát hành theo giấy phép **MIT**.
