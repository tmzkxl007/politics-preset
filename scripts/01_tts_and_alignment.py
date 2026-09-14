# -*- coding: utf-8 -*-
"""
Step 1: synthesize the full narration in ONE ElevenLabs call and get
character-level alignment back. Produces el_full/full_raw.mp3 + alignment.json.

>>> CUSTOMIZE PER STORY: edit SEGMENTS, TAG_AFTER, TAG_BEFORE below. <<<
Everything else (voice id, model, endpoint) is fixed for this preset.
"""
import json, os, base64, urllib.request

KEY_PATH = os.path.expanduser("~/.volcano/keys/elevenlabs")
API_KEY = open(KEY_PATH, encoding="utf-8").read().strip()

# Cloned "뇌전구" voice on this ElevenLabs account. Do NOT use "뇌전구1" (different clone).
VOICE_ID = "USmorkqgfPMr7hEKz9xg"
MODEL_ID = "eleven_v3"  # required for inline [chuckles]/[laughs] audio tags; do not swap to v2 (loses tags)
ENDPOINT = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/with-timestamps"

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "work", "el_full")
os.makedirs(OUT, exist_ok=True)

# ============================== CUSTOMIZE ==============================
# (segment_id, color_key, exact spoken text)
# color_key must be one of WHITE / YELLOW / PINK / RED (used later for glow color mapping)
SEGMENTS = [
    ("card", "CARD", "퇴직금 안 주려고 11개월만 계약하는 정부기관 대통령이 저격함"),
    ("s01", "WHITE", "작년 12월 국무회의에서 물어봤는데"),
    ("s02", "WHITE", "11개월 15일 일하면 퇴직금 왜 안 주냐고"),
    ("s03", "YELLOW", "정부가 퇴직금 안 주려고 11개월씩 계약하고"),
    ("s04", "WHITE", "정규직 될까 봐 1년 11개월 만에 자르고"),
    ("ad1", "WHITE", "한 달 쉬었다 다시 뽑는 거임"),
    ("s05", "PINK", "민간은 몰라도 정부가 그러면 부도덕하다 했음"),
    ("s06", "WHITE", "그래서 4월에 공정수당이라는 걸 만들었는데"),
    ("s07", "WHITE", "퇴직금 대신 최대 248만원 주는 거임"),
    ("s08", "WHITE", "1년 미만 계약도 원칙적으로 금지했고"),
    ("ad2", "WHITE", "근데 6월에 감독 결과가 나왔음"),
    ("s09", "YELLOW", "지자체 30곳 조사했더니 30곳 전부 쪼개기 계약"),
    ("s10", "YELLOW", "364일짜리 계약만 1833명임"),
    ("s11", "WHITE", "28곳은 아예 노동법 위반 113건 걸림"),
    ("s14", "RED", "근데 솔직히 이 정도면 답 없는 거 아님?"),
]

# Inline ElevenLabs v3 audio tags (e.g. " [chuckles] ", "[laughs] ") to splice
# right after / before a given segment's text. Keep them OUT of SEGMENTS text
# itself -- this script strips them back out when matching segment spans.
TAG_AFTER = {}
TAG_BEFORE = {"ad1": "[chuckles] ", "ad2": "[laughs] "}
# =========================================================================

full_parts = []
for sid, color, text in SEGMENTS:
    prefix = TAG_BEFORE.get(sid, "")
    full_parts.append(prefix + text)
    suffix = TAG_AFTER.get(sid)
    if suffix:
        full_parts.append(suffix.strip())
full_text = " ".join(full_parts)
print("FULL TEXT:\n", full_text)
print("length:", len(full_text))

body = {"text": full_text, "model_id": MODEL_ID}
# NOTE: voice_settings.speed is silently ignored by eleven_v3 (confirmed by testing).
# Speed is applied later as a post-process ffmpeg atempo step (see step 2 README section),
# so no speed setting is sent here.
data = json.dumps(body, ensure_ascii=False).encode("utf-8")
req = urllib.request.Request(
    ENDPOINT, data=data, method="POST",
    headers={"xi-api-key": API_KEY, "Content-Type": "application/json; charset=utf-8"},
)
with urllib.request.urlopen(req, timeout=120) as resp:
    res = json.loads(resp.read().decode("utf-8"))

audio_bytes = base64.b64decode(res["audio_base64"])
with open(os.path.join(OUT, "full_raw.mp3"), "wb") as f:
    f.write(audio_bytes)

align = res["alignment"]
with open(os.path.join(OUT, "alignment.json"), "w", encoding="utf-8") as f:
    json.dump(
        {
            "full_text": full_text,
            "segments": [{"id": s[0], "color": s[1], "text": s[2]} for s in SEGMENTS],
            "alignment": align,
        },
        f, ensure_ascii=False, indent=2,
    )

print("chars in alignment:", len(align["characters"]))
print("audio + alignment saved to", OUT)
print()
print("NEXT: run this manually (fixed 1.15x tempo, ffmpeg speed knob does not work on v3):")
print(f'  ffmpeg -y -i "{OUT}/full_raw.mp3" -filter:a atempo=1.15 -ar 44100 "{OUT}/full_atempo.wav"')
