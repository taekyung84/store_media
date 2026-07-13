# ── 베이스: Python 3.11 슬림 ──────────────────────────────────────────
FROM python:3.11-slim

# ── 시스템 패키지: Node.js 20 LTS + ffmpeg + Chromium (Remotion 렌더용) ──
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ffmpeg \
    chromium \
    fonts-noto-cjk \
    ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# ── Remotion은 Chromium 경로를 환경변수로 지정 ───────────────────────
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium
# Render/Railway 무료 플랜 메모리 극단적 절약 플래그 지정 (안정적인 리눅스 플래그 위주 + 크롬 메모리 한도 지정)
ENV REMOTION_CHROME_FLAGS="--disable-dev-shm-usage --no-sandbox --disable-gpu --no-zygote --disable-extensions --disable-setuid-sandbox --disable-dev-tools --js-flags=--max-old-space-size=128 --renderer-process-limit=1"



# ── 작업 디렉토리 설정 ────────────────────────────────────────────────
WORKDIR /app

# ── Python 의존성 먼저 설치 (레이어 캐시 최적화) ─────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── my-video Node.js 의존성 설치 ──────────────────────────────────────
COPY my-video/package.json my-video/package-lock.json ./my-video/
RUN cd my-video && npm ci --prefer-offline

# ── 나머지 소스 복사 ──────────────────────────────────────────────────
COPY . .

# ── 포트 노출 (Railway가 PORT 환경변수 주입) ─────────────────────────
EXPOSE 8080

# ── 서버 실행 ─────────────────────────────────────────────────────────
CMD ["python", "server.py"]
