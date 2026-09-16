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
    ("card", "CARD", "휴가 나온 군인이 네 번 만나자 했는데 네 번 다 까인 카톡임"),
    ("s01", "WHITE", "2018년 8월에 몇 년 만에 예은이한테 연락했는데"),
    ("s02", "WHITE", "군대 갔냐길래 지금 휴가라고 하니까"),
    ("s03", "YELLOW", "얼굴 보면 좋겠다더니 정작 시간은 안 된다는 거임"),
    ("ad1", "WHITE", "다음 휴가 때 연락하래"),
    ("s04", "WHITE", "11월 휴가엔 동아리 강원도 여행이고"),
    ("s05", "WHITE", "1월 휴가엔 친구들이랑 일본 여행이라"),
    ("s06", "YELLOW", "3월 초 한가하다길래 휴가를 거기 맞췄는데"),
    ("s07", "PINK", "이번엔 학생회 개강 회식이라 미안하다는 거임"),
    ("ad2", "WHITE", "저러다 결혼한다고 톡 오겠다는 댓글도 있음"),
    ("s08", "WHITE", "8개월 동안 네 번 물어봤는데"),
    ("s09", "WHITE", "매번 여행 아니면 회식임"),
    ("s10", "YELLOW", "댓글은 예은이 회피 스킬 지린다랑 남자가 눈치 없다로 갈림"),
    ("s11", "WHITE", "제목이 차라리 꺼지라고 해라 너무 잔인하다인 이유임"),
    ("s14", "RED", "근데 솔직히 세 번째 미안에서 눈치챘어야 함"),
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
