import { Config } from "@remotion/cli/config";
import { resolve } from "path";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);

// ── 시스템 Chrome 연동용 래퍼 스크립트 지정 (프로파일 충돌 회피 & 무설치 구동) ──
const wrapperPath = resolve(process.cwd(), "chrome-wrapper.sh");
Config.setBrowserExecutable(wrapperPath);

// ── 웹 보안 해제 (구동 속도 향상 & 프리징 차단) ──
Config.setChromiumDisableWebSecurity(true);
