import { Config } from "@remotion/cli/config";
import { resolve } from "path";
import { existsSync } from "fs";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);

// ── 시스템 Chrome 연동용 래퍼 스크립트 지정 (프로파일 충돌 회피 & 무설치 구동) ──
const wrapperPath = resolve(process.cwd(), "chrome-wrapper.sh");
if (existsSync(wrapperPath)) {
  Config.setBrowserExecutable(wrapperPath);
}

// ── 웹 보안 해제 (구동 속도 향상 & 프리징 차단) ──
Config.setChromiumDisableWebSecurity(true);

// ── Render 512MB RAM 극약 처방: 크롬 탭당 JS 힙 메모리를 128MB로 제한 ──
Config.setChromiumFlags([
  "--js-flags=--max-old-space-size=128",
  "--renderer-process-limit=1",
  "--disable-dev-shm-usage",
  "--no-sandbox",
  "--disable-gpu",
  "--no-zygote",
  "--disable-extensions",
  "--disable-setuid-sandbox",
  "--disable-dev-tools"
]);

