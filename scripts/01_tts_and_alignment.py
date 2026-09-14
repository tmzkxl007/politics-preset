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
    ("card", "CARD", "대통령 지지율 9주 연속 빠져서 33.8% 찍음"),
    ("s01", "WHITE", "리얼미터 14일 조사 보니까"),
    ("s03", "YELLOW", "한 주 만에 3.6포인트 빠져서 취임 후 최저치인데"),
    ("s04", "WHITE", "부정 평가는 63.3%로 첫 60%대 진입임"),
    ("ad1", "WHITE", "매주 신기록 경신 중임"),
    ("s05", "WHITE", "4월엔 65.5%까지 갔던 지지율이"),
    ("s07", "PINK", "다섯 달 만에 딱 반 토막 난 셈임"),
    ("s08", "WHITE", "20대에서만 일주일 새 10.2포인트 빠졌고"),
    ("s09", "WHITE", "부산 울산 경남도 9.1포인트 내려감"),
    ("ad2", "WHITE", "바닥이 어딘지 아무도 모름"),
    ("s10", "YELLOW", "리얼미터는 개각 논란이랑 호르무즈 파병 검토"),
    ("s11", "YELLOW", "부동산 불확실성 탓이라고 봤음"),
    ("s12", "WHITE", "정당 지지도는 국힘 42.1% 민주 36.1%로"),
    ("s13", "YELLOW", "국힘이 6포인트 앞섬"),
    ("s14", "RED", "근데 솔직히 이 속도면 20%대도 시간문제 아님?"),
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
