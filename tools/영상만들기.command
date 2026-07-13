#!/bin/bash
# 더블클릭: MD → 음성·데이터 생성 → 28+편 영상 렌더
cd "$(dirname "$0")"

# ── 사용자 프로필 및 환경설정 로드 ────────────────────────────────
# Finder에서 실행할 때 사용자 PATH(node, npx 등)가 로드되지 않는 문제를 방지합니다.
[ -f "$HOME/.zprofile" ] && source "$HOME/.zprofile" 2>/dev/null
[ -f "$HOME/.zshrc" ] && source "$HOME/.zshrc" 2>/dev/null
[ -f "$HOME/.bash_profile" ] && source "$HOME/.bash_profile" 2>/dev/null
[ -f "$HOME/.bashrc" ] && source "$HOME/.bashrc" 2>/dev/null

# ── PATH 보강 (기본 경로 확인) ──────────────────────────────────
[ -x /opt/homebrew/bin/brew ] && eval "$(/opt/homebrew/bin/brew shellenv)" 2>/dev/null
[ -d /opt/anaconda3/bin ] && export PATH="/opt/anaconda3/bin:$PATH"
[ -d /usr/local/bin ] && export PATH="/usr/local/bin:$PATH"
[ -s "$HOME/.nvm/nvm.sh" ] && . "$HOME/.nvm/nvm.sh" 2>/dev/null

PY="$(command -v python3 || true)"
[ -z "$PY" ] && [ -x /opt/anaconda3/bin/python3 ] && PY=/opt/anaconda3/bin/python3
[ -z "$PY" ] && [ -x /opt/homebrew/bin/python3 ] && PY=/opt/homebrew/bin/python3
[ -z "$PY" ] && [ -x /usr/bin/python3 ] && PY=/usr/bin/python3
if [ -z "$PY" ]; then echo "❌ python3를 찾을 수 없습니다."; read -n1 -s; exit 1; fi

if ! command -v npm &>/dev/null; then
  echo "❌ npm(Node.js)을 찾을 수 없습니다. brew install node 로 설치해 주세요."
  read -n1 -s; exit 1
fi

# ── ffmpeg 확보 및 PATH 추가 (remotion 렌더에 필수) ──────────
"$PY" -c "import os, shutil, videolib; bin_dir = os.path.abspath('.bin'); os.makedirs(bin_dir, exist_ok=True); sym = os.path.join(bin_dir, 'ffmpeg'); [os.remove(sym) if os.path.exists(sym) or os.path.islink(sym) else None]; (os.symlink(videolib.FFMPEG, sym) if hasattr(os, 'symlink') else shutil.copy(videolib.FFMPEG, sym))" 2>/dev/null || true
export PATH="$(pwd)/.bin:$PATH"

echo "▶ 1/2  MD에서 음성·데이터 생성 중… ($PY)"
"$PY" build_from_md.py || { echo "❌ 생성 실패"; read -n1 -s; exit 1; }
echo "▶ 2/2  영상 렌더링 중…"
cd ../my-video && npm run render-all
echo ""
echo "✅ 완료! my-video/out/ 폴더를 확인하세요. (아무 키나 누르면 닫힘)"
read -n1 -s

