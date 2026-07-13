# -*- coding: utf-8 -*-
"""
캐릭터 이미지 비율 정규화
모든 캐릭터(메인 + 28점포)를 동일한 정사각 캔버스에 같은 키·바닥선·중앙정렬로 맞춤.
원본: public/characters/  (사용자가 교체한 char_main / char_009 포함)
출력: public/characters/  와  stickers_cutout/  양쪽에 저장(투명 PNG).
"""
import os, json
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PUBC = os.path.join(ROOT, "my-video", "public", "characters")
CUT = os.path.join(HERE, "stickers_cutout")
stores = json.load(open(os.path.join(HERE, "stores.json"), encoding="utf-8"))

S = 900                 # 정사각 캔버스 한 변
TARGET_H = int(S * 0.84)  # 캐릭터(소품 포함) 목표 높이
MAX_W = int(S * 0.94)     # 최대 폭(넘으면 축소)
BASE_Y = int(S * 0.95)    # 바닥선(발 위치)


def normalize(src, dst_list):
    im = Image.open(src).convert("RGBA")
    bbox = im.getchannel("A").getbbox()
    if not bbox:
        print(f"  ! 빈 이미지: {src}")
        return
    im = im.crop(bbox)
    w, h = im.size
    scale = min(TARGET_H / h, MAX_W / w)
    nw, nh = max(1, round(w * scale)), max(1, round(h * scale))
    im = im.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    x = (S - nw) // 2
    y = BASE_Y - nh
    canvas.paste(im, (x, y), im)
    for d in dst_list:
        os.makedirs(os.path.dirname(d), exist_ok=True)
        canvas.save(d, "PNG", optimize=True)


# 메인 찬찬이
normalize(os.path.join(PUBC, "char_main.png"),
          [os.path.join(PUBC, "char_main.png"), os.path.join(CUT, "main_찬찬이.png")])
print("  ✓ main")

# 28 점포
for s in stores:
    sid, name = s["id"], s["name"]
    src = os.path.join(PUBC, f"char_{sid}.png")
    normalize(src, [os.path.join(PUBC, f"char_{sid}.png"),
                    os.path.join(CUT, f"{sid}_{name}.png")])
    print(f"  ✓ {sid} {name}")

print(f"\n완료: 메인+28점포 → {S}x{S} 정사각, 캐릭터 높이 {TARGET_H}px 통일")
print("  저장: public/characters/  +  stickers_cutout/")
