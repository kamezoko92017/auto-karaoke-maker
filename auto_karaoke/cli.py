#!/usr/bin/env python3
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import argparse
from auto_karaoke.pipeline import AutoKaraokePipeline

def main():
    parser = argparse.ArgumentParser(description="Auto-Karaoke Maker CLI: Turn any song + lyrics into karaoke video")
    parser.add_argument("audio", help="Input song audio (mp3, wav, flac)")
    parser.add_argument("-l", "--lyrics", required=True, help="Path to lyrics text file")
    parser.add_argument("-o", "--output-dir", default="output", help="Output directory (default: output)")
    parser.add_argument("-b", "--background", help="Optional video/image background")
    parser.add_argument("--cpu", action="store_true", help="Force CPU mode")

    args = parser.parse_args()

    with open(args.lyrics, "r", encoding="utf-8") as f:
        lyrics_text = f.read()

    pipeline = AutoKaraokePipeline(use_gpu=not args.cpu)
    pipeline.create_karaoke(
        song_audio_path=args.audio,
        lyrics_text=lyrics_text,
        output_dir=args.output_dir,
        background_media=args.background
    )

if __name__ == "__main__":
    main()
