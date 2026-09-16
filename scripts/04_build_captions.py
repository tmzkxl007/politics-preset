# -*- coding: utf-8 -*-
"""
Step 4: build the ASS subtitle file (title + 3-line stacked, right-aligned,
auto-fit, one-glow-per-segment rolling captions).

>>> CUSTOMIZE PER STORY: TITLE_LINE1, TITLE_LINE2, KEYWORDS. <<<
Everything else (geometry, colors, font sizing math) is the confirmed preset spec.
"""
import json, os
from PIL import ImageFont

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(BASE, "assets", "fonts", "S-CoreDream-7ExtraBold.ttf")
# ASS Fontname MUST be the TTF's internal name-table value, not the filename.
# For S-CoreDream-7ExtraBold.ttf that internal name is "S-Core Dream 7 ExtraBold" (with spaces).
ASS_FONT_NAME = "S-Core Dream 7 ExtraBold"

with open(os.path.join(BASE, "work", "timeline.json"), encoding="utf-8") as f:
    tl = json.load(f)

W, H = 1080, 1920
BOX_X, BOX_Y, BOX_W, BOX_H = 38, 369, 1004, 1143   # rounded video box geometry (confirmed spec)
RIGHT_X = BOX_X + BOX_W - 50                        # captions are right-aligned inside the box
TARGET_W = 900                                      # per-line auto-fit target pixel width
MIN_FS, MAX_FS = 65, 150                            # per-line font-size clamp
LINE_H_RATIO = 0.95
LINE_GAP = 12
BLOCK_CENTER_Y = 940                                # 3-line block is vertically centered here

# ============================== CUSTOMIZE ==============================
TITLE_LINE1 = "20년 계단만 탄 1층 주민이 거부한 것"   # white line, pos(540,110)
TITLE_LINE2 = "엘리베이터 교체비 200만원"                  # yellow line, pos(540,198)

# Exactly ONE glowing line per segment: seg_id -> keyword to glow. Whichever of the
# segment's (at most 3) chunk-lines actually contains this word gets the glow -- no
# need to track line-index by hand as segments get re-split. Pick the single most
# important word per segment (number / emotion / twist word) -- do NOT glow more than
# one line per segment, that was explicitly rejected in review.
KEYWORDS = {
    "card": "200만원",
    "s01":  "20년",
    "s02":  "똑같이",
    "s03":  "왜 내냐는",
    "ad1":  "주차장도",
    "s04":  "주요",
    "s05":  "장기수선충당금으로",
    "s06":  "집값",
    "s07":  "지하주차장도",
    "s08":  "이긴",
    "ad2":  "지하에",
    "s09":  "집주인이",
    "s10":  "남 일임",
    "s11":  "안 내도",
    "s14":  "억울하긴",
}
# =========================================================================

_font_cache = {}
def measure_width(text, fs):
    if fs not in _font_cache:
        _font_cache[fs] = ImageFont.truetype(FONT_PATH, fs)
    f = _font_cache[fs]
    bbox = f.getbbox(text)
    return bbox[2] - bbox[0]

def fit_size(text, target=TARGET_W):
    base = 100
    w = measure_width(text, base)
    if w == 0:
        return base
    size = int(target / w * base)
    return max(MIN_FS, min(MAX_FS, size))

def ass_time(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h:d}:{m:02d}:{s:05.2f}"

# caption glow color is derived from the segment's base color (WHITE/YELLOW/PINK/RED)
GLOW = {
    "WHITE": "&H001E1EFF&",   # red glow on default white lines
    "YELLOW": "&H0000D7FF&",  # gold glow
    "PINK": "&H00B469FF&",    # pink glow
    "RED": "&H001E1EFF&",     # red glow
}

def build_text(text, glow_color, fs, kw=None):
    if not kw or kw not in text:
        return f"{{\\fs{fs}}}{text}"
    idx = text.index(kw)
    before, after = text[:idx], text[idx + len(kw):]
    # \3c = glow color, \bord+\blur = halo, \u1 = underline, \i1 = synthetic italic tilt
    return (f"{{\\fs{fs}}}{before}"
            f"{{\\3c{glow_color}\\bord14\\blur9\\u1\\i1}}{kw}{{\\r\\fs{fs}}}"
            f"{after}")

def chunk_words(words, max_lines=3):
    """Split a segment's words into AT MOST max_lines evenly-sized chunks.
    No lonely trailing single-word chunk (round-then-distribute-remainder,
    not fixed-size chunking -- fixed-size left orphan 1-word lines)."""
    n = len(words)
    if n == 0:
        return []
    n_chunks = min(max_lines, n)
    base, rem = divmod(n, n_chunks)
    out, idx = [], 0
    for i in range(n_chunks):
        size = base + (1 if i < rem else 0)
        grp = words[idx:idx + size]
        out.append({"text": " ".join(w["text"] for w in grp), "start": grp[0]["start"], "end": grp[-1]["end"]})
        idx += size
    return out

header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: H1,{ASS_FONT_NAME},115,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,1,0,0,0,63,100,0,0,1,0,0,8,10,10,0,1
Style: H2,{ASS_FONT_NAME},160,&H0000FFFF,&H000000FF,&H00000000,&H00000000,1,0,0,0,75,100,0,0,1,0,0,8,10,10,0,1
Style: CAP,{ASS_FONT_NAME},85,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,6,0,6,10,10,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

total = tl["total_duration"]
lines = [header]

# Title uses explicit \pos() (NOT MarginV) -- libass's collision-avoidance silently
# overrides MarginV-based positioning between overlapping same-timerange lines otherwise.
lines.append(f"Dialogue: 0,{ass_time(0)},{ass_time(total)},H1,,0,0,0,,{{\\an8\\pos(540,110)}}{TITLE_LINE1}\n")
lines.append(f"Dialogue: 0,{ass_time(0)},{ass_time(total)},H2,,0,0,0,,{{\\an8\\pos(540,198)}}{TITLE_LINE2}\n")

for seg in tl["segments"]:
    color_key = seg["color"] if seg["id"] != "card" else "WHITE"
    glow = GLOW[color_key]
    chunks = chunk_words(seg["words"], 3)
    if not chunks:
        continue
    seg_end = seg["end"]
    fss = [fit_size(ch["text"]) for ch in chunks]
    heights = [fs * LINE_H_RATIO for fs in fss]
    total_h = sum(heights) + LINE_GAP * (len(chunks) - 1)
    cursor = BLOCK_CENTER_Y - total_h / 2
    y_positions = []
    for h in heights:
        y_positions.append(cursor + h / 2)
        cursor += h + LINE_GAP

    kw = KEYWORDS.get(seg["id"])
    glow_line_idx = None
    if kw:
        for p, ch in enumerate(chunks):
            if kw in ch["text"]:
                glow_line_idx = p
                break

    for p, ch in enumerate(chunks):
        start = ch["start"]
        y = round(y_positions[p])
        fs = fss[p]
        line_kw = kw if p == glow_line_idx else None
        text = build_text(ch["text"], glow, fs, line_kw)
        # each line is its own Dialogue event with a fixed \pos -- so line 1 never
        # shifts when line 2/3 later appear (this was explicitly required in review)
        lines.append(
            f"Dialogue: 1,{ass_time(start)},{ass_time(seg_end)},CAP,,0,0,0,,"
            f"{{\\an6\\pos({RIGHT_X},{y})}}{text}\n"
        )

out_path = os.path.join(BASE, "work", "captions.ass")
with open(out_path, "w", encoding="utf-8") as f:
    f.writelines(lines)
print("wrote", out_path)
