#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
예시 영상 생성 (프로토타입)
==========================
누끼 캐릭터 PNG + 작성된 대본으로 점포 안내 영상 1편을 실제로 만듭니다.
 - 음성: macOS 내장 TTS `say` (한국어 Yuna)  ※ 실제 운영은 Clova 권장
 - 영상: PIL로 프레임 렌더(배경+캐릭터 플로팅+자막+인트로/아웃트로) → ffmpeg 인코딩
사용: python3 make_example.py 001
"""
import sys, os, json, math, subprocess, wave, glob, shutil
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__))
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 720, 1280, 24
GREEN = (190, 211, 108); ORANGE = (241, 120, 41); BEIGE = (246, 223, 186); DARK = (70, 78, 40)
VOICE = "Yuna"; RATE = 175
INTRO, OUTRO, GAP = 2.6, 2.4, 0.45
FONT = "/System/Library/Fonts/AppleSDGothicNeo.ttc"

def font(sz, idx=0):
    try: return ImageFont.truetype(FONT, sz, index=idx)
    except Exception: return ImageFont.load_default()

def wav_dur(p):
    with wave.open(p, "rb") as w:
        return w.getnframes() / float(w.getframerate())

def wrap(draw, text, fnt, maxw):
    words, lines, cur = list(text), [], ""
    for ch in words:
        if draw.textlength(cur + ch, font=fnt) <= maxw: cur += ch
        else: lines.append(cur); cur = ch
    if cur: lines.append(cur)
    return lines

def vgrad(top, bot):
    img = Image.new("RGB", (W, H), top)
    d = ImageDraw.Draw(img)
    for y in range(H):
        f = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(top[i] + (bot[i]-top[i])*f) for i in range(3)))
    return img

def rounded_caption(base, text, fnt):
    d = ImageDraw.Draw(base)
    lines = wrap(d, text, fnt, W - 140)
    lh = fnt.size + 16
    block_h = lh * len(lines)
    y0 = H - 250 - block_h
    pad = 30
    box = [50, y0 - pad, W - 50, y0 + block_h + pad - 10]
    panel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    pd.rounded_rectangle(box, radius=28, fill=(255, 255, 255, 235))
    base.alpha_composite(panel)
    d = ImageDraw.Draw(base)
    for i, ln in enumerate(lines):
        tw = d.textlength(ln, font=fnt)
        d.text(((W - tw)//2, y0 + i*lh), ln, fill=DARK, font=fnt)

def main():
    sid = sys.argv[1] if len(sys.argv) > 1 else "001"
    stores = {s["id"]: s for s in json.load(open(os.path.join(HERE, "stores.json"), encoding="utf-8"))}
    store = stores[sid]
    name = store["name"]
    folder = os.path.join(HERE, "build", f"{sid}_{name}")
    sentences = [l.strip() for l in open(os.path.join(folder, "script.txt"), encoding="utf-8") if l.strip()]
    char_png = os.path.join(HERE, "stickers_cutout", f"{sid}_{name}.png")

    work = os.path.join(HERE, ".render_tmp");
    if os.path.exists(work): shutil.rmtree(work)
    os.makedirs(work)

    # --- 1) 문장별 음성 생성(aiff) → wav 변환 + 길이 측정 ---
    durs = []
    for i, s in enumerate(sentences):
        aiff = os.path.join(work, f"s{i}.aiff")
        wavp = os.path.join(work, f"s{i}.wav")
        subprocess.run(["say", "-v", VOICE, "-r", str(RATE), "-o", aiff, s], check=True)
        subprocess.run([FFMPEG, "-y", "-i", aiff, "-ar", "44100", "-ac", "1", wavp],
                       check=True, capture_output=True)
        durs.append(wav_dur(wavp))
    seg = [d + GAP for d in durs]

    # --- 2) 통합 오디오(wav): 인트로 무음 + 문장들 + 아웃트로 무음 ---
    sil_i = os.path.join(work, "sil_intro.wav"); sil_o = os.path.join(work, "sil_outro.wav"); silg = os.path.join(work, "gap.wav")
    for path, dur in [(sil_i, INTRO), (sil_o, OUTRO), (silg, GAP)]:
        subprocess.run([FFMPEG, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                        "-t", f"{dur}", path], check=True, capture_output=True)
    wavs = [sil_i]
    for i in range(len(sentences)):
        wavs.append(os.path.join(work, f"s{i}.wav")); wavs.append(silg)
    wavs.append(sil_o)
    concat_txt = os.path.join(work, "audio.txt")
    open(concat_txt, "w").write("\n".join(f"file '{p}'" for p in wavs))
    full_audio = os.path.join(work, "audio.wav")
    subprocess.run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", full_audio],
                   check=True, capture_output=True)

    # --- 3) 프레임 렌더 ---
    body = sum(seg); total = INTRO + body + OUTRO
    nframes = int(total * FPS)
    char = Image.open(char_png).convert("RGBA")
    cscale = (H * 0.42) / char.height
    char = char.resize((int(char.width*cscale), int(char.height*cscale)), Image.LANCZOS)
    f_title = font(96); f_slogan = font(38); f_cap = font(46); f_brand = font(30)
    f_store = font(80); f_info = font(34); f_bye = font(40)

    starts = [INTRO + sum(seg[:i]) for i in range(len(seg))]
    for f in range(nframes):
        t = f / FPS
        base = vgrad((205, 224, 130), (170, 196, 95)).convert("RGBA")
        d = ImageDraw.Draw(base)
        if t < INTRO:                         # 인트로
            d.text((W/2, 360), "교보문고 점포안내", anchor="mm", fill=(95, 110, 50), font=f_brand)
            d.text((W/2, 470), "찬찬이", anchor="mm", fill=(255, 255, 255), font=f_title)
            d.text((W/2, 600), "“조금 느려도 괜찮아요”", anchor="mm", fill=DARK, font=f_slogan)
            ch = char.copy()
            base.alpha_composite(ch, (int(W/2-ch.width/2), int(720 + 14*math.sin(t*3))))
        elif t < INTRO + body:                # 본문
            idx = max(i for i, s0 in enumerate(starts) if t >= s0)
            bob = 16 * math.sin(t * 2.2)
            ch = char.copy()
            base.alpha_composite(ch, (int(W/2 - ch.width/2), int(330 + bob)))
            d.text((W/2, 110), f"교보문고 {name}", anchor="mm", fill=(255,255,255), font=f_brand)
            rounded_caption(base, sentences[idx], f_cap)
        else:                                 # 아웃트로
            d.text((W/2, 360), name, anchor="mm", fill=(255,255,255), font=f_store)
            d.text((W/2, 470), f"운영시간  {store.get('hours','')}", anchor="mm", fill=DARK, font=f_info)
            dirs = store.get("directions","")
            for j, ln in enumerate(wrap(d, dirs, f_info, W-160)):
                d.text((W/2, 540 + j*46), ln, anchor="mm", fill=DARK, font=f_info)
            ch = char.copy()
            base.alpha_composite(ch, (int(W/2-ch.width/2), int(700 + 12*math.sin(t*3))))
            d.text((W/2, 700), "느루와 함께, 또 만나요!", anchor="mm", fill=(95,110,50), font=f_bye)
        base.convert("RGB").save(os.path.join(work, f"f{f:05d}.png"))

    # --- 4) 인코딩 ---
    out = os.path.join(HERE, f"예시영상_{name}.mp4")
    subprocess.run([FFMPEG, "-y", "-framerate", str(FPS), "-i", os.path.join(work, "f%05d.png"),
                    "-i", full_audio, "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-shortest", out], check=True, capture_output=True)
    shutil.rmtree(work)
    print(f"\n✅ 예시 영상 생성 완료: {out}")
    print(f"   해상도 {W}x{H} · {FPS}fps · 약 {total:.1f}초 · 음성 {VOICE}")

if __name__ == "__main__":
    main()
