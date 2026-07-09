#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remotion 운영본 에셋 준비 스크립트
=================================
점포 데이터/대본/누끼 PNG로 Remotion 프로젝트(my-video)에 필요한 에셋을 만듭니다.
 - public/characters/char_<id>.png   누끼 캐릭터 복사
 - public/audio/<id>.mp3              점포별 통합 내레이션(인트로 무음+문장+아웃트로 무음)
 - src/data.ts                        점포 메타데이터 + 자막 타이밍(ms)

음성은 데모용으로 macOS `say`(Yuna) 사용. 실제 운영은 Clova mp3로 교체하면 됩니다.
사용: python3 prepare_remotion.py            (전체)
      python3 prepare_remotion.py 001 013     (특정 점포만)
"""
import os, sys, json, wave, shutil, subprocess
import imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PROJ = os.path.join(ROOT, "my-video")
PUB = os.path.join(PROJ, "public")
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
VOICE, RATE = "Yuna", 175
INTRO, OUTRO, GAP = 2.6, 2.4, 0.45
FPS = 30

def wav_dur(p):
    with wave.open(p, "rb") as w:
        return w.getnframes() / float(w.getframerate())

def run(args):
    subprocess.run(args, check=True, capture_output=True)

def main():
    stores = json.load(open(os.path.join(HERE, "stores.json"), encoding="utf-8"))
    scripts = {k: v for k, v in json.load(open(os.path.join(HERE, "scripts.json"), encoding="utf-8")).items() if not k.startswith("_")}
    only = set(sys.argv[1:])
    if only:
        stores = [s for s in stores if s["id"] in only]

    os.makedirs(os.path.join(PUB, "characters"), exist_ok=True)
    os.makedirs(os.path.join(PUB, "audio"), exist_ok=True)
    work = os.path.join(HERE, ".rtmp")
    if os.path.exists(work): shutil.rmtree(work)
    os.makedirs(work)

    data = []
    for store in stores:
        sid, name = store["id"], store["name"]
        sents = scripts[sid]
        # 캐릭터: public/characters/ 가 원본. 없을 때만 시드 복사(교체본 보존)
        src_png = os.path.join(HERE, "stickers_cutout", f"{sid}_{name}.png")
        dst_png = os.path.join(PUB, "characters", f"char_{sid}.png")
        if not os.path.exists(dst_png):
            shutil.copy(src_png, dst_png)

        # 문장별 음성 생성 → wav 변환 → 길이 측정
        durs, wavs = [], []
        for i, s in enumerate(sents):
            aiff = os.path.join(work, f"{sid}_{i}.aiff")
            wv = os.path.join(work, f"{sid}_{i}.wav")
            run(["say", "-v", VOICE, "-r", str(RATE), "-o", aiff, s])
            run([FFMPEG, "-y", "-i", aiff, "-ar", "44100", "-ac", "1", wv])
            durs.append(wav_dur(wv)); wavs.append(wv)

        # 무음 클립
        sil_i = os.path.join(work, f"{sid}_si.wav"); sil_o = os.path.join(work, f"{sid}_so.wav"); silg = os.path.join(work, f"{sid}_g.wav")
        for path, d in [(sil_i, INTRO), (sil_o, OUTRO), (silg, GAP)]:
            run([FFMPEG, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", f"{d}", path])

        # 통합 오디오 → mp3
        seq = [sil_i]
        for wv in wavs: seq += [wv, silg]
        seq.append(sil_o)
        listf = os.path.join(work, f"{sid}_list.txt")
        open(listf, "w").write("\n".join(f"file '{p}'" for p in seq))
        mp3 = os.path.join(PUB, "audio", f"{sid}.mp3")
        run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", listf, "-ar", "44100", "-ac", "2", "-b:a", "160k", mp3])

        # 자막 타이밍(ms): 본문 구간만
        seg = [d + GAP for d in durs]
        caps = []
        for i, s in enumerate(sents):
            start = INTRO + sum(seg[:i])
            end = INTRO + sum(seg[:i + 1])
            caps.append({"text": s, "fromMs": round(start * 1000), "toMs": round(end * 1000)})
        total = INTRO + sum(seg) + OUTRO

        data.append({
            "id": sid, "name": name, "concept": store["concept"],
            "hours": store.get("hours", ""), "directions": store.get("directions", ""),
            "neuru": store.get("neuru_action", "appear"),
            "char": f"characters/char_{sid}.png", "audio": f"audio/{sid}.mp3",
            "introSec": INTRO, "outroSec": OUTRO, "totalSec": round(total, 3),
            "captions": caps,
        })
        print(f"  ✓ {sid} {name}  ({len(sents)}문장 · {round(total,1)}초)")

    # data.ts 작성
    ts = "// 자동 생성됨 (prepare_remotion.py). 직접 수정하지 마세요.\n"
    ts += "export type Caption = { text: string; fromMs: number; toMs: number };\n"
    ts += "export type Store = {\n  id: string; name: string; concept: string; hours: string;\n  directions: string; neuru: string; char: string; audio: string;\n  introSec: number; outroSec: number; totalSec: number; captions: Caption[];\n};\n\n"
    ts += "export const FPS = " + str(FPS) + ";\n"
    ts += "export const STORES: Store[] = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n"
    open(os.path.join(PROJ, "src", "data.ts"), "w", encoding="utf-8").write(ts)
    shutil.rmtree(work)
    print(f"\n완료: {len(data)}개 점포 → my-video/public + src/data.ts")

if __name__ == "__main__":
    main()
