#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
점포 영상 제작 자동화 — 로컬 웹앱
================================
브라우저 폼에서 점포·유형·목소리·내용을 선택/입력하면
무료 TTS(edge-tts) 음성 + 자막 + 메인 캐릭터 찬찬이 영상을 자동 생성합니다.

실행:  python3 server.py   →  http://localhost:8765
"""
import os, json, time, threading, webbrowser, shutil, subprocess, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, unquote, parse_qs
import videolib
import veo_animate

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.join(HERE, "my-video")   # Railway: 레포 내부
PUB = os.path.join(PROJ, "public")
OUT = os.path.join(PROJ, "out")
# Railway는 PORT 환경변수를 자동으로 주입합니다.
PORT = int(os.environ.get("PORT", 8765))
LOG_FILE = os.path.join(HERE, "usage_logs.json")


def _load_logs():
    """로그 파일에서 기존 로그를 로드합니다."""
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def _save_log(entry):
    """새 로그 항목을 추가 저장합니다."""
    logs = _load_logs()
    logs.insert(0, entry)  # 최신순
    # 최대 500건 유지
    if len(logs) > 500:
        logs = logs[:500]
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)


def _find_npx():
    """npx 실행 파일 경로를 찾습니다.
    .command 파일이 bash로 열리면 ~/.zprofile(homebrew)이 로드되지 않아
    npx가 PATH에 없을 수 있습니다. 명시적으로 탐색합니다."""
    # 1) PATH에 이미 있는 경우
    p = shutil.which("npx")
    if p:
        return p
    # 2) 일반적인 설치 경로 탐색
    candidates = [
        "/opt/homebrew/bin/npx",
        "/usr/local/bin/npx",
        os.path.expanduser("~/.nvm/current/bin/npx"),
    ]
    # nvm: 최신 버전 디렉토리 탐색
    nvm_dir = os.path.expanduser("~/.nvm/versions/node")
    if os.path.isdir(nvm_dir):
        for d in sorted(os.listdir(nvm_dir), reverse=True):
            candidates.append(os.path.join(nvm_dir, d, "bin", "npx"))
    for c in candidates:
        if os.path.isfile(c) and os.access(c, os.X_OK):
            # npx가 있으면 같은 디렉토리의 node도 PATH에 추가
            bindir = os.path.dirname(c)
            if bindir not in os.environ.get("PATH", ""):
                os.environ["PATH"] = bindir + ":" + os.environ.get("PATH", "")
            return c
    return None


NPX = _find_npx()

# remotion 렌더에 필수적인 ffmpeg가 system PATH에 없을 때를 위해,
# videolib.FFMPEG(imageio-ffmpeg 패키지의 바이너리)를 로컬 .bin/ffmpeg로 심링크/복사하고 PATH에 추가합니다.
def _setup_ffmpeg():
    bin_dir = os.path.join(HERE, ".bin")
    os.makedirs(bin_dir, exist_ok=True)
    sym_path = os.path.join(bin_dir, "ffmpeg")
    if os.path.exists(sym_path) or os.path.islink(sym_path):
        try:
            os.remove(sym_path)
        except Exception:
            pass
    try:
        os.symlink(videolib.FFMPEG, sym_path)
    except Exception:
        try:
            shutil.copy(videolib.FFMPEG, sym_path)
        except Exception:
            pass
    if os.path.isdir(bin_dir) and bin_dir not in os.environ.get("PATH", ""):
        os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")

_setup_ffmpeg()

STORES = {s["id"]: s for s in json.load(open(os.path.join(HERE, "stores.json"), encoding="utf-8"))}

# 렌더링 작업 상태 관리용 전역 객체
TASKS = {}
TASKS_LOCK = threading.Lock()

def bg_render_worker(task_id, p):
    try:
        t0 = time.time()
        with TASKS_LOCK:
            TASKS[task_id]["step"] = "AI 음성 / 애니메이션 처리 중..."
        outfile, video, engine = render_video(p)
        elapsed = round(time.time() - t0, 1)
        with TASKS_LOCK:
            TASKS[task_id] = {
                "status": "done",
                "file": outfile,
                "totalSec": video["totalSec"],
                "engine": engine,
                "elapsed": elapsed
            }
        # 로그 기록
        _save_log({
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "성공",
            "store": p.get("storeId", ""),
            "storeName": video.get("storeName", ""),
            "type": p.get("type", ""),
            "voice": p.get("voice", ""),
            "character": p.get("character", ""),
            "theme": p.get("theme", ""),
            "customColor": p.get("customThemeColor", ""),
            "motion": p.get("motion", ""),
            "useAi": p.get("useAiMotion", False),
            "title": p.get("title", ""),
            "lines": len(p.get("lines", [])),
            "totalSec": video["totalSec"],
            "engine": engine,
            "elapsed": elapsed,
            "file": outfile
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        with TASKS_LOCK:
            TASKS[task_id] = {
                "status": "failed",
                "error": str(e)
            }
        # 실패 로그 기록
        _save_log({
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "실패",
            "store": p.get("storeId", ""),
            "storeName": "",
            "type": p.get("type", ""),
            "voice": p.get("voice", ""),
            "character": p.get("character", ""),
            "theme": p.get("theme", ""),
            "customColor": p.get("customThemeColor", ""),
            "motion": p.get("motion", ""),
            "useAi": p.get("useAiMotion", False),
            "title": p.get("title", ""),
            "lines": len(p.get("lines", [])),
            "totalSec": 0,
            "engine": "",
            "elapsed": round(time.time() - t0, 1),
            "file": "",
            "error": str(e)
        })

# 배경 테마 단색 프리셋
THEMES = {
    "연두": {"top": "#BED36C", "bot": "#BED36C", "solid": "#BED36C"},
    "주황": {"top": "#F17829", "bot": "#F17829", "solid": "#F17829"},
    "하늘": {"top": "#9CC9E0", "bot": "#9CC9E0", "solid": "#9CC9E0"},
    "베이지": {"top": "#E3CDA3", "bot": "#E3CDA3", "solid": "#E3CDA3"},
    "분홍": {"top": "#E8A9C0", "bot": "#E8A9C0", "solid": "#E8A9C0"},
}


def seed_character(rel_path, src):
    """public/characters/ 에 캐릭터 이미지가 없을 때만 시드 복사.
    이미 있으면(=사용자가 교체했으면) 그대로 사용. 이 폴더가 유일한 원본."""
    dst = os.path.join(PUB, rel_path)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if not os.path.exists(dst) and os.path.exists(src):
        shutil.copy(src, dst)


def recommend(sid, vtype):
    """점포+유형에 맞는 추천 콘텐츠(제목/정보/내레이션) 생성."""
    s = STORES[sid]
    name = s["name"]
    ev = (s.get("events") or ["특별 기획전"])[0]
    if vtype == "이벤트":
        return {
            "title": f"{name} {ev}",
            "info": [["기간", "2026.00.00 ~ 00.00"], ["장소", "1층 이벤트 존"], ["", ""]],
            "lines": [
                f"조금 느려도 괜찮아요, {name} 찬찬이예요.",
                f"지금 저희 점포에서 {ev}이 열리고 있어요.",
                "다양한 도서와 즐길 거리를 준비했답니다.",
                "참여하고 특별한 혜택도 받아 가세요.",
                "느루와 함께 기다리고 있을게요!",
            ],
        }
    if vtype == "공지":
        return {
            "title": f"{name} 이용 안내",
            "info": [["운영시간", s.get("hours", "")], ["오시는길", s.get("directions", "")], ["", ""]],
            "lines": [
                f"안녕하세요, {name} 찬찬이예요.",
                f"저희 점포 운영시간은 {s.get('hours','')} 입니다.",
                "편안하게 둘러보실 수 있도록 준비했어요.",
                f"{s.get('directions','')} 천천히 찾아오세요.",
                "느루와 함께 기다릴게요!",
            ],
        }
    # 교육
    return {
        "title": f"{name} 이용 방법 안내",
        "info": [["문의", "고객센터 1599-0000"], ["장소", "1층 안내데스크"], ["", ""]],
        "lines": [
            f"조금 느려도 괜찮아요, 찬찬이가 알려드릴게요.",
            "오늘은 도서관 이용 방법을 소개할게요.",
            "1층 안내데스크에서 도움을 받을 수 있어요.",
            "회원카드가 있으면 적립과 할인이 가능해요.",
            "천천히 따라오시면 어렵지 않아요.",
            "느루와 함께 도와드릴게요!",
        ],
    }


def render_video(p):
    sid = str(p.get("storeId", "")).zfill(3)
    if sid not in STORES:
        raise ValueError("점포번호가 올바르지 않습니다 (001~028).")
    store = STORES[sid]
    lines = [l.strip() for l in p.get("lines", []) if l.strip()]
    if not lines:
        raise ValueError("내용(자막 문장)을 한 줄 이상 입력하세요.")
    voice_key = p.get("voice", "여성")
    if voice_key not in videolib.VOICES:
        voice_key = "여성"

    # 캐릭터: 기본=메인 찬찬이 / 점포특색=의상 캐릭터
    # ★ public/characters/ 가 원본. 파일이 없을 때만 시드 복사 → 사용자가 교체한 이미지는 보존됨.
    if p.get("character") == "store":
        char = f"characters/char_{sid}.png"
        seed_character(char, os.path.join(HERE, "stickers_cutout", f"{sid}_{store['name']}.png"))
    else:
        char = "characters/char_main.png"
        seed_character(char, os.path.join(HERE, "stickers_cutout", "main_찬찬이.png"))

    stamp = time.strftime("%y%m%d%H%M")
    audio_id = "web_" + time.strftime("%y%m%d%H%M%S")
    caps, total, intro, outro, engine = videolib.make_narration(
        lines, os.path.join(PUB, "audio", f"{audio_id}.mp3"), voice_key=voice_key)

    info = [{"label": str(it[0]).strip(), "value": str(it[1]).strip()}
            for it in p.get("info", []) if str(it[1]).strip()]
            
    # 배경 단색 HEX 지정 (컬러피커 지정값 우선, 없으면 프리셋)
    custom_color = str(p.get("customThemeColor", "")).strip()
    if custom_color and custom_color.startswith("#"):
        bg = {"top": custom_color, "bot": custom_color, "solid": custom_color}
    else:
        bg = THEMES.get(p.get("theme", "연두"), THEMES["연두"])

    # AI 움직임 (Veo) 옵션 처리
    animated_char = None
    use_ai = p.get("useAiMotion", False)
    if use_ai:
        try:
            print("  🤖 Veo AI 캐릭터 비디오 생성 시작...")
            char_abs = os.path.join(PUB, char)
            anim_dir = os.path.join(PUB, "animated")
            motion_type = p.get("motion", "기본")
            lines_str = "\n".join(lines)
            anim_path = veo_animate.animate_character(
                char_abs, motion=motion_type, lines_text=lines_str,
                bg_colors=bg, output_dir=anim_dir
            )
            animated_char = "animated/" + os.path.basename(anim_path)
            print(f"  🤖 AI 캐릭터 영상 준비 완료: {animated_char}")
        except Exception as e:
            print(f"  ⚠️ AI 움직임 생성 실패, CSS 모션으로 자동 전환: {e}")
            animated_char = None

    video = {
        "id": audio_id, "title": p.get("title") or f"{store['name']} 안내",
        "type": p.get("type") or "안내", "storeId": sid, "storeName": store["name"],
        "neuru": "appear", "char": char, "audio": f"audio/{audio_id}.mp3",
        "info": info, "introSec": intro, "outroSec": outro, "totalSec": total,
        "captions": caps, "bg": bg, "motion": p.get("motion", "기본"),
    }
    if animated_char:
        video["animatedChar"] = animated_char

    os.makedirs(OUT, exist_ok=True)
    propsf = os.path.join(PROJ, f".props_{audio_id}.json")
    json.dump({"video": video}, open(propsf, "w", encoding="utf-8"), ensure_ascii=False)
    sec = round(total)
    outfile = f"{store['name']}_{stamp}_{sec}s.mp4"
    if not NPX:
        raise RuntimeError(
            "npx(Node.js)를 찾을 수 없습니다.\n"
            "Homebrew: brew install node\n"
            "또는 https://nodejs.org 에서 설치해 주세요.")
    try:
        subprocess.run([NPX, "remotion", "render", "WebVideo", os.path.join("out", outfile),
                        f"--props={propsf}", "--concurrency=1", "--log=error"],
                       cwd=PROJ, check=True, capture_output=True, text=True,
                       timeout=300)
    except subprocess.TimeoutExpired:
        raise RuntimeError("렌더 시간 초과 (5분). 다시 시도해 주세요.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError("렌더 실패:\n" + (e.stderr or e.stdout or str(e))[-1500:])
    except FileNotFoundError:
        raise RuntimeError(
            f"npx를 실행할 수 없습니다: {NPX}\n"
            "Node.js가 올바르게 설치되어 있는지 확인해 주세요.")
    finally:
        if os.path.exists(propsf):
            os.remove(propsf)
    return outfile, video, engine


PAGE = r"""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>교보문고 점포 미디어 랩 — 점포 영상 제작 자동화</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
<style>
/* ──── KDS Design Tokens ──── */
:root {
  /* Colors — KDS semantic tokens */
  --fg:           #1B1D22;     /* gray-900 */
  --fg-secondary: #4D5159;     /* gray-700 */
  --fg-tertiary:  #A6AAB2;     /* gray-500 */
  --fg-disabled:  #C9CCD2;     /* gray-400 */
  --bg:           #FFFFFF;
  --bg-subtle:    #F4F5F7;     /* gray-100 */
  --bg-muted:     #EAEBEE;     /* gray-200 */
  --border:       #E0E2E6;     /* gray-300 */
  --border-strong:#C9CCD2;     /* gray-400 */
  --accent:       #5055B1;     /* blue-700 — primary action */
  --accent-hover: #3F4391;     /* blue-800 — pressed */
  --accent-light: #EEEEF8;     /* blue-100 tint */
  --positive:     #4DAC27;     /* green-600 */
  --positive-bg:  #E8F5E9;
  --negative:     #EC1F2D;     /* red-500 */
  --warn-bg:      #FFFBE6;
  --warn-border:  #FFE58F;
  --warn-fg:      #D48806;
  --brand-navy:   #003477;     /* KYOBO logo navy */
  --brand-green:  #45B035;     /* KYOBO logo green */

  /* Typography */
  --font: 'Noto Sans KR', 'Roboto', -apple-system, 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif;
  --ls: -0.01em;

  /* Spacing (4px base cadence) */
  --sp-50:  2px;
  --sp-100: 4px;
  --sp-200: 8px;
  --sp-300: 12px;
  --sp-400: 16px;
  --sp-500: 20px;
  --sp-600: 24px;
  --sp-700: 28px;
  --sp-800: 32px;

  /* Radius (4px base) */
  --r-4:  4px;
  --r-8:  8px;
  --r-12: 12px;
  --r-16: 16px;
  --r-24: 24px;
  --r-round: 9999px;

  /* Elevation & Depth */
  --shadow-sm: 0 2px 8px rgba(0,0,0,0.04);
  --shadow-md: 0 4px 14px rgba(0,0,0,0.08);
  --shadow-lg: 0 20px 40px rgba(0,0,0,0.10); /* shadow-gray-200 */

  /* Motion */
  --ease: cubic-bezier(0.4, 0, 0.2, 1);
  --duration-fast: 150ms;
  --duration-base: 240ms;
}

/* ──── Reset & Global ──── */
*, *::before, *::after { box-sizing: border-box; }
body {
  margin: 0;
  font-family: var(--font);
  background: var(--bg-subtle);
  color: var(--fg);
  letter-spacing: var(--ls);
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}

/* ──── Top Brand GNB Header ──── */
.top-gnb {
  background: var(--bg);
  border-bottom: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
  position: sticky;
  top: 0;
  z-index: 100;
}
.gnb-inner {
  max-width: 1080px;
  margin: 0 auto;
  padding: var(--sp-300) var(--sp-600);
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.gnb-brand {
  display: flex;
  align-items: center;
  gap: var(--sp-300);
}
.brand-logo-text {
  display: flex;
  align-items: center;
}
.brand-logo-img {
  height: 40px;
  width: auto;
  display: block;
}
.service-divider {
  width: 1px;
  height: 20px;
  background: var(--border-strong);
}
.service-name {
  font-size: 15px;
  font-weight: 500;
  color: var(--fg);
}

/* ──── Hero Header Banner ──── */
.hero-banner {
  background: linear-gradient(180deg, #FFFFFF 0%, var(--bg-subtle) 100%);
  border-bottom: 1px solid var(--border);
  padding: var(--sp-600) var(--sp-600) var(--sp-500);
  text-align: center;
}
.hero-title {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  color: var(--fg);
  line-height: 1.4;
}
.hero-desc {
  margin: var(--sp-200) 0 0;
  font-size: 14px;
  color: var(--fg-secondary);
}

/* ──── Layout Wrapper ──── */
.wrap {
  max-width: 1080px;
  margin: 0 auto;
  padding: var(--sp-600);
  display: grid;
  grid-template-columns: 1.25fr 1fr;
  gap: var(--sp-600);
}
@media (max-width: 860px) {
  .wrap { grid-template-columns: 1fr; padding: var(--sp-400); }
}

/* ──── KDS Card Component ──── */
.kds-card {
  background: var(--bg);
  border-radius: var(--r-16);
  padding: var(--sp-600);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
}

/* ──── Section Header with Green Accent ──── */
.sec-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--fg);
  margin: 0 0 var(--sp-400);
  display: flex;
  align-items: center;
  gap: var(--sp-200);
  padding-bottom: var(--sp-300);
  border-bottom: 1px solid var(--border);
}
.sec-title::before {
  content: '';
  display: inline-block;
  width: 4px;
  height: 16px;
  background: var(--brand-green);
  border-radius: var(--r-4);
}

/* ──── Form Elements ──── */
.form-group {
  margin-bottom: var(--sp-400);
}
label {
  display: block;
  font-weight: 500;
  font-size: 13px;
  line-height: 20px;
  color: var(--fg);
  margin-bottom: var(--sp-100);
}
label .hint {
  font-size: 12px;
  font-weight: 400;
  color: var(--fg-tertiary);
  margin-left: var(--sp-100);
}
input, select, textarea {
  width: 100%;
  padding: 10px var(--sp-300);
  border: 1px solid var(--border);
  border-radius: var(--r-8);
  font-size: 14px;
  font-family: var(--font);
  letter-spacing: var(--ls);
  background: var(--bg);
  color: var(--fg);
  transition: border-color var(--duration-fast) var(--ease),
              box-shadow var(--duration-fast) var(--ease);
}
input:focus, select:focus, textarea:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-light);
}
textarea {
  min-height: 140px;
  line-height: 1.6;
  resize: vertical;
}
input::placeholder, textarea::placeholder {
  color: var(--fg-disabled);
}

/* ──── Rows & Grid ──── */
.row { display: flex; gap: var(--sp-300); }
.row > div { flex: 1; }
.inforow { display: flex; gap: var(--sp-200); margin-bottom: var(--sp-200); }
.inforow input:first-child { flex: 0 0 32%; }

/* ──── Tip Banner Box ──── */
.help-banner {
  background: var(--accent-light);
  border: 1px solid rgba(80, 85, 177, 0.18);
  border-radius: var(--r-8);
  padding: var(--sp-300) var(--sp-400);
  font-size: 13px;
  line-height: 20px;
  color: var(--fg-secondary);
  margin-bottom: var(--sp-500);
  display: flex;
  align-items: flex-start;
  gap: var(--sp-200);
}
.help-banner-icon {
  background: var(--accent);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: var(--r-4);
  flex-shrink: 0;
  margin-top: 1px;
}

/* ──── Fieldset Styling ──── */
fieldset {
  border: 1px solid var(--border);
  border-radius: var(--r-12);
  margin: var(--sp-500) 0 0;
  padding: var(--sp-400);
  background: #FAFAFC;
}
legend {
  font-size: 13px;
  font-weight: 700;
  color: var(--fg-secondary);
  padding: 0 var(--sp-200);
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--r-round);
}

/* ──── AI Option Banner (KDS Special Card) ──── */
.ai-option-card {
  display: flex;
  align-items: flex-start;
  gap: var(--sp-300);
  margin-top: var(--sp-400);
  padding: var(--sp-400);
  background: var(--warn-bg);
  border: 1px solid var(--warn-border);
  border-radius: var(--r-12);
}
.ai-option-card input[type="checkbox"] {
  width: 18px;
  height: 18px;
  margin-top: 2px;
  flex-shrink: 0;
  accent-color: var(--accent);
  cursor: pointer;
}
.ai-option-card label {
  margin: 0;
  font-size: 13px;
  font-weight: 400;
  cursor: pointer;
  line-height: 1.5;
  color: var(--fg);
}
.ai-option-header {
  font-size: 14px;
  font-weight: 700;
  color: var(--fg);
  display: flex;
  align-items: center;
  gap: var(--sp-200);
}
.ai-option-card .desc {
  display: block;
  margin-top: var(--sp-100);
  font-size: 12px;
  line-height: 18px;
  color: var(--fg-secondary);
}

/* ──── Badges ──── */
.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: var(--r-4);
  font-size: 11px;
  font-weight: 700;
  line-height: 16px;
}
.badge--free {
  background: var(--positive-bg);
  color: #2A6614;
}
.badge--paid {
  background: #FFF0B3;
  color: var(--warn-fg);
}

/* ──── Action Buttons ──── */
.btn-group {
  display: flex;
  gap: var(--sp-300);
  margin-top: var(--sp-600);
}
button {
  flex: 1;
  border: none;
  border-radius: var(--r-12);
  padding: 14px var(--sp-400);
  font-size: 15px;
  font-weight: 700;
  font-family: var(--font);
  letter-spacing: var(--ls);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease);
}
#rec {
  background: var(--bg);
  color: var(--fg-secondary);
  border: 1px solid var(--border-strong);
}
#rec:hover {
  background: var(--bg-muted);
  color: var(--fg);
}
#go {
  background: var(--accent);
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(80, 85, 177, 0.25);
}
#go:hover {
  background: var(--accent-hover);
  box-shadow: 0 6px 16px rgba(80, 85, 177, 0.35);
}
button:disabled {
  opacity: 0.5;
  cursor: wait;
  box-shadow: none !important;
}

/* ──── Status Indicator ──── */
#status {
  margin-top: var(--sp-300);
  font-size: 13px;
  line-height: 20px;
  min-height: 20px;
  color: var(--fg-secondary);
}

/* ──── Preview Display Shell (Mockup Player) ──── */
.preview-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.player-shell {
  background: #111318;
  border-radius: var(--r-24);
  padding: 12px;
  box-shadow: var(--shadow-lg);
  position: relative;
  overflow: hidden;
  margin-top: var(--sp-200);
}
.player-screen {
  aspect-ratio: 9/16;
  width: 100%;
  max-height: 560px;
  background: #000;
  border-radius: var(--r-16);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
video {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
.placeholder-view {
  text-align: center;
  padding: var(--sp-600) var(--sp-400);
  color: var(--fg-tertiary);
}
.placeholder-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto var(--sp-300);
  background: rgba(255,255,255,0.06);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--fg-tertiary);
}
.placeholder-text {
  font-size: 13px;
  line-height: 20px;
  color: #8A8F9B;
}
a.dl-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--sp-200);
  margin-top: var(--sp-400);
  padding: 12px var(--sp-400);
  background: var(--bg-subtle);
  border: 1px solid var(--border);
  border-radius: var(--r-12);
  color: var(--accent);
  font-weight: 700;
  text-decoration: none;
  font-size: 14px;
  transition: background var(--duration-fast) var(--ease);
}
a.dl-btn:hover {
  background: var(--accent-light);
}

/* ──── Loading Spinner — Counter-Clockwise ──── */
.spin {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin-ccw 0.9s linear infinite;
  vertical-align: -2px;
  margin-right: var(--sp-200);
}
@keyframes spin-ccw {
  to { transform: rotate(-360deg); }
}

/* ──── Settings Button (GNB) ──── */
.gnb-actions {
  display: flex;
  align-items: center;
  gap: var(--sp-200);
}
.btn-icon {
  width: 38px;
  height: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border);
  border-radius: var(--r-8);
  background: var(--bg);
  color: var(--fg-secondary);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease);
  flex-shrink: 0;
  padding: 0;
}
.btn-icon:hover {
  background: var(--bg-subtle);
  color: var(--fg);
  border-color: var(--border-strong);
}

/* ──── Log Modal Overlay ──── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(27, 29, 34, 0.45);
  z-index: 200;
  display: none;
  align-items: center;
  justify-content: center;
  animation: fade-in var(--duration-base) var(--ease);
}
.modal-overlay.active {
  display: flex;
}
@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}
.modal-panel {
  background: var(--bg);
  border-radius: var(--r-24);
  width: min(90vw, 960px);
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-lg);
  animation: slide-up var(--duration-base) var(--ease);
}
@keyframes slide-up {
  from { transform: translateY(24px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--sp-500) var(--sp-600);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.modal-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--fg);
  display: flex;
  align-items: center;
  gap: var(--sp-200);
}
.modal-header h2::before {
  content: '';
  display: inline-block;
  width: 4px;
  height: 18px;
  background: var(--brand-green);
  border-radius: var(--r-4);
}
.modal-close {
  width: 32px;
  height: 32px;
  border: none;
  background: var(--bg-subtle);
  border-radius: var(--r-8);
  color: var(--fg-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  padding: 0;
  flex: none;
  transition: all var(--duration-fast) var(--ease);
}
.modal-close:hover {
  background: var(--bg-muted);
  color: var(--fg);
}
.modal-body {
  padding: var(--sp-500) var(--sp-600);
  overflow-y: auto;
  flex: 1;
}

/* ──── Log Summary Stats ──── */
.log-stats {
  display: flex;
  gap: var(--sp-300);
  margin-bottom: var(--sp-500);
  flex-wrap: wrap;
}
.stat-card {
  background: var(--bg-subtle);
  border: 1px solid var(--border);
  border-radius: var(--r-12);
  padding: var(--sp-300) var(--sp-400);
  flex: 1;
  min-width: 120px;
  text-align: center;
}
.stat-card .stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--accent);
  line-height: 1.2;
}
.stat-card .stat-label {
  font-size: 12px;
  color: var(--fg-secondary);
  margin-top: var(--sp-50);
}
.stat-card.stat-success .stat-value { color: var(--positive); }
.stat-card.stat-fail .stat-value { color: var(--negative); }

/* ──── Log Table ──── */
.log-table-wrap {
  overflow-x: auto;
  border: 1px solid var(--border);
  border-radius: var(--r-12);
}
.log-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  min-width: 700px;
}
.log-table thead {
  background: var(--bg-subtle);
  position: sticky;
  top: 0;
  z-index: 1;
}
.log-table th {
  padding: var(--sp-300) var(--sp-300);
  font-weight: 700;
  font-size: 12px;
  color: var(--fg-secondary);
  text-align: left;
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
}
.log-table td {
  padding: var(--sp-200) var(--sp-300);
  border-bottom: 1px solid var(--border);
  color: var(--fg);
  vertical-align: middle;
}
.log-table tbody tr:hover {
  background: rgba(80, 85, 177, 0.03);
}
.log-table tbody tr:last-child td {
  border-bottom: none;
}
.log-status {
  display: inline-block;
  padding: 2px 8px;
  border-radius: var(--r-round);
  font-size: 11px;
  font-weight: 700;
}
.log-status.s-ok {
  background: var(--positive-bg);
  color: #2A6614;
}
.log-status.s-fail {
  background: #FFEAEC;
  color: #B01219;
}
.log-empty {
  text-align: center;
  padding: var(--sp-800) var(--sp-400);
  color: var(--fg-tertiary);
  font-size: 14px;
}
.log-ai-badge {
  display: inline-block;
  padding: 1px 6px;
  border-radius: var(--r-4);
  font-size: 10px;
  font-weight: 700;
  background: #FFF0B3;
  color: var(--warn-fg);
}

/* ──── Footer ──── */
footer {
  text-align: center;
  padding: var(--sp-600) var(--sp-400);
  font-size: 12px;
  color: var(--fg-tertiary);
  border-top: 1px solid var(--border);
  margin-top: var(--sp-800);
  background: var(--bg);
}
</style></head><body>

<!-- Top Brand GNB Header -->
<header class="top-gnb">
  <div class="gnb-inner">
    <div class="gnb-brand">
      <span class="brand-logo-text"><img class="brand-logo-img" src="https://contents.kyobobook.co.kr/resources/fo/images/common/ink/united/logo_book.svg" alt="교보문고"></span>
      <span class="service-divider"></span>
      <span class="service-name">점포 미디어 랩</span>
    </div>
    <div class="gnb-actions">
      <button class="btn-icon" onclick="openLogModal()" title="설정 / 사용 기록">
        <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
      </button>
    </div>
  </div>
</header>

<!-- Hero Title Banner -->
<section class="hero-banner">
  <h1 class="hero-title">점포 안내 영상 자동 생성 시스템</h1>
  <p class="hero-desc">점포와 안내 유형을 선택하면 고품질 TTS 음성 및 캐릭터 영상이 10초 만에 완성됩니다.</p>
</section>

<!-- Main Layout -->
<div class="wrap">
  <!-- Left: Control Panel Card -->
  <div class="kds-card">
    <div class="sec-title">기본 정보 설정</div>
    
    <div class="help-banner">
      <span class="help-banner-icon">TIP</span>
      <div>[점포]와 [유형] 선택 후 <strong>"추천 내용 불러오기"</strong>를 누르시면 최적의 카피 문구가 자동 작성됩니다.</div>
    </div>

    <div class="row form-group">
      <div><label>점포 선택</label><select id="storeId">__STORE_OPTIONS__</select></div>
      <div><label>안내 유형</label><select id="type"><option>이벤트</option><option>공지</option><option>교육</option></select></div>
    </div>

    <div class="form-group">
      <label>영상 제목 <span class="hint">아웃트로 엔딩 카드로 표시됩니다</span></label>
      <input id="title" placeholder="예: 광화문점 독서의 달 스탬프 투어">
    </div>

    <div class="form-group">
      <label>아웃트로 세부 정보 <span class="hint">항목명 / 내용 (미입력 항목은 자동 제외)</span></label>
      <div class="inforow"><input id="infoL0" placeholder="예: 기간"><input id="infoV0" placeholder="예: 2026.06.01 ~ 06.30"></div>
      <div class="inforow"><input id="infoL1" placeholder="예: 장소"><input id="infoV1" placeholder="예: 1층 이벤트 존"></div>
      <div class="inforow"><input id="infoL2" placeholder="예: 대상"><input id="infoV2" placeholder="예: 전 연령"></div>
    </div>

    <div class="form-group">
      <label>내레이션 자막 대본 <span class="hint">한 줄 = 자막 1문장 = 음성 1단락</span></label>
      <textarea id="lines" placeholder="'추천 내용 불러오기'를 누르면 점포 및 유형에 맞는 내레이션 문구가 자동으로 설정됩니다."></textarea>
    </div>

    <!-- Customization Fieldset -->
    <fieldset>
      <legend>스타일 & 모션 커스터마이징</legend>
      <div class="row form-group" style="margin-top: var(--sp-200);">
        <div><label>목소리 톤</label><select id="voice"><option>[Google AI] 찬찬이</option><option>[Google AI] 느루</option><option>여성</option><option>남성</option><option>여아</option><option>남아</option></select></div>
        <div><label>캐릭터 종류</label><select id="character"><option value="main">기본 찬찬이</option><option value="store">점포 특색 캐릭터</option></select></div>
      </div>
      <div class="row form-group">
        <div>
          <label>배경 테마 단색 <span class="hint">프리셋 OR 컬러피커</span></label>
          <div style="display:flex; gap:6px; align-items:center;">
            <select id="theme" onchange="onThemeSelectChange()">
              <option value="연두" data-color="#BED36C">연두 (#BED36C)</option>
              <option value="주황" data-color="#F17829">주황 (#F17829)</option>
              <option value="하늘" data-color="#9CC9E0">하늘 (#9CC9E0)</option>
              <option value="베이지" data-color="#E3CDA3">베이지 (#E3CDA3)</option>
              <option value="분홍" data-color="#E8A9C0">분홍 (#E8A9C0)</option>
            </select>
            <input type="color" id="themePicker" value="#BED36C" title="직접 배경색 선택 (Color Picker)" style="width:42px; height:38px; padding:2px; cursor:pointer; border:1px solid var(--border); border-radius:var(--r-8); flex-shrink:0;">
          </div>
        </div>
        <div><label>동작 프리셋</label><select id="motion"><option>인사 (기본)</option><option>소개 (안내추천)</option><option>박수 (이벤트추천)</option><option>깜짝</option><option>댄스</option><option>걷기</option><option>두리번</option><option>통통</option><option>없음</option></select></div>
      </div>

      <!-- AI Motion Banner Card -->
      <div class="ai-option-card">
        <input type="checkbox" id="useAiMotion">
        <label for="useAiMotion">
          <div class="ai-option-header">
            AI 내용 기반 자동 움직임 (Veo)
            <span class="badge badge--paid">선택 시 유료</span>
          </div>
          <span class="desc">
            • <strong>체크 시</strong>: Gemini가 내레이션 맥락을 분석하여 최적의 캐릭터 모션을 AI 영상으로 자동 생성합니다.<br>
            • <strong>체크 해제 시</strong>: 선택한 프리셋 동작으로 100% 무료 렌더링됩니다. <span class="badge badge--free">무료</span><br>
            • <em>동일 조건 영상은 스마트 캐시가 적용되어 재발행 시 추가 생성비 없이 10초 내 완료됩니다.</em>
          </span>
        </label>
      </div>
    </fieldset>

    <div class="btn-group">
      <button id="rec" onclick="loadRec()">추천 내용 불러오기</button>
      <button id="go" onclick="gen()">영상 만들기</button>
    </div>
    <div id="status"></div>
  </div>

  <!-- Right: Video Preview Card Shell -->
  <div class="kds-card preview-container">
    <div class="sec-title">영상 미리보기 / 다운로드</div>
    <div class="player-shell">
      <div class="player-screen" id="result">
        <div class="placeholder-view">
          <div class="placeholder-icon">
            <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
          </div>
          <div class="placeholder-text">
            왼쪽에서 설정을 마친 후<br>
            <strong>"영상 만들기"</strong>를 누르시면<br>
            이곳에 완성본 영상이 표시됩니다.
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- Log Modal -->
<div class="modal-overlay" id="logModal">
  <div class="modal-panel">
    <div class="modal-header">
      <h2>사용 기록</h2>
      <button class="modal-close" onclick="closeLogModal()">
        <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
      </button>
    </div>
    <div class="modal-body" id="logModalBody">
      <div class="log-empty">로그를 불러오는 중...</div>
    </div>
  </div>
</div>

<footer>
  © Kyobo Book Centre Store Media Lab. All Rights Reserved.
</footer>

<script>
function setInfo(rows){for(var i=0;i<3;i++){var r=rows[i]||["",""];document.getElementById('infoL'+i).value=r[0];document.getElementById('infoV'+i).value=r[1];}}

/* ──── Log Modal ──── */
function openLogModal(){
  document.getElementById('logModal').classList.add('active');
  document.body.style.overflow='hidden';
  fetchLogs();
}
function closeLogModal(){
  document.getElementById('logModal').classList.remove('active');
  document.body.style.overflow='';
}
// 오버레이 클릭 시 닫기
document.getElementById('logModal').addEventListener('click',function(e){
  if(e.target===this) closeLogModal();
});
// ESC 닫기
document.addEventListener('keydown',function(e){
  if(e.key==='Escape' && document.getElementById('logModal').classList.contains('active')) closeLogModal();
});

function fetchLogs(){
  fetch('/api/logs').then(r=>r.json()).then(function(logs){
    renderLogs(logs);
  }).catch(function(){
    document.getElementById('logModalBody').innerHTML='<div class="log-empty">로그를 불러올 수 없습니다.</div>';
  });
}

function renderLogs(logs){
  var body=document.getElementById('logModalBody');
  if(!logs.length){
    body.innerHTML='<div class="log-empty"><svg width="40" height="40" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24" style="color:var(--fg-disabled);margin-bottom:8px"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg><br>아직 영상 생성 기록이 없습니다.<br><span style="font-size:12px;color:var(--fg-disabled)">영상을 생성하면 이곳에 기록이 표시됩니다.</span></div>';
    return;
  }
  var totalCnt=logs.length;
  var okCnt=logs.filter(function(l){return l.status==="성공";}).length;
  var failCnt=totalCnt-okCnt;
  var aiCnt=logs.filter(function(l){return l.useAi;}).length;

  var html='<div class="log-stats">';
  html+='<div class="stat-card"><div class="stat-value">'+totalCnt+'</div><div class="stat-label">전체 생성 횟수</div></div>';
  html+='<div class="stat-card stat-success"><div class="stat-value">'+okCnt+'</div><div class="stat-label">성공</div></div>';
  html+='<div class="stat-card stat-fail"><div class="stat-value">'+failCnt+'</div><div class="stat-label">실패</div></div>';
  html+='<div class="stat-card"><div class="stat-value">'+aiCnt+'</div><div class="stat-label">AI (Veo) 사용</div></div>';
  html+='</div>';

  html+='<div class="log-table-wrap"><table class="log-table"><thead><tr>';
  html+='<th>일시</th><th>상태</th><th>점포</th><th>유형</th><th>음성</th><th>테마</th><th>동작</th><th>AI</th><th>영상길이</th><th>소요시간</th>';
  html+='</tr></thead><tbody>';

  logs.forEach(function(l){
    var statusCls=l.status==="성공"?'s-ok':'s-fail';
    html+='<tr>';
    html+='<td style="white-space:nowrap;font-size:12px;color:var(--fg-secondary)">'+l.timestamp+'</td>';
    html+='<td><span class="log-status '+statusCls+'">'+l.status+'</span></td>';
    html+='<td>'+(l.storeName || l.store)+'</td>';
    html+='<td>'+l.type+'</td>';
    html+='<td style="font-size:12px">'+l.voice+'</td>';
    html+='<td>'+(l.customColor||l.theme)+'</td>';
    html+='<td style="font-size:12px">'+(l.motion||'-')+'</td>';
    html+='<td>'+(l.useAi?'<span class="log-ai-badge">Veo</span>':'-')+'</td>';
    html+='<td>'+(l.totalSec?l.totalSec+'초':'-')+'</td>';
    html+='<td>'+(l.elapsed?l.elapsed+'초':'-')+'</td>';
    html+='</tr>';
  });
  html+='</tbody></table></div>';
  body.innerHTML=html;
}

function onThemeSelectChange(){
 var sel=document.getElementById('theme');
 var opt=sel.options[sel.selectedIndex];
 var color=opt.getAttribute('data-color');
 if(color){
   document.getElementById('themePicker').value=color;
 }
}

function loadRec(){
 var sid=document.getElementById('storeId').value, ty=document.getElementById('type').value;
 fetch('/api/recommend?store='+sid+'&type='+encodeURIComponent(ty)).then(r=>r.json()).then(function(d){
  document.getElementById('title').value=d.title;
  document.getElementById('lines').value=d.lines.join('\n');
  setInfo(d.info);
  document.getElementById('status').textContent='추천 내용을 불러왔습니다. 자유롭게 입력값을 수정해 보세요.';
 });
}

function gen(){
 var btn=document.getElementById('go'), st=document.getElementById('status');
 var lines=document.getElementById('lines').value.split('\n').map(s=>s.trim()).filter(Boolean);
 if(!lines.length){st.textContent='내용을 한 줄 이상 입력해 주세요.';return;}
 var info=[];for(var i=0;i<3;i++){info.push([document.getElementById('infoL'+i).value,document.getElementById('infoV'+i).value]);}
  var useAi=document.getElementById('useAiMotion').checked;
  var customColor=document.getElementById('themePicker').value;
  var payload={storeId:document.getElementById('storeId').value,type:document.getElementById('type').value,
   voice:document.getElementById('voice').value,character:document.getElementById('character').value,
   theme:document.getElementById('theme').value,customThemeColor:customColor,motion:document.getElementById('motion').value,
   title:document.getElementById('title').value,info:info,lines:lines,useAiMotion:useAi};
   btn.disabled=true; st.innerHTML='<span class="spin"></span>'+(useAi?'AI 캐릭터 생성 + ':'')+'음성 합성 및 영상 렌더링 중… '+(useAi?'(약 2~4분 소요':'(약 1~2분 소요')+', 창을 닫지 마세요)';
  var t0=Date.now();
  var dots=setInterval(function(){var s=Math.round((Date.now()-t0)/1000);st.innerHTML='<span class="spin"></span>영상 렌더링 진행 중… '+s+'초 경과';},1000);
  
  fetch('/api/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)})
   .then(r=>r.json()).then(function(d){
    if(!d.ok){
      clearInterval(dots);btn.disabled=false;st.textContent='오류 발생: '+d.error;return;
    }
    var taskId=d.taskId;
    var pollTimer=setInterval(function(){
      fetch('/api/status?taskId='+taskId)
        .then(r=>r.json()).then(function(statusRes){
          if(statusRes.status==='done'){
            clearInterval(dots);clearInterval(pollTimer);btn.disabled=false;
            st.textContent='영상 제작 완료 ('+statusRes.totalSec+'초, 음성: '+statusRes.engine+', 렌더 '+statusRes.elapsed+'초)';
            var u='/out/'+encodeURIComponent(statusRes.file)+'?t='+Date.now();
            document.getElementById('result').innerHTML='<video src="'+u+'" controls autoplay muted></video>';
            
            // 다운로드 버튼 생성 (기존 placeholder 외부 디바이스 쉘 아래에 깔끔하게 배치)
            var existingDl = document.getElementById('dl-link');
            if(existingDl) existingDl.remove();
            
            var a = document.createElement('a');
            a.id = 'dl-link';
            a.className = 'dl-btn';
            a.href = u;
            a.download = statusRes.file;
            a.innerHTML = '<svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg> 완성본 파일 다운로드 ('+statusRes.file+')';
            document.querySelector('.preview-container').appendChild(a);
            
          } else if(statusRes.status==='failed'){
            clearInterval(dots);clearInterval(pollTimer);btn.disabled=false;
            st.textContent='오류 발생: '+statusRes.error;
          }
        }).catch(function(e){
          clearInterval(dots);clearInterval(pollTimer);btn.disabled=false;
          st.textContent='상태 확인 오류: '+e;
        });
    }, 2000);
   }).catch(function(e){clearInterval(dots);btn.disabled=false;st.textContent='오류 발생: '+e;});
}
</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, ctype, body):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        path = unquote(u.path)
        if path in ("/", "/index.html"):
            opts = "".join(f'<option value="{i}">{i} {s["name"]}</option>' for i, s in STORES.items())
            return self._send(200, "text/html; charset=utf-8",
                              PAGE.replace("__STORE_OPTIONS__", opts).encode("utf-8"))
        if path == "/api/recommend":
            q = parse_qs(u.query)
            sid = q.get("store", ["001"])[0].zfill(3)
            ty = q.get("type", ["이벤트"])[0]
            rec = recommend(sid, ty) if sid in STORES else {"title": "", "info": [], "lines": []}
            return self._send(200, "application/json; charset=utf-8",
                              json.dumps(rec, ensure_ascii=False).encode("utf-8"))
        if path == "/api/status":
            q = parse_qs(u.query)
            tid = q.get("taskId", [""])[0]
            with TASKS_LOCK:
                res = TASKS.get(tid, {"status": "not_found"})
            return self._send(200, "application/json; charset=utf-8",
                              json.dumps(res, ensure_ascii=False).encode("utf-8"))
        if path.startswith("/out/"):
            f = os.path.join(OUT, os.path.basename(path))
            if os.path.exists(f):
                with open(f, "rb") as fh:
                    return self._send(200, "video/mp4", fh.read())
            return self._send(404, "text/plain", b"not found")
        if path == "/api/logs":
            logs = _load_logs()
            return self._send(200, "application/json; charset=utf-8",
                              json.dumps(logs, ensure_ascii=False).encode("utf-8"))
        return self._send(404, "text/plain; charset=utf-8", "없는 경로".encode("utf-8"))

    def do_POST(self):
        if urlparse(self.path).path != "/api/generate":
            return self._send(404, "text/plain", b"not found")
        n = int(self.headers.get("Content-Length", 0))
        p = json.loads(self.rfile.read(n).decode("utf-8"))
        
        # 태스크 ID 생성
        task_id = "task_" + str(int(time.time() * 1000))
        with TASKS_LOCK:
            TASKS[task_id] = {"status": "running"}
            
        # 백그라운드 렌더링 스레드 실행
        t = threading.Thread(target=bg_render_worker, args=(task_id, p))
        t.daemon = True
        t.start()
        
        body = json.dumps({"ok": True, "taskId": task_id}, ensure_ascii=False)
        self._send(200, "application/json; charset=utf-8", body.encode("utf-8"))


def main():
    ThreadingHTTPServer.allow_reuse_address = True
    is_cloud = bool(os.environ.get("RAILWAY_ENVIRONMENT") or os.environ.get("RAILWAY_PROJECT_ID") or os.environ.get("RENDER"))
    # 클라우드: 0.0.0.0으로 바인딩 / 로컬: 127.0.0.1
    host = "0.0.0.0" if is_cloud else "127.0.0.1"
    srv = None
    if is_cloud:
        # Railway: 포트 고정 (환경변수 PORT)
        try:
            srv = ThreadingHTTPServer((host, PORT), Handler)
        except OSError as e:
            print(f"❌ 포트 {PORT} 바인딩 실패: {e}")
            return
    else:
        for port in range(PORT, PORT + 10):
            try:
                srv = ThreadingHTTPServer((host, port), Handler)
                break
            except OSError:
                continue
    if srv is None:
        print(f"❌ 사용 가능한 포트를 찾지 못했습니다 ({PORT}~{PORT+9}).")
        print("   이미 실행 중인 웹앱이 있는지 확인하거나, 기존 터미널 창을 닫고 다시 시도하세요.")
        return
    port = srv.server_address[1]
    url = f"http://localhost:{port}"
    print(f"\n🐢 점포 영상 제작 자동화 웹앱 → {url}")
    print(f"   npx: {NPX or '⚠️ 없음 — 영상 렌더 불가!'}")
    print(f"   (종료: Ctrl+C)\n")
    if not NPX:
        print("⚠️  npx(Node.js)를 찾을 수 없습니다. 영상 만들기가 작동하지 않습니다.")
        print("   Homebrew: brew install node")
        print("   또는 https://nodejs.org 에서 설치해 주세요.\n")
    if not is_cloud and port != PORT:
        print(f"※ 기본 포트 {PORT}가 사용 중이어서 {port}로 열었습니다.")
        print(f"  (이전에 띄운 웹앱이 아직 켜져 있을 수 있어요 → http://localhost:{PORT})\n")
    # 로컬에서만 브라우저 자동 실행 (클라우드 서버에서는 생략)
    if not is_cloud:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n종료합니다.")


if __name__ == "__main__":
    main()
