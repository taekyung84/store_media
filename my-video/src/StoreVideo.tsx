import {
  AbsoluteFill,
  Audio,
  Img,
  OffthreadVideo,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from "remotion";
import type { Video, Caption, Info } from "./data";

const fontFamily = "-apple-system, 'Apple SD Gothic Neo', 'Noto Sans KR', 'Malgun Gothic', sans-serif";

// 웹앱에서 추가로 넘어올 수 있는 선택 필드
type AnimatedScene = { file: string; lineIdx: number; prompt?: string };
type VideoX = Video & {
  bg?: { top: string; bot: string; solid?: string };
  motion?: string; // 기본 / 인사 / 댄스 / 걷기 / 두리번 / 통통 / 없음
  animatedChar?: string; // Veo AI 생성 캐릭터 영상 경로 (하위호환)
  animatedScenes?: AnimatedScene[]; // 장면별 AI 클립 배열 (v2)
  useBgm?: boolean;
};

const ORANGE = "#F17829";
const DARK = "#464e28";
const WHITE = "#ffffff";
const DEFAULT_BG = { top: "#BED36C", bot: "#BED36C", solid: "#BED36C" };

// ... (getMotion 생략되지 않도록 보존)
function getMotion(motion: string, t: number) {
  switch (motion) {
    case "없음":
      return { x: 0, y: 0, rot: 0, sx: 1, sy: 1 };
    case "인사": {
      const y = Math.sin(t * 2) * -8;
      const rot = Math.sin(t * 5) * 9;
      return { x: 0, y, rot, sx: 1, sy: 1 };
    }
    case "소개": {
      const rot = Math.sin(t * 1.8) * 6;
      const x = Math.sin(t * 1.8) * 12;
      return { x, y: -6, rot, sx: 1.03, sy: 1.03 };
    }
    case "박수": {
      const bounce = Math.abs(Math.sin(t * 6));
      return { x: 0, y: -bounce * 18, rot: Math.sin(t * 6) * 3, sx: 1, sy: 1 };
    }
    case "깜짝": {
      const pop = Math.abs(Math.sin(t * 1.5)) * 0.08;
      return { x: 0, y: -10, rot: 0, sx: 1 + pop, sy: 1 + pop };
    }
    case "댄스": {
      const bounce = Math.abs(Math.sin(t * 4));
      const y = -bounce * 34;
      const x = Math.sin(t * 2) * 48;
      const rot = Math.sin(t * 4) * 9;
      const sy = 1 + (0.5 - Math.abs(0.5 - bounce)) * 0.08;
      return { x, y, rot, sx: 1, sy };
    }
    case "걷기": {
      const x = Math.sin(t * 0.8) * 210;
      const step = Math.abs(Math.sin(t * 5));
      const y = -step * 14;
      const dir = Math.cos(t * 0.8);
      const rot = (dir >= 0 ? 1 : -1) * 4 + Math.sin(t * 5) * 2;
      return { x, y, rot, sx: 1, sy: 1 };
    }
    case "두리번": {
      const s = Math.sin(t * 1.1);
      return { x: s * 34, y: Math.sin(t * 2.2) * 6, rot: s * 11, sx: 1, sy: 1 };
    }
    case "통통": {
      const bounce = Math.abs(Math.sin(t * 3));
      const y = -bounce * 46;
      const landing = 1 - bounce;
      const sy = 1 - landing * 0.1 + bounce * 0.06;
      const sx = 1 + landing * 0.1 - bounce * 0.04;
      return { x: 0, y, rot: 0, sx, sy };
    }
    default: {
      return {
        x: 0,
        y: Math.sin(t * 2.4) * 16,
        rot: Math.sin(t * 1.6) * 2.4,
        sx: 1,
        sy: 1 + Math.sin(t * 3) * 0.03,
      };
    }
  }
}

const Character: React.FC<{
  src: string;
  size: number;
  baseTop: number;
  motion?: string;
  entrance?: boolean;
  animatedSrc?: string;
}> = ({ src, size, baseTop, motion, entrance, animatedSrc }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const pop = entrance
    ? spring({ frame, fps, config: { damping: 12, mass: 0.6 }, durationInFrames: 30 })
    : 1;

  // AI 생성 영상이 있으면 OffthreadVideo를 사용 (동작이 잘리지 않고 프레임에 자연스럽게 맞춰지도록)
  if (animatedSrc) {
    return (
      <OffthreadVideo
        src={staticFile(animatedSrc)}
        style={{
          position: "absolute",
          width: size * 1.1, // 스케일 극대화하되 가장자리 동작이 자르지 않게
          left: "50%",
          top: baseTop - 20,
          transform: `translateX(-50%) scale(${pop})`,
          transformOrigin: "center bottom",
          filter: "drop-shadow(0 14px 20px rgba(0,0,0,0.1))",
          objectFit: "contain" as const,
        }}
        loop
        muted
      />
    );
  }

  // 기본: CSS 트랜스폼 애니메이션
  const m = getMotion(motion ?? "기본", t);
  return (
    <Img
      src={staticFile(src)}
      style={{
        position: "absolute",
        width: size,
        left: "50%",
        top: baseTop,
        transform: `translateX(-50%) translate(${m.x}px, ${m.y}px) rotate(${m.rot}deg) scale(${m.sx * pop}, ${m.sy * pop})`,
        transformOrigin: "center bottom",
        filter: "drop-shadow(0 16px 22px rgba(0,0,0,0.13))",
      }}
    />
  );
};

// ─── 장면별 AI 클립 전환 컴포넌트 (크로스페이드) ───
const ScenePlayer: React.FC<{
  scenes: AnimatedScene[];
  captions: Caption[];
  size: number;
  baseTop: number;
  fallbackSrc: string;
  fallbackMotion?: string;
}> = ({ scenes, captions, size, baseTop, fallbackSrc, fallbackMotion }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentMs = (frame / fps) * 1000;
  const FADE_FRAMES = Math.round(fps * 0.5); // 0.5초 크로스페이드

  // 현재 프레임이 어느 캡션(장면)에 해당하는지 결정
  let activeLineIdx = -1;
  for (let i = 0; i < captions.length; i++) {
    if (currentMs >= captions[i].fromMs && currentMs < captions[i].toMs) {
      activeLineIdx = i;
      break;
    }
  }

  // 활성 장면에 매칭되는 AI 클립 찾기
  const activeScene = scenes.find((s) => s.lineIdx === activeLineIdx);
  // 이전 장면 (크로스페이드 아웃용)
  const prevLineIdx = activeLineIdx > 0 ? activeLineIdx - 1 : -1;
  const prevScene = scenes.find((s) => s.lineIdx === prevLineIdx);

  // 크로스페이드 진행률 계산
  let fadeProgress = 1; // 1 = 완전히 새 장면
  if (activeLineIdx >= 0 && activeLineIdx < captions.length) {
    const captionStartFrame = Math.round((captions[activeLineIdx].fromMs / 1000) * fps);
    const framesSinceStart = frame - captionStartFrame;
    if (framesSinceStart < FADE_FRAMES && framesSinceStart >= 0) {
      fadeProgress = interpolate(framesSinceStart, [0, FADE_FRAMES], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
    }
  }

  // AI 클립이 없으면 CSS 모션 폴백
  if (!activeScene && !prevScene) {
    const t = frame / fps;
    const m = getMotion(fallbackMotion ?? "기본", t);
    return (
      <Img
        src={staticFile(fallbackSrc)}
        style={{
          position: "absolute",
          width: size,
          left: "50%",
          top: baseTop,
          transform: `translateX(-50%) translate(${m.x}px, ${m.y}px) rotate(${m.rot}deg) scale(${m.sx}, ${m.sy})`,
          transformOrigin: "center bottom",
          filter: "drop-shadow(0 16px 22px rgba(0,0,0,0.13))",
        }}
      />
    );
  }

  const videoStyle = (opacity: number) => ({
    position: "absolute" as const,
    width: size * 1.1,
    left: "50%",
    top: baseTop - 20,
    transform: "translateX(-50%)",
    transformOrigin: "center bottom",
    filter: "drop-shadow(0 14px 20px rgba(0,0,0,0.1))",
    objectFit: "contain" as const,
    opacity,
    transition: "opacity 0.3s ease",
  });

  return (
    <>
      {/* 이전 장면 (크로스페이드 아웃) */}
      {prevScene && fadeProgress < 1 && (
        <OffthreadVideo
          src={staticFile(prevScene.file)}
          style={videoStyle(1 - fadeProgress)}
          loop
          muted
        />
      )}
      {/* 현재 활성 장면 (크로스페이드 인) */}
      {activeScene && (
        <OffthreadVideo
          src={staticFile(activeScene.file)}
          style={videoStyle(fadeProgress)}
          loop
          muted
        />
      )}
    </>
  );
};

const Badge: React.FC<{ label: string }> = ({ label }) => (
  <div
    style={{
      display: "inline-block",
      background: ORANGE,
      color: WHITE,
      fontSize: 38,
      fontWeight: 700,
      padding: "10px 34px",
      borderRadius: 999,
    }}
  >
    {label}
  </div>
);

const CaptionBar: React.FC<{ text: string }> = ({ text }) => {
  const frame = useCurrentFrame();
  const appear = interpolate(frame, [0, 8], [0, 1], { extrapolateRight: "clamp" });
  return (
    <div
      style={{
        position: "absolute",
        left: 60,
        right: 60,
        bottom: 230,
        background: "rgba(255,255,255,0.94)",
        borderRadius: 36,
        padding: "40px 48px",
        textAlign: "center",
        fontFamily,
        fontSize: 56,
        fontWeight: 700,
        lineHeight: 1.35,
        color: DARK,
        opacity: appear,
        transform: `translateY(${(1 - appear) * 20}px)`,
        boxShadow: "0 10px 30px rgba(0,0,0,0.12)",
      }}
    >
      {text}
    </div>
  );
};

const Intro: React.FC<{ video: VideoX }> = ({ video }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame, fps, config: { damping: 200 }, durationInFrames: 25 });
  const y = interpolate(s, [0, 1], [40, 0]);
  return (
    <AbsoluteFill style={{ fontFamily, alignItems: "center" }}>
      <div style={{ marginTop: 410, opacity: s, transform: `translateY(${y}px)`, textAlign: "center" }}>
        <div style={{ fontSize: 40, color: DARK, opacity: 0.7, marginBottom: 24 }}>
          교보문고 {video.storeName}
        </div>
        <Badge label={`${video.type} 안내`} />
        <div style={{ fontSize: 140, fontWeight: 800, color: WHITE, margin: "20px 0 6px" }}>찬찬이</div>
        <div style={{ fontSize: 48, color: DARK }}>“조금 느려도 괜찮아요”</div>
      </div>
      <Character src={video.char} size={430} baseTop={1080} motion="인사" entrance animatedSrc={video.animatedChar} />
    </AbsoluteFill>
  );
};

const Outro: React.FC<{ video: VideoX }> = ({ video }) => {
  const frame = useCurrentFrame();
  const fade = interpolate(frame, [0, 12], [0, 1], { extrapolateRight: "clamp" });
  const info = video.info ?? [];
  return (
    <AbsoluteFill style={{ fontFamily, alignItems: "center", opacity: fade }}>
      <div style={{ marginTop: 410, textAlign: "center", width: 920 }}>
        <div style={{ fontSize: 76, fontWeight: 800, color: WHITE, lineHeight: 1.22 }}>{video.title}</div>
        {info.length > 0 && (
          <div
            style={{
              marginTop: 40,
              background: "rgba(255,255,255,0.9)",
              borderRadius: 28,
              padding: "30px 40px",
              display: "inline-block",
              minWidth: 620,
            }}
          >
            {info.map((it: Info, i: number) => (
              <div key={i} style={{ fontSize: 42, color: DARK, margin: "10px 0" }}>
                <span style={{ fontWeight: 800, color: ORANGE }}>{it.label}</span>
                <span style={{ marginLeft: 14 }}>{it.value}</span>
              </div>
            ))}
          </div>
        )}
        <div style={{ fontSize: 46, color: DARK, fontWeight: 700, marginTop: 48 }}>
          느루와 함께, 또 만나요!
        </div>
      </div>
      <Character src={video.char} size={400} baseTop={1180} motion="기본" animatedSrc={video.animatedChar} />
    </AbsoluteFill>
  );
};

const Body: React.FC<{ video: VideoX }> = ({ video }) => (
  <AbsoluteFill style={{ fontFamily }}>
    <div style={{ position: "absolute", top: 100, width: "100%", textAlign: "center" }}>
      <Badge label={video.type} />
      <div style={{ fontSize: 46, fontWeight: 700, color: WHITE, marginTop: 18 }}>
        교보문고 {video.storeName}
      </div>
    </div>
    {/* 장면별 AI 클립이 있으면 ScenePlayer, 없으면 기존 Character */}
    {video.animatedScenes && video.animatedScenes.length > 0 ? (
      <ScenePlayer
        scenes={video.animatedScenes}
        captions={video.captions}
        size={540}
        baseTop={440}
        fallbackSrc={video.char}
        fallbackMotion={video.motion}
      />
    ) : (
      <Character src={video.char} size={540} baseTop={440} motion={video.motion} animatedSrc={video.animatedChar} />
    )}
  </AbsoluteFill>
);

export const VideoComp: React.FC<{ video: VideoX }> = ({ video }) => {
  const { fps } = useVideoConfig();
  const introF = Math.round(video.introSec * fps);
  const outroStart = Math.round((video.totalSec - video.outroSec) * fps);
  const bodyDur = outroStart - introF;
  const bg = video.bg ?? DEFAULT_BG;
  // 단색 (solid) 배경 처리
  const solidColor = bg.solid || bg.top || "#BED36C";

  return (
    <AbsoluteFill style={{ background: solidColor }}>
      <Audio src={staticFile(video.audio)} />
      <Audio src={staticFile("audio/bgm_gentle.mp3")} volume={0.12} loop />

      <Sequence durationInFrames={introF} name="Intro">
        <Intro video={video} />
      </Sequence>

      <Sequence from={introF} durationInFrames={bodyDur} name="Body">
        <Body video={video} />
      </Sequence>

      {video.captions.map((c: Caption, i: number) => {
        const from = Math.round((c.fromMs / 1000) * fps);
        const dur = Math.max(1, Math.round(((c.toMs - c.fromMs) / 1000) * fps));
        return (
          <Sequence key={i} from={from} durationInFrames={dur} name={`Caption-${i + 1}`}>
            <CaptionBar text={c.text} />
          </Sequence>
        );
      })}

      <Sequence from={outroStart} name="Outro">
        <Outro video={video} />
      </Sequence>
    </AbsoluteFill>
  );
};
