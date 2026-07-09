#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
찬찬이 점포 스티커 — 캐릭터 누끼(배경 제거) 스크립트
==================================================
stickers/ 의 28개 PNG에서 배경(흰 카드)과 라벨 텍스트를 제거하고
캐릭터 + 부착 소품만 투명 PNG로 stickers_cutout/ 에 저장합니다.

설치:  python3 -m pip install rembg onnxruntime pillow
사용:  python3 cutout.py
       python3 cutout.py --src stickers --out stickers_cutout
첫 실행 시 u2net 모델(~176MB)을 자동 다운로드합니다.
"""
import argparse
import glob
import os
from rembg import remove, new_session
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser(description="찬찬이 스티커 누끼")
    ap.add_argument("--src", default=os.path.join(HERE, "stickers"))
    ap.add_argument("--out", default=os.path.join(HERE, "stickers_cutout"))
    ap.add_argument("--no-trim", action="store_true", help="투명 여백 자동 트림 끄기")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    sess = new_session("u2net")
    files = sorted(glob.glob(os.path.join(args.src, "*.png")))
    for path in files:
        name = os.path.basename(path)
        img = Image.open(path)
        out = remove(
            img, session=sess, alpha_matting=True,
            alpha_matting_foreground_threshold=240,
            alpha_matting_background_threshold=15,
        )
        if not args.no_trim:
            bbox = out.getbbox()
            if bbox:
                out = out.crop(bbox)
        out.save(os.path.join(args.out, name))
        print(f"  ✓ {name}")
    print(f"\n누끼 완료: {len(files)}개 → {args.out}")


if __name__ == "__main__":
    main()
