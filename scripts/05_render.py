# -*- coding: utf-8 -*-
"""
Step 5: composite screenshots/memes into the rounded box with Ken-Burns motion,
concat all segments, burn in captions.ass, mux the atempo'd narration audio.

>>> CUSTOMIZE PER STORY: IMG_DIR, PEPE_DIR (or delete meme logic if unused),
    MEME_OVERRIDE, SHAKE_SEGMENTS. <<<

IMPORTANT: every image is ALWAYS cover-cropped to fill the box completely --
meme/cartoon images included. The rounded box must never show empty/black
padding; that's the whole visual point of this template. An earlier version
of this script letterboxed (contain+pad) meme/cartoon images, which put
black bars top/bottom inside the box -- rejected by the user 2026-09-14:
"안에 영상에 까만 공백이 있는 이미지가 들어가면 템플릿이 이상해져"
("if an image with black empty space goes in, the template looks broken").
Do not reintroduce a letterbox/contain path here. If a specific image would
crop away something essential, crop or re-frame the SOURCE IMAGE FILE itself
(e.g. in an image editor) before it reaches this script, rather than adding
padding logic back.
"""
import json, os, subprocess

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS_DIR = os.path.join(BASE, "assets", "fonts")
MASK_PATH = os.path.join(BASE, "assets", "box_mask.png")

# ============================== CUSTOMIZE ==============================
IMG_DIR = os.path.join(BASE, "stories", "cafe_dmain_47465221", "img")     # files named 01.png, 02.png, ...
PEPE_DIR = "C:/Users/최진영/volcano-work/군림보/fm_10323813802/pepe"              # only needed if MEME_OVERRIDE is non-empty

# segment id -> meme image path, when the meme comes from a SEPARATE library (e.g. a pepe
# folder) instead of this story's own IMG_DIR. Cover-cropped like everything else.
MEME_OVERRIDE = {}

# REQUIRED, not optional: segment ids that get the "trembling reveal" shake effect
# instead of normal Ken Burns, at the story's key/twist point (usually the PINK
# segment). Confirmed 2026-09-14 the user expects this on every video -- a batch of
# 4 videos built without it drew "핵심 포인트가 나올때는 이미지 덜덜덜 흔들라고 했잖아."
# Use sparingly (one beat per video); don't apply it to more than one segment.
SHAKE_SEGMENTS = {"s07"}
# =========================================================================

BOX_X, BOX_Y, BOX_W, BOX_H = 38, 369, 1004, 1143

with open(os.path.join(BASE, "work", "timeline.json"), encoding="utf-8") as f:
    tl = json.load(f)

segs = tl["segments"]
total_duration = tl["total_duration"]

ffmpeg = "ffmpeg"
args = [ffmpeg, "-y"]

durations = []
for i, seg in enumerate(segs):
    next_start = segs[i + 1]["start"] if i + 1 < len(segs) else total_duration
    dur = next_start - seg["start"]  # includes trailing silence gap, NOT just speech length,
    durations.append(dur)            # otherwise video track ends short of the audio track
    img_path = MEME_OVERRIDE.get(seg["id"], f"{IMG_DIR}/{seg['img']:02d}.png")
    args += ["-loop", "1", "-t", f"{dur:.3f}", "-i", img_path]
    args += ["-loop", "1", "-t", f"{dur:.3f}", "-i", MASK_PATH]

audio_path = os.path.join(BASE, "work", "el_full", "full_atempo.wav")
args += ["-i", audio_path]
audio_idx = len(segs) * 2

filt = []
for i, seg in enumerate(segs):
    dur = durations[i]
    frames = max(1, round(dur * 30))
    img_in = 2 * i
    mask_in = 2 * i + 1

    # CRITICAL: trim=end_frame=1 before zoompan on a looped image input.
    # Without it, zoompan restarts its zoom cycle once per input frame and the
    # output duration multiplies by ~100x (a 27s video became 1481s once).
    if seg["id"] in SHAKE_SEGMENTS:
        zexpr = "1.05"
        xexpr = "trunc(iw/2-(iw/zoom/2)+9*sin(on*2.4)+4*sin(on*5.1))"
        yexpr = "trunc(ih/2-(ih/zoom/2)+9*cos(on*2.7)+4*cos(on*4.6))"
        filt.append(
            f"[{img_in}:v]scale={BOX_W}:{BOX_H}:force_original_aspect_ratio=increase,crop={BOX_W}:{BOX_H},setsar=1,format=yuv420p,trim=end_frame=1,"
            f"zoompan=z='{zexpr}':x='{xexpr}':y='{yexpr}':d={frames}:s={BOX_W}x{BOX_H}:fps=30,format=rgba[boxed{i}]"
        )
    else:
        # max zoom capped at 1.05, not 1.13 -- 1.13 made images unrecognizably
        # tight, especially ones already cropped close to their subject (confirmed
        # 2026-09-14: "이미지들을 너무 확대해서 어떤 이미지인지 모르겠어"). Keep motion
        # subtle; the point is "not static," not "constant aggressive zoom."
        zoom_in = (i % 2 == 0)
        zexpr = "min(zoom+0.0006,1.05)" if zoom_in else "if(eq(on,0),1.05,max(zoom-0.0006,1.0))"
        filt.append(
            f"[{img_in}:v]scale={BOX_W}:{BOX_H}:force_original_aspect_ratio=increase,crop={BOX_W}:{BOX_H},setsar=1,format=yuv420p,trim=end_frame=1,"
            f"zoompan=z='{zexpr}':d={frames}:s={BOX_W}x{BOX_H}:fps=30,format=rgba[boxed{i}]"
        )

    filt.append(
        f"[{mask_in}:v]scale={BOX_W}:{BOX_H},format=gray,trim=end_frame=1,"
        f"zoompan=z='1':d={frames}:s={BOX_W}x{BOX_H}:fps=30,format=gray[mask{i}]"
    )
    filt.append(f"[boxed{i}][mask{i}]alphamerge[masked{i}]")
    filt.append(f"color=black:size=1080x1920:rate=30:d={dur:.3f}[bg{i}]")
    filt.append(f"[bg{i}][masked{i}]overlay=x={BOX_X}:y={BOX_Y}:format=yuv420[v{i}]")

concat_inputs = "".join(f"[v{i}]" for i in range(len(segs)))
filt.append(f"{concat_inputs}concat=n={len(segs)}:v=1:a=0[vc]")

# Windows absolute paths inside filter_complex need ':' escaped as '\:'
sub_path = os.path.join(BASE, "work", "captions.ass").replace("\\", "/").replace(":", "\\:")
fonts_dir_escaped = FONTS_DIR.replace("\\", "/").replace(":", "\\:")
filt.append(f"[vc]subtitles='{sub_path}':fontsdir='{fonts_dir_escaped}'[vout]")

filter_complex = ";".join(filt)

out_path = os.path.join(BASE, "work", "final.mp4")
args += [
    "-filter_complex", filter_complex,
    "-map", "[vout]",
    "-map", f"{audio_idx}:a",
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium",
    "-c:a", "aac", "-b:a", "192k",
    out_path,
]

print("Running ffmpeg with", len(segs), "segments...")
res = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
print("returncode:", res.returncode)
if res.returncode != 0:
    print("STDERR TAIL:\n", res.stderr[-5000:])
else:
    print("OK ->", out_path)
