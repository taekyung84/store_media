#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
찬찬이 점포 안내 영상 — 자동화 오케스트레이션 스크립트
====================================================

stores.json 을 읽어 점포별로 다음을 자동 생성합니다.

  [A] Claude API  → 찬찬이 페르소나 내레이션 대본 (문장 단위)
  [B] Clova Voice → 문장별 mp3 음성 + 길이(추정)
  [C] AI 영상 프롬프트 (Veo/Kling image-to-video) 파일
  → 점포별 "제작 폴더" + shotlist.csv (편집툴 조립용)

특징
  - 표준 라이브러리(urllib)만 사용 → 별도 설치 불필요
  - API 키가 없으면 자동으로 DRY-RUN: 폴더/대본/프롬프트/shotlist 골격을
    모두 생성하되 외부 호출은 건너뜀 (구조 검증 가능)

환경변수
  ANTHROPIC_API_KEY   Claude API 키 (없으면 대본 단계 dry-run)
  CLOVA_ID            Naver Cloud CLOVA Voice API Key ID
  CLOVA_SECRET        Naver Cloud CLOVA Voice API Key
  CLAUDE_MODEL        (선택) 기본 claude-sonnet-4-6
  CLOVA_SPEAKER       (선택) 기본 ndain (아이 톤). 대안: nara, vara

사용법
  python3 generate.py                 # stores.json 전체, 키 있으면 실호출
  python3 generate.py --dry-run       # 강제 dry-run (호출 없이 골격만)
  python3 generate.py --only 001,013  # 특정 점포만
  python3 generate.py --stores other.json --out build
"""

import argparse
import csv
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse

# ---------------------------------------------------------------------------
# 설정
# ---------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))

CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")
CLAUDE_URL = "https://api.anthropic.com/v1/messages"
CLOVA_URL = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"
CLOVA_SPEAKER = os.environ.get("CLOVA_SPEAKER", "ndain")  # 아이 톤
CLOVA_SPEED = os.environ.get("CLOVA_SPEED", "1")          # 살짝 느리게: 1, 더 느리게: 2

# 찬찬이 브랜드 컬러 (자막/그래픽 가이드)
BRAND = {"green": "#BED36C", "orange": "#F17829", "beige": "#F6DFBA", "yellow": "#FEE03C"}

# 느루 동작 연출 사전 → AI 영상 프롬프트에 주입
NEURU_MOTION = {
    "appear": "the acorn friend Neuru pops up from the top of the head and peeks out cutely",
    "hat":    "the acorn friend Neuru stays nestled on the head like a little hat, only its cap showing",
    "roll":   "the acorn friend Neuru rolls around playfully near the character",
}


# ---------------------------------------------------------------------------
# [A] 대본 프롬프트
# ---------------------------------------------------------------------------
def build_script_prompt(store):
    floors = "\n".join(f"  - {f['f']}: {f['desc']}" for f in store.get("floors", []))
    events = "\n".join(f"  - {e}" for e in store.get("events", []))
    return f"""당신은 교보문고 점포 안내 캐릭터 '찬찬이'입니다.

[페르소나]
- 차분하고 따뜻하며 느긋한 아기 거북이. 머리 위엔 도토리 친구 '느루'가 함께 있습니다.
- 말투: 존댓말, 부드럽고 다정하게. 슬로건 정서 "조금 느려도 괜찮아".
- 과장된 감탄사·이모지 사용 금지. 담백하고 포근하게.

[작업]
아래 점포 데이터로 약 60~75초 분량의 안내 내레이션을 작성하세요.
구성 순서: ① 인사+점포 소개 ② 층별 핵심 안내 ③ 진행 이벤트 ④ 찾아오는 길 ⑤ 따뜻한 맺음말.

[출력 형식 — 매우 중요]
- 5~8개의 짧은 문장으로 작성하고, 한 문장을 한 줄로 출력하세요. (한 줄 = 한 자막)
- 각 문장은 12자 이상 40자 이하.
- 다른 설명·머리말·번호 없이 문장들만 줄바꿈으로 출력하세요.

[점포 데이터]
점포명: {store['name']}
콘셉트: {store['concept']}
위치: {store.get('location','')}
층별 안내:
{floors or '  - (정보 없음)'}
운영시간: {store.get('hours','')}
진행 이벤트:
{events or '  - (없음)'}
찾아오는 길: {store.get('directions','')}
"""


def call_claude(prompt, api_key):
    body = json.dumps({
        "model": CLAUDE_MODEL,
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")
    req = urllib.request.Request(CLAUDE_URL, data=body, method="POST")
    req.add_header("x-api-key", api_key)
    req.add_header("anthropic-version", "2023-06-01")
    req.add_header("content-type", "application/json")
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["content"][0]["text"].strip()


def fallback_script(store):
    """dry-run 또는 키 없음일 때 사용하는 자리표시 대본."""
    f0 = store["floors"][0] if store.get("floors") else {"f": "", "desc": "다양한 도서"}
    ev = store["events"][0] if store.get("events") else "특별 기획전"
    return "\n".join([
        f"조금 느려도 괜찮아요, {store['name']}에 오신 걸 환영해요.",
        "저는 점포 친구 찬찬이, 머리 위엔 도토리 느루가 함께해요.",
        f"{f0['f']}에서는 {f0['desc']}를 만나보실 수 있어요.",
        f"지금 저희 점포에서는 {ev}이 열리고 있답니다.",
        f"{store.get('directions','')} 천천히 찾아오세요.",
        "오늘도 당신만의 이야기를 함께 모아가요.",
    ])


# ---------------------------------------------------------------------------
# [B] Clova Voice
# ---------------------------------------------------------------------------
def call_clova(text, out_path, key_id, key_secret):
    params = [
        ("speaker", CLOVA_SPEAKER),
        ("speed", CLOVA_SPEED),
        ("pitch", "0"),
        ("volume", "0"),
        ("format", "mp3"),
        ("text", text),
    ]
    data = urllib.parse.urlencode(params).encode("utf-8")
    req = urllib.request.Request(CLOVA_URL, data=data, method="POST")
    req.add_header("X-NCP-APIGW-API-KEY-ID", key_id)
    req.add_header("X-NCP-APIGW-API-KEY", key_secret)
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, timeout=60) as resp:
        audio = resp.read()
    with open(out_path, "wb") as f:
        f.write(audio)


def estimate_duration(text):
    """한국어 내레이션 길이 추정(초). 편집 시 미세 조정용 가이드값.
    경험치: 글자당 약 0.18초 + 문장 호흡 0.6초."""
    chars = len([c for c in text if not c.isspace()])
    return round(chars * 0.18 + 0.6, 1)


# ---------------------------------------------------------------------------
# [C] AI 영상 프롬프트
# ---------------------------------------------------------------------------
def build_clip_prompt(store, scene_idx):
    neuru = NEURU_MOTION.get(store.get("neuru_action", "appear"), NEURU_MOTION["appear"])
    motion_by_scene = {
        0: "gently waves a hand to greet, slow friendly blink",
        1: "tilts head and points softly as if guiding the way",
        2: "claps little hands lightly, cheerful idle motion",
        3: "looks toward the viewer and nods warmly",
    }
    motion = motion_by_scene.get(scene_idx, "soft idle sway, slow blink")
    return (
        f"A cute felt-textured baby turtle character \"Chanchani\" wearing "
        f"{store['costume_keywords']}. {neuru}. "
        f"Motion: {motion}. "
        f"Soft handmade wool-felt look, warm cozy lighting, clean simple background. "
        f"Keep the character shape identical to the reference image. "
        f"Low motion strength, seamless loop, 4 seconds, square or 9:16."
    )


# ---------------------------------------------------------------------------
# 메인 처리
# ---------------------------------------------------------------------------
def process_store(store, out_root, keys, dry_run, prewritten=None):
    sid, name = store["id"], store["name"]
    folder = os.path.join(out_root, f"{sid}_{name}")
    os.makedirs(folder, exist_ok=True)

    # [A] 대본 — 우선순위: 사전작성(scripts.json) > Claude API > 자리표시
    if prewritten and sid in prewritten:
        script = "\n".join(prewritten[sid])
    elif not dry_run and keys["anthropic"]:
        try:
            script = call_claude(build_script_prompt(store), keys["anthropic"])
        except Exception as e:
            print(f"  ! Claude 호출 실패({name}) → 자리표시 대본 사용: {e}")
            script = fallback_script(store)
    else:
        script = fallback_script(store)

    sentences = [s.strip() for s in script.splitlines() if s.strip()]
    with open(os.path.join(folder, "script.txt"), "w", encoding="utf-8") as f:
        f.write(script + "\n")

    # [B] 음성 + [C] 클립 프롬프트 + shotlist
    clip_prompts = []
    shot_rows = []
    for i, sentence in enumerate(sentences):
        vo_name = f"vo_{i+1:02d}.mp3"
        vo_path = os.path.join(folder, vo_name)
        spoke = False
        if not dry_run and keys["clova_id"] and keys["clova_secret"]:
            try:
                call_clova(sentence, vo_path, keys["clova_id"], keys["clova_secret"])
                spoke = True
            except Exception as e:
                print(f"  ! Clova 호출 실패({name} #{i+1}): {e}")
        dur = estimate_duration(sentence)
        clip_prompt = build_clip_prompt(store, i)
        clip_prompts.append(f"[Scene {i+1}] (첫 프레임: {sid}_{name}.png)\n{clip_prompt}\n")
        shot_rows.append({
            "scene": i + 1,
            "narration": sentence,
            "vo_file": vo_name if spoke else f"(dry-run) {vo_name}",
            "est_sec": dur,
            "caption": sentence,
            "clip_prompt": clip_prompt,
        })

    # clip_prompts.txt
    with open(os.path.join(folder, "clip_prompts.txt"), "w", encoding="utf-8") as f:
        f.write(f"# {name} ({sid}) — AI 영상 생성 프롬프트 (Veo/Kling image-to-video)\n")
        f.write(f"# 첫 프레임으로 반드시 점포 스티커 PNG 사용, motion strength LOW\n\n")
        f.write("\n".join(clip_prompts))

    # shotlist.csv
    with open(os.path.join(folder, "shotlist.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["scene", "narration", "vo_file", "est_sec", "caption", "clip_prompt"])
        w.writeheader()
        w.writerows(shot_rows)

    total = round(sum(r["est_sec"] for r in shot_rows), 1)
    return {"folder": folder, "scenes": len(sentences), "est_total_sec": total}


def main():
    ap = argparse.ArgumentParser(description="찬찬이 점포 안내 영상 자동화")
    ap.add_argument("--stores", default=os.path.join(HERE, "stores.json"))
    ap.add_argument("--out", default=os.path.join(HERE, "build"))
    ap.add_argument("--only", default="", help="쉼표로 구분한 점포 id (예: 001,013)")
    ap.add_argument("--dry-run", action="store_true", help="외부 호출 없이 골격만 생성")
    ap.add_argument("--scripts", default=os.path.join(HERE, "scripts.json"),
                    help="사전 작성 대본 파일(있으면 Claude API보다 우선 사용)")
    args = ap.parse_args()

    prewritten = None
    if args.scripts and os.path.exists(args.scripts):
        with open(args.scripts, encoding="utf-8") as f:
            prewritten = {k: v for k, v in json.load(f).items() if not k.startswith("_")}
        print(f"※ 사전 작성 대본 사용: {args.scripts} ({len(prewritten)}개 점포)\n")

    keys = {
        "anthropic": os.environ.get("ANTHROPIC_API_KEY", ""),
        "clova_id": os.environ.get("CLOVA_ID", ""),
        "clova_secret": os.environ.get("CLOVA_SECRET", ""),
    }
    dry_run = args.dry_run or not (keys["anthropic"] or (keys["clova_id"] and keys["clova_secret"]))
    if dry_run:
        print("※ DRY-RUN 모드: 외부 API 호출 없이 폴더/대본/프롬프트/shotlist 골격만 생성합니다.")
        print("  (실제 생성하려면 ANTHROPIC_API_KEY / CLOVA_ID / CLOVA_SECRET 환경변수를 설정하세요.)\n")

    with open(args.stores, encoding="utf-8") as f:
        stores = json.load(f)
    if args.only:
        wanted = {s.strip() for s in args.only.split(",")}
        stores = [s for s in stores if s["id"] in wanted]

    os.makedirs(args.out, exist_ok=True)
    summary = []
    for store in stores:
        print(f"▶ {store['id']} {store['name']} 처리 중…")
        res = process_store(store, args.out, keys, dry_run, prewritten)
        summary.append((store["id"], store["name"], res))
        print(f"  ✓ {res['scenes']}장면 · 예상 {res['est_total_sec']}초 → {res['folder']}")

    print(f"\n완료: {len(summary)}개 점포. 출력 폴더 → {args.out}")
    print("다음 단계: 각 점포 폴더의 clip_prompts.txt로 AI 클립 생성 →")
    print("           편집툴 템플릿에 vo_*.mp3 + 클립 + shotlist.csv 자막을 배치하세요.")


if __name__ == "__main__":
    main()
