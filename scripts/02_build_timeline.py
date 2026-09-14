# -*- coding: utf-8 -*-
"""
Step 2: turn the character-level ElevenLabs alignment into a per-segment,
per-word timeline (timeline.json) that later scripts (captions, render) consume.

Run AFTER step 1's script + the manual `ffmpeg atempo=1.15` step have produced
work/el_full/alignment.json and work/el_full/full_atempo.wav.

>>> CUSTOMIZE PER STORY: IMG (segment id -> screenshot number in your image folder). <<<
ATEMPO must match whatever tempo you actually applied in the ffmpeg step.
"""
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(BASE, "work", "el_full", "alignment.json"), encoding="utf-8") as f:
    data = json.load(f)

full_text = data["full_text"]
segments_meta = data["segments"]
align = data["alignment"]
chars = align["characters"]
starts = align["character_start_times_seconds"]
ends = align["character_end_times_seconds"]
assert len(chars) == len(full_text) == len(starts) == len(ends)

ATEMPO = 1.15  # must match the atempo value used in the step-1 ffmpeg command

# ============================== CUSTOMIZE ==============================
# segment id -> which numbered screenshot (NN.png in your image folder) plays during it
IMG = {
    "card": 1, "s01": 2, "s02": 3, "s03": 4, "ad1": 5, "s04": 6, "s05": 7, "s06": 8,
    "s07": 9, "s08": 10, "ad2": 11, "s10": 12, "s11": 13, "s12": 14, "s14": 15,
}
# =========================================================================

# Walk full_text sequentially, matching each segment's text in order to get char index ranges.
# This works even with [chuckles]/[laughs] tags spliced in between segments, because we only
# ever search forward from the previous segment's end index.
cursor = 0
timeline = []
for seg in segments_meta:
    sid, color, text = seg["id"], seg["color"], seg["text"]
    idx = full_text.index(text, cursor)
    assert idx >= cursor, f"segment {sid} not found in order"
    start_idx = idx
    end_idx = idx + len(text)  # exclusive
    seg_start = starts[start_idx] / ATEMPO
    seg_end = ends[end_idx - 1] / ATEMPO

    words = []
    wstart = None
    wchars = []
    for i in range(start_idx, end_idx):
        ch = full_text[i]
        if ch == " ":
            if wchars:
                words.append({"text": "".join(wchars), "start": wstart / ATEMPO, "end": ends[i - 1] / ATEMPO})
                wchars = []
                wstart = None
            continue
        if wstart is None:
            wstart = starts[i]
        wchars.append(ch)
    if wchars:
        words.append({"text": "".join(wchars), "start": wstart / ATEMPO, "end": ends[end_idx - 1] / ATEMPO})

    timeline.append({
        "id": sid, "color": color, "img": IMG[sid],
        "start": seg_start, "end": seg_end, "text": text, "words": words,
    })
    cursor = end_idx

total_duration = ends[-1] / ATEMPO

out = {"total_duration": total_duration, "atempo": ATEMPO, "segments": timeline}
out_path = os.path.join(BASE, "work", "timeline.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print("total_duration(scaled):", round(total_duration, 3))
for t in timeline:
    print(f"  {t['id']:5s} img{t['img']} [{t['start']:.2f}-{t['end']:.2f}] words={len(t['words'])}")
print("wrote", out_path)
