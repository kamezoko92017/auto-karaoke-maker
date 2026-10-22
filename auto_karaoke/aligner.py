"""
Advanced Forced Alignment Engine for Millisecond Word-Level Karaoke Timestamps
Supports:
1. Meta MMS_FA (torchaudio.pipelines.MMS_FA) - Best for Vietnamese & Latin lyrics
2. Faster-Whisper / Stable-ts - Best for International songs (English, Chinese, Japanese, Korean)
3. Syllabic Fallback Pacing - Offline lightweight fallback
"""
import os
import re
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
    Aligns lyrics to audio track with millisecond precision.
    Engine options: 'auto', 'mms', 'whisper'
    """
    def __init__(self, engine: str = "auto", language: str = "vi", device: str = "auto"):
        self.engine = engine.lower()
        self.language = language.lower()
        self.device = device

    def align(self, audio_path: str, lyrics_text: str) -> List[TimedLine]:
        """
        Aligns words of lyrics_text to vocal audio track.
        """
        # Decide engine if 'auto'
        chosen_engine = self.engine
        if chosen_engine == "auto":
            # MMS is superior for Vietnamese monosyllabic tonal lyrics
            chosen_engine = "mms" if self.language in ["vi", "vie", "vietnamese"] else "whisper"

        if chosen_engine == "mms":
            try:
                print(f"[Aligner] Using Meta MMS_FA (CTC Forced Alignment) for language='{self.language}'...")
                return self._align_with_mms(audio_path, lyrics_text)
            except Exception as e:
                print(f"[Aligner] MMS_FA not available or encountered ({e}); falling back to Faster-Whisper...")
                try:
                    return self._align_with_whisper(audio_path, lyrics_text)
                except Exception as e2:
                    print(f"[Aligner] Whisper failed ({e2}); falling back to uniform syllabic pacing...")
                    return self._fallback_uniform(audio_path, lyrics_text)

        else: # 'whisper'
            try:
                print(f"[Aligner] Using Faster-Whisper Cross-Attention Alignment for language='{self.language}'...")
                return self._align_with_whisper(audio_path, lyrics_text)
            except Exception as e:
                print(f"[Aligner] Whisper failed ({e}); falling back to uniform pacing...")
                return self._fallback_uniform(audio_path, lyrics_text)

    def _align_with_mms(self, audio_path: str, lyrics_text: str) -> List[TimedLine]:
        """
        Meta MMS_FA (Massively Multilingual Speech Forced Alignment) via PyTorch & torchaudio.
        Best accuracy for Vietnamese because it calculates phoneme emission probabilities
        against the exact provided lyrics text without speech-to-text hallucination.
        """
        import torch
        import torchaudio

        dev = "cuda" if (self.device == "cuda" or (self.device == "auto" and torch.cuda.is_available())) else "cpu"
        bundle = torchaudio.pipelines.MMS_FA
        model = bundle.get_model().to(dev)
        tokenizer = bundle.get_tokenizer()
        aligner = bundle.get_aligner()

        waveform, sr = torchaudio.load(audio_path)
        if sr != bundle.sample_rate:
            waveform = torchaudio.functional.resample(waveform, sr, bundle.sample_rate)
        
        # Mix to mono
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)
        waveform = waveform.to(dev)

        # Build clean word list & normalized transcript
        parsed_lines = parse_lyrics_file(lyrics_text)
        all_words = []
        for line_info in parsed_lines:
            for w in line_info["words"]:
                # Romanize for CTC dictionary
                norm_w = romanize_vietnamese(w)
                if norm_w:
                    all_words.append((w, norm_w))

        if not all_words:
            return self._fallback_uniform(audio_path, lyrics_text)

        full_transcript = " ".join(norm_w for _, norm_w in all_words)
        
        with torch.inference_mode():
            emission, _ = model(waveform)
            tokens = tokenizer(full_transcript)
            alignments, scores = aligner(emission[0], tokens)
            spans = torchaudio.functional.merge_tokens(alignments, scores)

        # Convert spans back to seconds
        frame_duration = (waveform.shape[1] / bundle.sample_rate) / emission.shape[1]
        
        word_spans = []
        span_idx = 0
        for orig_w, norm_w in all_words:
            w_chars = len(norm_w)
            if span_idx + w_chars <= len(spans):
                start_frame = spans[span_idx].start
                end_frame = spans[span_idx + w_chars - 1].end
                st = round(start_frame * frame_duration, 3)
                en = round(max(st + 0.1, end_frame * frame_duration), 3)
                word_spans.append(TimedWord(word=orig_w, start=st, end=en, duration=round(en - st, 3)))
                span_idx += w_chars
            else:
                last_end = word_spans[-1].end if word_spans else 0.0
                word_spans.append(TimedWord(word=orig_w, start=last_end, end=last_end + 0.35, duration=0.35))

        # Re-assemble timed words into original lines
        timed_lines = []
        w_ptr = 0
        for line_info in parsed_lines:
            target_words = line_info["words"]
            line_timed_words = []
            for _ in target_words:
                if w_ptr < len(word_spans):
                    line_timed_words.append(word_spans[w_ptr])
                    w_ptr += 1
            if line_timed_words:
                timed_lines.append(TimedLine(
                    line_index=line_info["line_index"],
                    text=line_info["raw_text"],
                    start=line_timed_words[0].start,
                    end=line_timed_words[-1].end,
                    words=line_timed_words
                ))

        return timed_lines

    def _align_with_whisper(self, audio_path: str, lyrics_text: str) -> List[TimedLine]:
        """
        Faster-Whisper cross-attention word-level alignment.
        Excels for English, Chinese, Japanese, Korean where vocabulary & context
        resolve multisyllabic word boundaries and non-Latin logograms.
        """
        from faster_whisper import WhisperModel
        import torch
        dev = "cuda" if (self.device == "cuda" or (self.device == "auto" and torch.cuda.is_available())) else "cpu"
        c_type = "float16" if dev == "cuda" else "int8"
        
        model = WhisperModel("base", device=dev, compute_type=c_type)
        lang_arg = self.language if self.language not in ["auto", ""] else None
        segments, _ = model.transcribe(audio_path, language=lang_arg, word_timestamps=True, beam_size=5)

        raw_words = []
        for s in segments:
            if s.words:
                for w in s.words:
                    clean_w = w.word.strip()
                    if clean_w:
                        raw_words.append({
                            "word": clean_w,
                            "start": round(w.start, 3),
                            "end": round(w.end, 3)
                        })

        parsed_lines = parse_lyrics_file(lyrics_text)
        timed_lines = []
        w_ptr = 0

        for line_info in parsed_lines:
            target_words = line_info["words"]
            line_timed_words = []
            
            for tw in target_words:
                if w_ptr < len(raw_words):
                    wh_w = raw_words[w_ptr]
                    st = wh_w["start"]
                    en = max(st + 0.12, wh_w["end"])
                    line_timed_words.append(TimedWord(word=tw, start=st, end=en, duration=round(en - st, 3)))
                    w_ptr += 1
                else:
                    last_end = line_timed_words[-1].end if line_timed_words else 0.0
                    line_timed_words.append(TimedWord(word=tw, start=last_end, end=last_end + 0.35, duration=0.35))

            if line_timed_words:
                timed_lines.append(TimedLine(
                    line_index=line_info["line_index"],
                    text=line_info["raw_text"],
                    start=line_timed_words[0].start,
                    end=line_timed_words[-1].end,
                    words=line_timed_words
                ))

        return timed_lines

    def _fallback_uniform(self, audio_path: str, lyrics_text: str) -> List[TimedLine]:
        """Uniform duration fallback for minimal setups without AI acceleration."""
        import subprocess
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_path]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            dur = float(res.stdout.strip()) if res.returncode == 0 else 180.0
        except Exception:
            dur = 180.0

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
