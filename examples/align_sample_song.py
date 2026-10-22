import sys, os
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from auto_karaoke.aligner import LyricAligner
from auto_karaoke.ass_builder import ASSBuilder

aligner = LyricAligner()

lyrics = """
Sáng nay nắng vàng trên mái nhà
Mẹ phơi áo trắng ngoài hiên xa
Con đường quen dẫn về chợ nhỏ
Tiếng rao vang mãi chẳng phai nhoà
"""

audio_file = "sample_vocals.wav"
if not os.path.exists(audio_file):
    print("Vui lòng chuẩn bị file âm thanh sample_vocals.wav để chạy thử.")
    sys.exit(0)

print("Đang căn chỉnh lời bài hát theo từng từ...")
timed_lines = aligner.align(audio_file, lyrics)

print("\nKẾT QUẢ CĂN CHỮ KARAOKE:")
for line in timed_lines:
    print(f"[{line.start:.2f}s -> {line.end:.2f}s] {line.text}")
    for w in line.words:
        print(f"   -> {w.word} ({w.start:.2f}s - {w.end:.2f}s, kéo dài {w.duration * 1000:.0f}ms)")

# Xuất file phụ đề Karaoke .ass
ass_text = ASSBuilder.build_ass_content(timed_lines)
with open("sample_karaoke.ass", "w", encoding="utf-8") as f:
    f.write(ass_text)
print("\nĐã xuất file phụ đề Karaoke chuẩn: sample_karaoke.ass (Mở được bằng Aegisub/VLC/CapCut)!")
