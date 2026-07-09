#!/bin/bash
# 더블클릭하면 로컬 웹앱 실행 → 브라우저에서 입력으로 영상 제작
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

# ── python3 자동 탐색 ─────────────────────────────────────
PY="$(command -v python3 || true)"
[ -z "$PY" ] && [ -x /opt/anaconda3/bin/python3 ] && PY=/opt/anaconda3/bin/python3
[ -z "$PY" ] && [ -x /opt/homebrew/bin/python3 ] && PY=/opt/homebrew/bin/python3
[ -z "$PY" ] && [ -x /usr/bin/python3 ] && PY=/usr/bin/python3
if [ -z "$PY" ]; then
  echo "❌ python3를 찾을 수 없습니다. 터미널에서 'which python3'로 경로를 확인해 주세요."
  echo "아무 키나 누르면 닫힙니다."; read -n1 -s; exit 1
fi

# ── node/npx 확인 (영상 렌더에 필요) ──────────────────────
NPX="$(command -v npx || true)"
if [ -z "$NPX" ]; then
  echo "⚠️  npx(Node.js)를 찾을 수 없습니다."
  echo "   Homebrew: brew install node"
  echo "   또는 https://nodejs.org 에서 설치 후 다시 실행해 주세요."
  echo "아무 키나 누르면 닫힙니다."; read -n1 -s; exit 1
fi

# ── ffmpeg 확보 및 PATH 추가 (remotion 렌더에 필수) ──────────
"$PY" -c "import os, shutil, videolib; bin_dir = os.path.abspath('.bin'); os.makedirs(bin_dir, exist_ok=True); sym = os.path.join(bin_dir, 'ffmpeg'); [os.remove(sym) if os.path.exists(sym) or os.path.islink(sym) else None]; (os.symlink(videolib.FFMPEG, sym) if hasattr(os, 'symlink') else shutil.copy(videolib.FFMPEG, sym))" 2>/dev/null || true
export PATH="$(pwd)/.bin:$PATH"

echo "🐢 점포 영상 제작 자동화 웹앱을 시작합니다..."
echo "   Python: $PY"
echo "   Node:   $(node --version 2>/dev/null) ($(which node))"
echo "   FFmpeg: $(which ffmpeg 2>/dev/null || echo '⚠️ 심링크 실패')"
echo ""
"$PY" server.py
echo ""
echo "서버가 종료되었습니다. 이 창은 닫아도 됩니다. (아무 키나 누르면 닫힘)"
read -n1 -s
