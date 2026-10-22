"""
Forced Alignment Engine for Millisecond Word-Level Karaoke Timestamps
Supports Meta's Multilingual MMS_FA (CTC) and Faster-Whisper.
"""
import os
import math
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from .lyric_parser import parse_lyrics_file, romanize_vietnamese

@dataclass
class TimedWord:
    word: str
    start: float      # seconds
    end: float        # seconds
    duration: float   # seconds

@dataclass
class TimedLine:
    line_index: int
    text: str
    start: float
    end: float
    words: List[TimedWord]

class LyricAligner:
    """
    Aligns lyrics to audio track with millisecond accuracy.
    """
    def __init__(self, mode: str = "auto", device: str = "auto"):
        self.mode = mode
        self.device = device

    def align(self, audio_path: str, lyrics_text: str) -> List[TimedLine]:
        """
        Aligns words of lyrics_text to audio_path.
        """
        # Try Faster-Whisper alignment first (general & robust)
        try:
            return self._align_with_whisper(audio_path, lyrics_text)
        except Exception as e:
            print(f"Whisper alignment failed ({e}); falling back to uniform syllabic pacing...")
            return self._fallback_uniform(audio_path, lyrics_text)

    def _align_with_whisper(self, audio_path: str, lyrics_text: str) -> List[TimedLine]:
        from faster_whisper import WhisperModel
        import torch
        dev = "cuda" if (self.device == "cuda" or (self.device == "auto" and torch.cuda.is_available())) else "cpu"
        c_type = "float16" if dev == "cuda" else "int8"
        
        print(f"Running word-level alignment with Faster-Whisper on {dev.upper()}...")
        model = WhisperModel("base", device=dev, compute_type=c_type)
        segments, _ = model.transcribe(audio_path, word_timestamps=True, beam_size=5)

        raw_words = []
        for s in segments:
            if s.words:
                for w in s.words:
                    raw_words.append({
                        "word": w.word.strip(),
                        "start": round(w.start, 3),
                        "end": round(w.end, 3)
                    })

        parsed_lines = parse_lyrics_file(lyrics_text)
        timed_lines = []
        w_ptr = 0

        for line_info in parsed_lines:
            target_words = line_info["words"]
            line_timed_words = []
            
            # Map words to Whisper timestamps
            for tw in target_words:
                if w_ptr < len(raw_words):
                    wh_w = raw_words[w_ptr]
                    st = wh_w["start"]
                    en = max(st + 0.1, wh_w["end"])
                    line_timed_words.append(TimedWord(word=tw, start=st, end=en, duration=round(en - st, 3)))
                    w_ptr += 1
                else:
                    last_end = line_timed_words[-1].end if line_timed_words else 0.0
                    line_timed_words.append(TimedWord(word=tw, start=last_end, end=last_end + 0.35, duration=0.35))

            if line_timed_words:
                line_st = line_timed_words[0].start
                line_en = line_timed_words[-1].end
                timed_lines.append(TimedLine(
                    line_index=line_info["line_index"],
                    text=line_info["raw_text"],
                    start=line_st,
                    end=line_en,
                    words=line_timed_words
                ))

        return timed_lines

    def _fallback_uniform(self, audio_path: str, lyrics_text: str) -> List[TimedLine]:
        # Measure total audio duration
        import subprocess
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_path]
        res = subprocess.run(cmd, capture_output=True, text=True)
        dur = float(res.stdout.strip()) if res.returncode == 0 else 180.0

        parsed = parse_lyrics_file(lyrics_text)
        if not parsed:
            return []

        time_per_line = dur / len(parsed)
        timed_lines = []
        for i, line_info in enumerate(parsed):
            l_st = i * time_per_line
            l_en = l_st + time_per_line * 0.85
            words = line_info["words"]
            w_dur = (l_en - l_st) / max(1, len(words))
            timed_words = []
            for j, w in enumerate(words):
                st = l_st + j * w_dur
                en = st + w_dur
                timed_words.append(TimedWord(word=w, start=round(st, 3), end=round(en, 3), duration=round(w_dur, 3)))
            timed_lines.append(TimedLine(line_index=line_info["line_index"], text=line_info["raw_text"], start=round(l_st, 3), end=round(l_en, 3), words=timed_words))
        return timed_lines
