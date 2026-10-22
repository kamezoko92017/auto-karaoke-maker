"""
End-to-End Automated Karaoke Production Pipeline
"""
import os
from typing import Optional, Dict, Any
from .separator import AudioSeparator
from .aligner import LyricAligner
from .ass_builder import ASSBuilder
from .video_renderer import VideoRenderer

class AutoKaraokePipeline:
    def __init__(self, engine: str = "auto", language: str = "vi", use_gpu: bool = True):
        self.separator = AudioSeparator(use_gpu=use_gpu)
        self.aligner = LyricAligner(engine=engine, language=language, device="cuda" if use_gpu else "cpu")
        self.renderer = VideoRenderer()

    def create_karaoke(
        self,
        song_audio_path: str,
        lyrics_text: str,
        output_dir: str = "output",
        background_media: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes complete Karaoke generation:
        1. Separate vocals & instrumental beat (Demucs v4)
        2. Align lyrics to vocal stem down to millisecond (Meta MMS_FA / Whisper)
        3. Build Karaoke ASS subtitle with animated \\k highlight tags
        4. Render ready-to-sing Karaoke MP4 video
        """
        os.makedirs(output_dir, exist_ok=True)
        song_name = os.path.splitext(os.path.basename(song_audio_path))[0]

        print("[1/4] Separating Vocal & Instrumental Beat (Demucs v4)...")
        stems_dir = os.path.join(output_dir, "stems")
        voc_path, inst_path = self.separator.separate(song_audio_path, stems_dir)
        print(f"      Beat: {inst_path}\n      Vocal: {voc_path}")

        print(f"[2/4] Aligning Lyrics to Vocal Stem (Engine: {self.aligner.engine}, Lang: {self.aligner.language})...")
        timed_lines = self.aligner.align(voc_path, lyrics_text)
        print(f"      Aligned {len(timed_lines)} lines with running word timings.")

        print("[3/4] Generating Animated Karaoke Subtitles (.ass & .lrc)...")
        ass_path = os.path.join(output_dir, f"{song_name}_karaoke.ass")
        lrc_path = os.path.join(output_dir, f"{song_name}_karaoke.lrc")
        
        ass_content = ASSBuilder.build_ass_content(timed_lines)
        with open(ass_path, "w", encoding="utf-8") as f:
            f.write(ass_content)

        lrc_content = ASSBuilder.build_lrc_content(timed_lines)
        with open(lrc_path, "w", encoding="utf-8") as f:
            f.write(lrc_content)

        print("[4/4] Rendering Final Karaoke MP4 Video (1080p)...")
        video_out = os.path.join(output_dir, f"{song_name}_karaoke_1080p.mp4")
        self.renderer.render_karaoke_video(
            beat_audio=inst_path,
            ass_subtitles=ass_path,
            output_video=video_out,
            background_media=background_media
        )

        print(f"[SUCCESS] Karaoke Production Complete: {video_out}")
        return {
            "video_path": video_out,
            "beat_path": inst_path,
            "vocal_path": voc_path,
            "ass_path": ass_path,
            "lrc_path": lrc_path,
            "line_count": len(timed_lines)
        }
