"""
Vocal & Instrumental Stem Separation Module
Separates song into clean 'vocals.wav' and 'instrumental.wav' using Demucs or FFmpeg band filters.
"""
import os
import subprocess
from typing import Tuple, Optional

class AudioSeparator:
    def __init__(self, use_gpu: bool = True):
        self.use_gpu = use_gpu

    def separate(self, song_path: str, output_dir: str) -> Tuple[str, str]:
        """
        Separates song into (vocals_path, instrumental_path).
        """
        os.makedirs(output_dir, exist_ok=True)
        vocals_path = os.path.join(output_dir, "vocals.wav")
        instrumental_path = os.path.join(output_dir, "instrumental.wav")

        # 1. Try Demucs first (highest studio quality)
        try:
            print("Separating stems using Demucs v4 (htdemucs)...")
            cmd = [
                "demucs",
                "--two-stems", "vocals",
                *(["-d", "cuda"] if self.use_gpu else ["-d", "cpu"]),
                "-o", output_dir,
                song_path
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0:
                song_name = os.path.splitext(os.path.basename(song_path))[0]
                demucs_dir = os.path.join(output_dir, "htdemucs", song_name)
                d_voc = os.path.join(demucs_dir, "vocals.wav")
                d_inst = os.path.join(demucs_dir, "no_vocals.wav")
                if os.path.exists(d_voc) and os.path.exists(d_inst):
                    import shutil
                    shutil.move(d_voc, vocals_path)
                    shutil.move(d_inst, instrumental_path)
                    return vocals_path, instrumental_path
        except FileNotFoundError:
            pass

        # 2. Fast Fallback: FFmpeg center-channel vocal isolation / cancellation
        print("Demucs not found; using high-speed FFmpeg vocal isolation filter...")
        # Instrumental: center-channel vocal cancellation (OOPS filter)
        cmd_inst = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", song_path,
            "-filter_complex", "pan=stereo|c0=c0-c1|c1=c1-c0",
            instrumental_path
        ]
        subprocess.run(cmd_inst, check=True)

        # Vocals: center extraction + vocal frequency bandpass (300Hz - 3400Hz)
        cmd_voc = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", song_path,
            "-af", "highpass=f=200,lowpass=f=3500",
            vocals_path
        ]
        subprocess.run(cmd_voc, check=True)

        return vocals_path, instrumental_path
