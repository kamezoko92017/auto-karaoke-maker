"""
Lyrics Parser & Vietnamese Syllabic Tokenizer
Splits lyrics into clean lines and word units suitable for millisecond Karaoke alignment.
"""
import re
import unicodedata
from typing import List, Dict, Any

def romanize_vietnamese(text: str) -> str:
    """Converts Vietnamese words to base latin characters for CTC alignment."""
    t = text.lower().replace("đ", "d")
    t = "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z']", "", t)

def clean_lyric_line(line: str) -> str:
    """Removes chords, brackets, stage directions like [Chorus], [Verse], (x2)."""
    line = re.sub(r"\[.*?\]", "", line)
    line = re.sub(r"\(.*?\)", "", line)
    return line.strip()

def split_into_words(line: str) -> List[str]:
    """Splits a line into words while stripping surrounding punctuation."""
    words = []
    for token in line.strip().split():
        cleaned = re.sub(r"^[^\w\d]+|[^\w\d]+$", "", token)
        if cleaned:
            words.append(cleaned)
    return words

def parse_lyrics_file(lyrics_text: str) -> List[Dict[str, Any]]:
    """
    Parses lyrics into structured lines and words.
    Returns: List of {"line_index": int, "raw_text": str, "words": List[str]}
    """
    parsed = []
    idx = 1
    for raw in lyrics_text.splitlines():
        cleaned = clean_lyric_line(raw)
        words = split_into_words(cleaned)
        if words:
            parsed.append({
                "line_index": idx,
                "raw_text": cleaned,
                "words": words
            })
            idx += 1
    return parsed
