"""
FFmpeg Karaoke Video Rendering Engine
Burns synchronized animated karaoke subtitles onto beat audio with customizable video/image background.
"""
import os
import subprocess
from typing import Optional

class VideoRenderer:
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg = ffmpeg_path

    def render_karaoke_video(
        self,
        beat_audio: str,
        ass_subtitles: str,
        output_video: str,
        background_media: Optional[str] = None,
        resolution: str = "1920x1080",
        fps: int = 30
    ) -> str:
        """
        Renders ready-to-sing MP4 Karaoke video with burning ASS subtitles.
        """
        os.makedirs(os.path.dirname(os.path.abspath(output_video)), exist_ok=True)
        w, h = resolution.split("x")

        # Escape subtitle path for FFmpeg filter
        ass_esc = ass_subtitles.replace("\\", "/").replace(":", "\\:")

        if background_media and os.path.exists(background_media):
            # Using provided video or image background
            is_video = background_media.lower().endswith((".mp4", ".mov", ".mkv", ".webm"))
            if is_video:
                cmd = [
                    self.ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
                    "-stream_loop", "-1", "-i", background_media,
                    "-i", beat_audio,
                    "-filter_complex", f"[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},ass='{ass_esc}'[v]",
                    "-map", "[v]",
                    "-map", "1:a",
                    "-c:v", "libx264", "-preset", "fast", "-crf", "20",
                    "-c:a", "aac", "-b:a", "320k",
                    "-shortest",
                    output_video
                ]
            else: # Still image background
                cmd = [
                    self.ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
                    "-loop", "1", "-i", background_media,
                    "-i", beat_audio,
                    "-filter_complex", f"[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},ass='{ass_esc}'[v]",
                    "-map", "[v]",
                    "-map", "1:a",
                    "-c:v", "libx264", "-preset", "fast", "-crf", "20",
                    "-c:a", "aac", "-b:a", "320k",
                    "-shortest",
                    output_video
                ]
        else:
            # Generate aesthetic dark gradient background dynamically
            gradient_filter = f"color=c=0x111625:s={w}x{h}:r={fps},drawbox=x=0:y=0:w={w}:h={h}:color=0x0a0e17@0.6:t=fill,ass='{ass_esc}'[v]"
            cmd = [
                self.ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
                "-f", "lavfi", "-i", f"color=c=0x0f172a:s={w}x{h}:r={fps}",
                "-i", beat_audio,
                "-filter_complex", f"[0:v]ass='{ass_esc}'[v]",
                "-map", "[v]",
                "-map", "1:a",
                "-c:v", "libx264", "-preset", "fast", "-crf", "20",
                "-c:a", "aac", "-b:a", "320k",
                "-shortest",
                output_video
            ]

        print("Rendering final Karaoke MP4 video with FFmpeg...")
        subprocess.run(cmd, check=True)
        return output_video
