import "./index.css";
import { Composition } from "remotion";
import { VideoComp } from "./StoreVideo";
import { VIDEOS, FPS } from "./data";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {VIDEOS.map((video) => (
        <Composition
          key={video.id}
          id={video.id}
          component={VideoComp}
          durationInFrames={Math.ceil(video.totalSec * FPS)}
          fps={FPS}
          width={1080}
          height={1920}
          defaultProps={{ video }}
        />
      ))}

      {/* 웹 폼에서 props로 영상을 만드는 범용 컴포지션 */}
      <Composition
        id="WebVideo"
        component={VideoComp}
        durationInFrames={Math.ceil(VIDEOS[0].totalSec * FPS)}
        fps={FPS}
        width={1080}
        height={1920}
        defaultProps={{ video: VIDEOS[0] }}
        calculateMetadata={({ props }) => ({
          durationInFrames: Math.ceil(props.video.totalSec * FPS),
        })}
      />
    </>
  );
};
