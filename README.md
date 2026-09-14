# politics-preset — 정치·시사 뉴스용 둥근 뇌전구 숏폼

`nm2240/rounded-noejeongu-preset`(둥근 비디오박스 "한입만" 템플릿)을 정치·여론조사 뉴스에 적용한 개인 저장소.
파이프라인·규격은 원본 그대로이고(전문은 `docs_upstream_README.md`), 여기엔 **실제로 만든 영상의 대본·이미지·타임라인**을 스토리별로 남긴다.

## 구성

```
scripts/      01~05 파이프라인 (CUSTOMIZE 구간이 마지막 스토리 값으로 채워져 있음)
assets/       S-Core Dream 7 ExtraBold 폰트, 둥근 박스 마스크(1004x1143, r=80)
stories/<id>/ 스토리별 산출물: img/ (박스 비율 0.878로 미리 크롭한 컷), captions.ass, timeline.json,
              alignment.json(ElevenLabs 글자 단위 정렬), README.md(대본·이미지 출처)
work/         git 제외. 렌더 중간 산출물(mp3/wav/mp4)
```

## 실행

```
pip install Pillow
# ~/.volcano/keys/elevenlabs 에 sk_ 로 시작하는 ElevenLabs 키 (Text to Speech 권한, 뇌전구 복제 음성 보유 계정)
python scripts/01_tts_and_alignment.py
ffmpeg -y -i work/el_full/full_raw.mp3 -filter:a atempo=1.15 -ar 44100 work/el_full/full_atempo.wav
python scripts/02_build_timeline.py
python scripts/04_build_captions.py
python scripts/05_render.py      # -> work/final.mp4
```

새 스토리는 `scripts/01`(SEGMENTS·TAG_BEFORE), `02`(IMG), `04`(TITLE·KEYWORDS), `05`(IMG_DIR·SHAKE_SEGMENTS)의 CUSTOMIZE 구간만 바꾼다.
완성본은 `내 문서\뇌전구\` 에 복사한다.

## 정치 뉴스에서 이미지 구하는 법 (이 저장소에서 확인된 것)

기사 화면·방송사(KBS/MBC/SBS/YTN/뉴스1 등) 화면은 쓰지 않는다. 대신:

- **여론조사 기관 공식 자료** — 리얼미터 realmeter.net 게시글의 차트 jpg와 주간통계표 PDF (`pdftoppm -r 200 -png`로 페이지 렌더 후 표·차트 부분 크롭). 실제 수치가 박힌 진짜 그래픽이라 가장 잘 먹힌다.
- **KTV 국민방송**(정부 제작, 유튜브 채널 `UCIMOytYIzaUpoAM2bpT4JZQ`) — 대통령·국무회의·청와대 브리핑·현장 영상. 하단 자막 밴드와 좌상단 프로그램 로고를 피해 크롭.
- **당사자·정당 공식 유튜브**(예: 용혜인 채널)와 **NATV 국회방송**(인사청문회) — 정치인 본인 영상과 국회 회의 영상. 자막 밴드·국회방송 로고·수어 통역 박스를 피해 크롭.
- **페페 밈** — 애드립 2곳 + 엔딩. (`~/volcano-work/군림보/fm_10323813802/pepe/fm/`)
- 크롭은 `-ss`로 뽑은 실제 프레임을 보고 좌표를 잡는다. 컨택트시트(fps 샘플)와 `-ss` 프레임은 다른 프레임일 수 있어 자막이 끼어드는 일이 잦다 → 잘라낸 결과를 반드시 다시 본다.

## 규격 메모 (원본 README 요약)

- 1080×1920, 검정 배경, 둥근 박스 x=38..1042 / y=369..1512, 항상 꽉 채움(레터박스 금지)
- 제목 2줄 상단 고정(`\pos`), 박스 안 3줄 롤링 자막, 세그먼트당 글로우 1개
- 세그먼트 4~6단어, 이미지 15장 이상, 애드립 2개 이상(중간 배치), 핵심 포인트 1곳 흔들림(`SHAKE_SEGMENTS`), 줌 최대 1.05
- eleven_v3 + `[chuckles]`/`[laughs]`, 속도는 ffmpeg atempo=1.15로 후처리
- `%P`는 TTS가 불안정해서 "포인트"로 쓴다.
- 길이 목표 19~28초와 "이미지 15장" 규칙은 숫자 많은 대본에서 충돌한다(세그먼트당 ~2.4초). 지금까지는 15장 유지 → 35~37초.

## 스토리 목록

| id | 소재 | 길이 | 완성본 |
|---|---|---|---|
| `naver008_0005413076` | 李대통령 지지율 33.8% 최저, 국힘 42.1% vs 민주 36.1% (리얼미터 2026-09-14) | 36.9s | `내 문서\뇌전구\지지율_33.8_최저_rounded_v001.mp4` |
| `naver032_0003470045` | 용혜인 청문회 전 낙마, 네 번째 낙마·청와대 인사 난맥 (경향 2026-09-13) | 34.7s | `내 문서\뇌전구\용혜인_낙마_rounded_v001.mp4` |
