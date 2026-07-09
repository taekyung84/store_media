#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MD → 영상 데이터 빌더 (단일 작성 원본 방식)
==========================================
`점포_영상콘텐츠.md` 한 파일을 읽어 Remotion 영상 에셋을 만듭니다.
 - public/audio/<vid>.mp3       영상별 통합 내레이션
 - public/characters/char_<점포>.png  누끼 캐릭터 (자동 복사)
 - src/data.ts                  영상 목록(VIDEOS) + 자막 타이밍

MD 형식: `## 제목` 한 개 = 영상 1편.
  - 점포: 001        (필수, 캐릭터 의상)
  - 유형: 소개/이벤트/교육/안내
  - 느루: appear/hat/roll
  - (그 외 키:값)    → 아웃트로 정보 (운영시간/오시는길/기간/장소/대상/문의 …)
  ### 내용
  문장1
  문장2 ...          (한 줄 = 자막 1줄 = 음성 1문장)

사용: python3 build_from_md.py            (전체)
      python3 build_from_md.py --md 다른파일.md
음성은 데모용 macOS `say`(Yuna). 실제 운영은 Clova로 교체 가능.
"""
import os, re, sys, json, wave, shutil, subprocess, argparse
import imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PROJ = os.path.join(ROOT, "my-video")
PUB = os.path.join(PROJ, "public")
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
VOICE, RATE = "Yuna", 175
INTRO, OUTRO, GAP = 2.6, 2.6, 0.45
FPS = 30
CONTROL = {"점포", "유형", "느루", "영상id", "영상ID"}

def wav_dur(p):
    with wave.open(p, "rb") as w:
        return w.getnframes() / float(w.getframerate())

def run(a):
    subprocess.run(a, check=True, capture_output=True)

def parse_md(path):
    """## 섹션들을 영상 dict 리스트로 파싱."""
    text = open(path, encoding="utf-8").read()
    videos = []
    # '작성 규칙' 등 안내용 섹션은 ### 내용 이 없으므로 자동 제외됨
    blocks = re.split(r"^##\s+", text, flags=re.M)[1:]
    for b in blocks:
        lines = b.splitlines()
        title = lines[0].strip()
        if title.startswith("비활성") or title.startswith("작성 규칙"):
            continue
        meta, sents, in_content = {}, [], False
        for ln in lines[1:]:
            s = ln.strip()
            if s.startswith("### "):
                in_content = "내용" in s
                continue
            if in_content:
                if s and not s.startswith("#") and not re.fullmatch(r"[-=*_]{3,}", s):
                    sents.append(s)
            else:
                m = re.match(r"-\s*([^:：]+)\s*[:：]\s*(.+)", s)
                if m:
                    meta[m.group(1).strip()] = m.group(2).strip()
        if not sents:
            continue  # 내용 없는 섹션(안내/규칙)은 건너뜀
        videos.append({"title": title, "meta": meta, "sents": sents})
    return videos

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", default=os.path.join(HERE, "점포_영상콘텐츠.md"))
    args = ap.parse_args()

    stores = {s["id"]: s for s in json.load(open(os.path.join(HERE, "stores.json"), encoding="utf-8"))}
    videos = parse_md(args.md)
    print(f"파싱된 영상: {len(videos)}편\n")

    os.makedirs(os.path.join(PUB, "characters"), exist_ok=True)
    os.makedirs(os.path.join(PUB, "audio"), exist_ok=True)
    work = os.path.join(HERE, ".mdtmp")
    if os.path.exists(work): shutil.rmtree(work)
    os.makedirs(work)

    data, seen = [], set()
    for idx, v in enumerate(videos, 1):
        meta, sents = v["meta"], v["sents"]
        sid = meta.get("점포", "").zfill(3) if meta.get("점포") else None
        if not sid or sid not in stores:
            print(f"  ! 건너뜀(점포 없음/오류): {v['title']}")
            continue
        store = stores[sid]
        vid = meta.get("영상ID") or meta.get("영상id") or f"v{idx:03d}"
        vid = re.sub(r"[^A-Za-z0-9_-]", "", vid) or f"v{idx:03d}"
        while vid in seen:
            vid = vid + "x"
        seen.add(vid)

        # 캐릭터: public/characters/ 가 원본. 없을 때만 시드 복사(교체본 보존)
        src_png = os.path.join(HERE, "stickers_cutout", f"{sid}_{store['name']}.png")
        dst_png = os.path.join(PUB, "characters", f"char_{sid}.png")
        if not os.path.exists(dst_png):
            shutil.copy(src_png, dst_png)

        # 문장별 음성 → wav → 길이
        durs, wavs = [], []
        for i, s in enumerate(sents):
            aiff = os.path.join(work, f"{vid}_{i}.aiff"); wv = os.path.join(work, f"{vid}_{i}.wav")
            run(["say", "-v", VOICE, "-r", str(RATE), "-o", aiff, s])
            run([FFMPEG, "-y", "-i", aiff, "-ar", "44100", "-ac", "1", wv])
            durs.append(wav_dur(wv)); wavs.append(wv)

        sil_i = os.path.join(work, f"{vid}_si.wav"); sil_o = os.path.join(work, f"{vid}_so.wav"); silg = os.path.join(work, f"{vid}_g.wav")
        for path, d in [(sil_i, INTRO), (sil_o, OUTRO), (silg, GAP)]:
            run([FFMPEG, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", f"{d}", path])
        seq = [sil_i]
        for wv in wavs: seq += [wv, silg]
        seq.append(sil_o)
        listf = os.path.join(work, f"{vid}_l.txt")
        open(listf, "w").write("\n".join(f"file '{p}'" for p in seq))
        mp3 = os.path.join(PUB, "audio", f"{vid}.mp3")
        run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", listf, "-ar", "44100", "-ac", "2", "-b:a", "160k", mp3])

        seg = [d + GAP for d in durs]
        caps = [{"text": s, "fromMs": round((INTRO + sum(seg[:i])) * 1000),
                 "toMs": round((INTRO + sum(seg[:i + 1])) * 1000)} for i, s in enumerate(sents)]
        total = INTRO + sum(seg) + OUTRO

        # 아웃트로 정보(제어 키 제외)
        info = [{"label": k, "value": val} for k, val in meta.items() if k not in CONTROL]

        data.append({
            "id": vid, "title": v["title"], "type": meta.get("유형", "안내"),
            "storeId": sid, "storeName": store["name"],
            "neuru": meta.get("느루", store.get("neuru_action", "appear")),
            "char": f"characters/char_{sid}.png", "audio": f"audio/{vid}.mp3",
            "info": info, "introSec": INTRO, "outroSec": OUTRO,
            "totalSec": round(total, 3), "captions": caps,
        })
        print(f"  ✓ [{data[-1]['type']}] {data[-1]['title']}  ({len(sents)}문장 · {round(total,1)}초)  id={vid}")

    ts = "// 자동 생성됨 (build_from_md.py). 직접 수정하지 마세요. 원본: 점포_영상콘텐츠.md\n"
    ts += "export type Caption = { text: string; fromMs: number; toMs: number };\n"
    ts += "export type Info = { label: string; value: string };\n"
    ts += ("export type Video = {\n  id: string; title: string; type: string; storeId: string; storeName: string;\n"
           "  neuru: string; char: string; audio: string; info: Info[];\n"
           "  introSec: number; outroSec: number; totalSec: number; captions: Caption[];\n};\n\n")
    ts += f"export const FPS = {FPS};\n"
    ts += "export const VIDEOS: Video[] = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n"
    open(os.path.join(PROJ, "src", "data.ts"), "w", encoding="utf-8").write(ts)
    shutil.rmtree(work)
    print(f"\n완료: {len(data)}편 → my-video/public + src/data.ts")
    print("다음: cd ../my-video && npm run render-all")

if __name__ == "__main__":
    main()
