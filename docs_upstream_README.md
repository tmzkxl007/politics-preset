# 둥근 뇌전구 (Rounded Noejeongu) preset

Reproducible pipeline for 뇌전구-channel shorts using the **rounded video-box
"한입만" template** — confirmed/finalized 2026-09-14 on the 층간소음 (floor-noise)
story (`cheungan-soeum-nuna_hainma_template_v002.mp4`).

This is a **manual ffmpeg/Python pipeline**, not the volcano MCP tool's built-in
뇌전구 preset — that preset was abandoned because it produces discrete
complete-sentence caption cards + AI-composited images, which does not match
the real channel's actual style (continuous rolling captions cut mid-sentence,
real screenshots/footage, a specific cloned narrator voice).

Give a future session **just this repo's link** and it should be able to build
a new video end-to-end by editing only the marked CUSTOMIZE sections below —
no re-deriving the geometry, no re-discovering the ffmpeg gotchas.

## Prerequisites

- `ffmpeg` on PATH (with libass/subtitles filter support).
- Python 3 with `Pillow` installed (`pip install Pillow`).
- An ElevenLabs API key at `~/.volcano/keys/elevenlabs`, with **Text to Speech**
  and **Voices** permissions enabled, on a **paid plan** (voice cloning /
  direct TTS API calls to account-owned cloned voices work on free tier, but
  most other things — e.g. shared/library voices — return 402 on free).
- The account must already have a voice cloned from the real 뇌전구 narrator,
  named **"뇌전구"** (NOT "뇌전구1", a different clone), voice_id
  `USmorkqgfPMr7hEKz9xg`. Find it via `GET https://api.elevenlabs.io/v2/voices`
  filtering `category == "cloned"`.
- A folder of real screenshots/footage stills for the story, numbered
  `01.png, 02.png, ...` (NOT AI-generated images — the real channel uses actual
  screenshots). Pull these from a **different video than wherever the facts
  came from** — see "Source material is material, not a template to copy"
  below.
- Optionally, a folder of reaction-meme images to splice in for 1-2 beats.

## Pipeline overview

```
scripts/01_tts_and_alignment.py   -> work/el_full/full_raw.mp3 + alignment.json
(manual) ffmpeg atempo=1.15       -> work/el_full/full_atempo.wav
scripts/02_build_timeline.py      -> work/timeline.json
scripts/03_make_box_mask.py       -> assets/box_mask.png   (run once, reusable)
scripts/04_build_captions.py      -> work/captions.ass
scripts/05_render.py              -> work/final.mp4
```

Run them in that order from the repo root (`python scripts/01_...py`, etc.).
`work/` is git-ignored — it's per-video scratch output.

### Customization points (edit these, nothing else, for a new story)

| Script | What to edit |
|---|---|
| `01_tts_and_alignment.py` | `SEGMENTS` (id, color, exact spoken text per beat), `TAG_AFTER`/`TAG_BEFORE` (where to splice `[chuckles]`/`[laughs]`) |
| `02_build_timeline.py` | `IMG` (segment id -> screenshot number) |
| `04_build_captions.py` | `TITLE_LINE1`, `TITLE_LINE2`, `KEYWORDS` (segment id -> keyword to glow; whichever of its chunk-lines contains the word gets the glow, no need to track line-index by hand) |
| `05_render.py` | `IMG_DIR`, `PEPE_DIR`, `MEME_OVERRIDE`, `SHAKE_SEGMENTS` |

Everything else (canvas size, box geometry, font sizing math, color mapping,
zoompan formulas) is the **confirmed spec** — do not change it per-story.

### Source material is material, not a template to copy

When the source is an existing YouTube video: reuse only its **facts**.
**Never reuse its title or sentence wording verbatim** — write an original
title (different sub-pattern or at least clearly different phrasing) and
rewrite every sentence in your own words before it goes anywhere near TTS.
Confirmed by the user 2026-09-14 after a first draft copied the source
video's exact title and phrasing.

**Images must also come from somewhere else, not from the fact-source video
— this applies to every video, not just one.** An earlier version of this
rule allowed cropping the fact-source video's own frames for footage; the
user overturned that 2026-09-14 and made it general: "소재만 쓰고 이미지는 항상 새로
구해서 써야해. 이영상 뿐 아니라 다른영상도 마찬가지야." Practically: after getting the
facts from the source video, web-search for a *different* video covering the
same trend/story/topic (a different creator's short is fine) and pull
screenshots/reaction images from that one instead. Real footage is still
required (no AI-generated images) — the point is separating "where the facts
came from" from "where the pictures came from," not relaxing the
real-footage rule. This also sidesteps the copyright exposure of a source
with an explicit no-redistribution/no-AI-use notice (e.g. Korean broadcaster
news content) — if the facts come from such a source, this rule means none
of its footage ends up in the video at all.

### Keep segments SHORT (learned from the 백령도/NLL video, 2026-09-14)

- Prefer **more, shorter segments (4-6 words each)** over fewer long ones. A
  9-13 word segment still only splits into at most 3 lines, so each line ends
  up carrying 3-4 words of often-long vocabulary — the auto-fit shrinks font
  to the MIN_FS clamp and the result reads as cramped/too-dense. Splitting a
  long factual sentence into two short segments (with its own short duration
  each) fixes this directly, and is very cheap to do since each segment is
  just one more tuple in `SEGMENTS` + one more `IMG` entry (can reuse the same
  image number as its neighbor).
- Total narration length matters less than segment shape: a 25-30s video built
  from 12-15 short (4-6 word) segments reads far cleaner than the same runtime
  built from 8-9 long (9-13 word) segments.
- **Use at least 15 distinct images per video** (confirmed requirement,
  2026-09-14). Don't have neighboring segments share the same image number as
  a default — pull enough different frames/screenshots so nearly every
  segment gets its own unique visual (a first pass reusing ~8 images across
  15 segments was rejected: "이미지 최소 15장 넣어야해"). When extracting frames
  from a source video at 1fps, check neighboring seconds aren't
  near-duplicates of the same graphic before picking one — several
  candidate frames one second apart can render as visually identical.
- **Every image is cover-cropped to fill the box, memes and cartoons
  included — never letterboxed/padded.** An earlier version of this preset
  letterboxed (contain+pad) meme/cartoon images to avoid cropping them, which
  put black bars top/bottom inside the rounded box. Rejected by the user
  2026-09-14: "안에 영상에 까만 공백이 있는 이미지가 들어가면 템플릿이 이상해져" — the
  whole visual point of this template is that the rounded box is always
  completely filled, so that rule beats "don't crop the meme." If cropping
  would cut off something essential in a specific image, fix that by
  re-framing/cropping the source image file before it reaches `05_render.py`
  (see `03_captions.py`'s per-story `img/` folder convention), not by adding
  padding logic to the renderer. Aim for **at least 2-3 distinct meme/graphic
  cuts** per video, more if the source material has them available.
- **Ad-libs at meme beats**: a short aside/reaction line (delivered with
  `[laughs]`/`[chuckles]`) works well layered right after a meme image's
  factual line — add it as its own short segment (own `SEGMENTS` tuple, same
  `IMG` number as the meme it rides on, `TAG_BEFORE` set to the tag) rather
  than cramming it into the factual sentence itself. **Use at least 2 ad-libs
  per video, and spread them through the middle of the timeline — don't
  cluster them near the end.** Confirmed 2026-09-14 after a batch where most
  videos had only one ad-lib near the very end: "중간에 에드립 2번 넣어줘."

### Source video download resolution (learned from the banknote video, 2026-09-14)

- **Don't filter by `height<=1080` for a vertical short.** A vertical short's
  actual "1080p" format is `1080x1920` (width x height) — filtering
  `height<=1080` wrongly excludes it and silently picks a much smaller
  `608x1080` stream instead (looks fine at a glance, since it happens to
  satisfy the filter, but it's really a low-res stream). This produced a
  visibly blurry video after the box's ~2.4x upscale. Check with `yt-dlp -F
  <url>` and pick the real highest-res progressive/mergeable format (here,
  format `137` mp4 1080x1920), or filter by `width<=1080` instead.
- Re-verify the title/content/caption band boundaries **per video** via a
  row-brightness scan (see "Confirmed visual spec" below) — don't reuse a
  previous video's exact pixel offsets even from the same channel template;
  confirm both the top AND bottom boundary precisely. A residual few-pixel
  sliver of the title bar's black background left inside the crop looks
  trivial at 1:1 scale but becomes a visible black bar once the box's
  ~1.4-2.4x scale-up stretches it.
- **Verify image content at full resolution before finalizing a fact-specific
  segment**, especially anything with numbers on it (banknote/coin
  denominations, dates, scores). A tiny thumbnail-scale contact sheet makes
  visually-similar frames (e.g. two different banknotes with similar color
  and layout) easy to misidentify — this caused two different segments
  (about two different bills) to end up pointing at the same wrong bill
  image in an early pass. Open the actual candidate frame full-size and
  read the printed numbers/text before assigning it to a segment.

### Lessons from a 4-video parallel batch (2026-09-14)

Four videos were built at once by separate agents from the same brief. Cross-cutting findings:

- **Verify a candidate image source isn't itself a broadcast repost.** Title
  and uploader name aren't enough — a channel that looks like a personal
  curation account can actually be re-uploading news-broadcast clips. Open an
  actual frame and check the corners for a small "영상출처: MBC/KBS" watermark
  or a network logo before committing to that source.
- **A single source video can mix real footage and AI-generated illustration
  across different scenes** (e.g. a real interview clip followed by an
  animated AI-illustrated cutaway). Check every candidate frame's art style
  individually — don't assume a video is "real footage" as a whole just
  because the parts you first saw were.
- **Cover-crop scale direction depends on source aspect and can fail
  outright.** `scale=-2:{BOX_H}` (scale-by-height) only works when the
  source is wider than the box's aspect ratio; a source cropped to something
  taller/narrower than the box causes `crop=...` to error with "Invalid too
  big size" because the scaled width comes out smaller than `BOX_W`. Prefer
  `scale={BOX_W}:{BOX_H}:force_original_aspect_ratio=increase` — this always
  scales up to cover the box regardless of the source's aspect ratio, so it's
  a safe default across differently-shaped sources. If a source is a
  full-bleed pure 9:16 portrait video (no title/caption bars to crop out —
  some individual creators shoot this way, no fixed template), scale by width
  instead (`scale={BOX_W}:-2`) since scaling by height would leave the
  result narrower than the box.
- **Some source videos have no fixed title-bar/content/caption-bar template
  at all** — a plain full-bleed vertical recording with dynamically-placed
  captions burned in wherever. Brightness-scan band-detection doesn't apply
  here; conservatively crop to the top half or so of the frame instead and
  visually confirm no caption text survives.
- **A niche/policy-heavy topic may simply not have 15 usable alternate-source
  images available** (little meme/vlog coverage of e.g. bond-savings-account
  policy or adult-adoption law). When that happens, report the honest count
  and why, rather than padding with loosely-related images to hit the
  number — a thin match looks worse than an honest shortfall.
- **Don't estimate a frame number from its position in a small contact-sheet
  grid** — row/column math against a 10-30px thumbnail is unreliable and
  repeatedly picked the wrong frame across multiple videos in this batch.
  Always open the actual candidate frame file (Read tool, full size) before
  cropping/assigning it.
- When delegating a full video build to another agent, the brief must
  explicitly restate every non-negotiable house-style rule (shake effect on
  the key point, max zoom cap, ad-lib placement, etc.) — don't assume the
  agent will independently rediscover a rule that only lives in this
  document's prose. Missing this caused the shake effect and mid-timeline
  ad-lib spacing to be dropped from an entire batch.

## Script writing rules (뇌전구 house style)

- Narration is one continuous, run-on script connected with natural Korean
  connective endings (-는데/-니까/-길래), **not** a string of discrete complete
  sentences. Real channel videos run 19-28s; keep the script tight enough to
  land in that range at 1.15x tempo.
- The script must end with a short personal-opinion closing line (like the
  RED-colored `s11` segment here: "근데 솔직히 이 정도면 사이다긴 함").
- State specific facts (what someone specifically said/did), not vague
  category summaries.
- Quotes/quotation marks ARE allowed in titles for this template (unlike the
  stricter 뇌전구 MCP-preset script-style rules).

## Confirmed visual spec

**Canvas**: 1080x1920, black background.

**Title (top)**: 2 lines, always on screen for the full video (not just the
intro).
- Line 1 (white): fontsize 115, `ScaleX=63%` (horizontal compression — needed
  because 150pt would overflow 1080px width for a 16-character line, but a
  smaller size looks weaker than the reference), `pos(540,110)`.
- Line 2 (yellow, shorter phrase so it has width budget): fontsize 160,
  `ScaleX=75%`, `pos(540,198)`.
- **Must use explicit `\pos()`, not MarginV** — libass's automatic collision
  avoidance silently overrides MarginV-based spacing between two
  same-timerange dialogue lines. `\pos()` bypasses collision detection
  entirely. This bit us on both the title and the captions.

**Rounded video box**: x=38..1042 (1004px wide), y=369..1512 (1143px tall),
corner radius 80px, aspect ratio ~0.878 (same family of ratio as the 군림보
preset's 0.88 card — likely a general preference). No player-chrome icons
(play/mute/CC/more/expand) overlaid — explicitly removed from the reference.
**The box must always be completely filled — no black/empty padding inside
it, ever, for any image type** (confirmed 2026-09-14). Every image is
cover-cropped to the box's exact aspect ratio; letterboxing (contain+pad) is
never used here even for memes/cartoons, since a partially-empty box breaks
the template's core look.

**Captions (inside the box, right-aligned, 3-line rolling stack)**:
- "Right-aligned" here means the whole caption block sits at the box's right
  edge, not that text is right-justified within a fixed block.
- Each spoken segment splits into **at most 3 lines**, word count divided as
  evenly as possible (`round`-then-distribute-remainder — never a fixed chunk
  size, which left orphan 1-word trailing lines).
- Each of the 3 line-slots has a **fixed position that never moves** as later
  lines appear — implemented as 3 separate ASS Dialogue events per segment,
  each with its own `{\an6\pos(x,y)}`, not one growing multi-line block (a
  growing `\N`-joined block re-centers and shifts line 1 upward every time a
  new line is appended — rejected in review).
- **Per-line auto-fit font size**: measure each line's pixel width via PIL at
  a reference size, scale to hit a 900px target width, clamp to [65, 150].
  Confirmed base size ~85pt "feels right" for a typical line.
- Because per-line sizes vary, line spacing must be **dynamic**, not a fixed
  slot gap: compute each line's height from its own font size (`fs * 0.95`),
  stack cumulatively, and center the whole 3-line block on `y=940` (relative
  to the box).
- **Exactly one glowing line per segment**, on its single most important
  keyword (number / emotion word / twist word) — not one glow per line.
  Glow = `{\3c<color>&\bord14\blur9\u1\i1}keyword{\r}` (colored halo via thick
  blurred border, plus underline, plus synthetic italic tilt). Base text is
  white with a black outline. Glow color is derived from the segment's base
  color: WHITE/RED segments -> red glow, YELLOW -> gold, PINK -> pink.

**Images / motion**:
- Real screenshots per segment (see `IMG_DIR`), Ken-Burns zoom in/out
  alternating by segment index, via ffmpeg `zoompan`.
- **Max zoom is capped at 1.05, not higher.** An earlier version capped at
  1.13. Motion should read as "not a static photo," not as a constant
  aggressive push-in.
- **This zoompan cap is a DIFFERENT problem from the static crop being too
  tight, and fixing one does not fix the other.** The first correction of
  "이미지들을 너무 확대해서 어떤 이미지인지 모르겠어" (lowering the zoompan max above) turned
  out to be the wrong diagnosis — the user's actual complaint, confirmed on a
  second round ("나이키 운동화 로고만 나올정도로 가깝고 그래프도 기둥 3개 보이고 달러도 윗쪽만
  보여"), was that the SOURCE IMAGE FILES themselves (`img/NN.png`, before any
  zoompan is ever applied) were cropped so tight during image selection that
  the subject isn't identifiable — a shoe crop showing only a texture/logo
  fragment, a chart crop showing 3 bars with no title or axis, a bill crop
  showing one blurry corner. **When choosing/cropping a candidate image, ask
  "would a viewer recognize what this is at a glance" before it ever reaches
  `05_render.py`** — a chart needs its title AND enough of the axis to read
  as a chart; an object (shoe, bill, box) needs enough of its silhouette
  intact to read as that object, not just a close-up texture patch. Some
  source b-roll is itself an artsy extreme close-up with no wider shot
  available anywhere in that clip (confirmed by checking every nearby frame)
  — in that case, don't fight it with a slightly-less-tight crop of the same
  unusable shot; swap in a different, clearer candidate image entirely, even
  if it means reusing another segment's image (a repeat beats an
  unrecognizable one).
- **Critical zoompan bug**: feeding a `-loop 1 -t dur` looped image directly
  into `zoompan` restarts the zoom cycle once per received input frame — a
  ~27s video became 1481s. Fix: always insert `trim=end_frame=1` immediately
  before `zoompan` so exactly one frame reaches it.
- **The story's key/twist point MUST use the trembling shake, not smooth
  zoom — this is required, not optional.** Fixed zoom (1.05) with `x`/`y`
  driven by a sum of two sine/cosine terms at different frequencies (see
  `SHAKE_SEGMENTS` in `05_render.py`). A batch of 4 videos built without
  anyone applying this drew direct correction: "핵심 포인트가 나올때는 이미지 덜덜덜
  흔들라고 했잖아." When delegating video-building to another agent, this
  requirement must be spelled out explicitly in the brief — don't assume it'll
  be inferred from the repo alone.
- Reaction memes/cartoons are **cover-cropped just like everything else** —
  never letterboxed/padded (see "Confirmed visual spec" above for why).
- Each segment's display duration must span to the **next segment's start
  time**, not just its own speech length — otherwise the video track ends
  ~2s short of the audio track (the inter-segment silence gap has to belong to
  the video too).
- Rounded corners are done via a PIL-generated grayscale mask
  (`03_make_box_mask.py`) + ffmpeg `alphamerge`, not a border/clip trick.

## ElevenLabs voice pipeline

- Model **`eleven_v3`**, not `eleven_multilingual_v2` — v3 supports inline
  audio tags like `[chuckles]`/`[laughs]` that produce real laughing sounds in
  the output (this is how the "playful/laughing" delivery is achieved; a
  Typecast `emotion_preset="happy"` at any intensity produced no audible
  effect and was abandoned for that reason).
- The **entire script is sent as one API call** (not per-segment + manual
  concatenation) to `POST /v1/text-to-speech/{voice_id}/with-timestamps`. The
  response gives **character-level** alignment
  (`characters`/`character_start_times_seconds`/`character_end_times_seconds`),
  not word-level — `02_build_timeline.py` locates each segment's known text
  via sequential `full_text.index(text, cursor)` and reconstructs words by
  splitting on spaces.
- `voice_settings.speed` is **silently ignored by `eleven_v3`** (confirmed:
  passing out-of-range values causes no error and no duration change either).
  `eleven_multilingual_v2` does respect `speed` (range 0.7-1.2) but has no
  audio-tag support, so it's not usable here. Speed is instead applied as a
  **post-process ffmpeg `atempo=1.15`** step on the raw synthesized audio, and
  every alignment timestamp is divided by the same 1.15 factor before
  building the timeline.
- Voice-gender/identity judgment from raw pitch (F0) analysis alone is
  unreliable — an energetic male narrator's F0 median can land in a range
  (~165-185Hz) that looks female-typical by the numbers. Don't trust automatic
  pitch stats over an actual listen.

## Other ffmpeg/ASS pitfalls

- ASS font name in the `.ass` file must be the **TTF's internal name-table
  value**, not the filename — for `S-CoreDream-7ExtraBold.ttf` that's
  `S-Core Dream 7 ExtraBold` (spaces, no hyphens). Check with
  `fontTools.ttLib.TTFont(path)['name']` (nameID 1/4) if using a different font.
- Windows absolute paths (`C:/...`) inside an ffmpeg `-filter_complex` string
  need their colon escaped as `\:` — both the `subtitles=` file path and
  `fontsdir=` need this, or ffmpeg errors with "No option name near ...".
- `BorderStyle=3` (opaque box) with `Outline=0` renders as a fully invisible
  zero-size box (a general ASS gotcha, not currently used by this template
  since it dropped the white-box card intro treatment).

## Related memory (for the assistant working on this repo)

`project_hainma_template_spec.md` and `project_noejeongu_manual_pipeline.md`
in this user's Claude Code memory carry the same information as this README —
this README is the portable/repo-local copy so a fresh session with just this
link has everything it needs without depending on memory lookups.
