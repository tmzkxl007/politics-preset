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
    ("card", "CARD", "1층 주민이 엘리베이터 교체비 200만원 못 내겠다고 버팀"),
    ("s01", "WHITE", "20년 동안 한 번도 안 탔다는 게 이유인데"),
    ("s02", "YELLOW", "고층 주민들은 공용시설이니까 똑같이 내라는 거고"),
    ("s03", "YELLOW", "1층은 평생 걸어 다닌 내가 왜 내냐는 거임"),
    ("ad1", "WHITE", "안 내면 주차장도 막자는 얘기까지 나옴"),
    ("s04", "WHITE", "근데 법적으로는 엘리베이터가 아파트 주요 시설이라"),
    ("s05", "WHITE", "장기수선충당금으로 소유자 전원이 내는 게 원칙임"),
    ("s06", "PINK", "수원지법도 1층이 집값 오르는 이익 보니까 내라고 했음"),
    ("s07", "WHITE", "근데 지하주차장도 없는 구축 아파트에선"),
    ("s08", "WHITE", "1층 2층이 소송 걸어서 이긴 적도 있음"),
    ("ad2", "WHITE", "결국 주차장이 지하에 있냐 없냐 싸움임"),
    ("s09", "WHITE", "그리고 세입자는 안 내고 집주인이 내는 거라"),
    ("s10", "WHITE", "1층 세입자면 애초에 남 일임"),
    ("s11", "YELLOW", "다른 커뮤니티 댓글은 안 내도 된다는 쪽인데"),
    ("s14", "RED", "근데 솔직히 20년 계단이면 억울하긴 함"),
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
