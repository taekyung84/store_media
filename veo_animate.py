# -*- coding: utf-8 -*-
"""
Veo 3.1 Image-to-Video 캐릭터 애니메이션 모듈
=============================================
캐릭터 PNG 이미지를 Google Veo API로 보내 자연스러운 움직임의
MP4 클립으로 변환합니다.

사용법:
    from veo_animate import animate_character
    mp4_path = animate_character("characters/char_001.png", motion="인사", output_dir="public/animated")
"""
import os, time, pathlib, shutil

HERE = os.path.dirname(os.path.abspath(__file__))

# .env 파일에서 API 키 로드
def _load_env():
    env_path = os.path.join(HERE, ".env")
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

_load_env()

# 배경색 hex → 영어 색상 설명 변환
HEX_TO_COLOR_DESC = {
    "#bed36c": "soft lime green",
    "#cde08a": "soft lime green",
    "#a8c45f": "fresh green",
    "#f17829": "warm orange",
    "#ffd9b8": "warm peach orange",
    "#f3a368": "golden orange",
    "#cfe8f5": "light sky blue",
    "#9cc9e0": "soft blue",
    "#f3e6cf": "light beige",
    "#e3cda3": "warm tan",
    "#f7d9e3": "light pink",
    "#e8a9c0": "soft rose pink",
}


def _bg_prompt_fragment(bg_colors: dict) -> str:
    """배경 테마 색상을 Veo 프롬프트 문구로 변환합니다. (단색 Solid Color)"""
    if not bg_colors:
        return "on a clean, flat solid pastel green background (color hex #BED36C)"
    
    hex_code = bg_colors.get("solid") or bg_colors.get("top") or "#BED36C"
    color_desc = HEX_TO_COLOR_DESC.get(hex_code.lower())
    if color_desc:
        return f"on a clean, flat solid {color_desc} background (color hex {hex_code})"
    else:
        return f"on a clean, flat solid background of color hex {hex_code}"


# 동작 타입별 Veo 프롬프트 매핑 (배경은 동적으로 삽입)
MOTION_PROMPTS = {
    "인사": (
        "The cute illustrated character waves hello cheerfully, "
        "tilting side to side with a warm greeting gesture. "
    ),
    "소개": (
        "The cute illustrated character gestures warmly with open hands towards the side, "
        "as if presenting or introducing information to the audience. "
    ),
    "박수": (
        "The cute illustrated character claps hands joyfully and bounces slightly with excitement. "
    ),
    "깜짝": (
        "The cute illustrated character widens eyes in pleasant surprise, "
        "raising hands near face with a cute gasp gesture. "
    ),
    "댄스": (
        "The cute illustrated character dances happily with bouncy movements, "
        "swaying left and right with joyful energy. "
    ),
    "걷기": (
        "The cute illustrated character walks slowly from side to side, "
        "with gentle stepping motion and slight body sway. "
    ),
    "두리번": (
        "The cute illustrated character looks around curiously, "
        "turning head left and right as if searching for something. "
    ),
    "통통": (
        "The cute illustrated character bounces up and down playfully, "
        "with a squash-and-stretch cartoon-like effect. "
    ),
    "기본": (
        "The cute illustrated character gently floats up and down, "
        "with a subtle breathing motion and slight sway. "
    ),
}

PROMPT_SUFFIX = (
    "Camera stays perfectly still, "
    "keep the entire character safely inside the video frame without clipping hands, feet, or head, "
    "smooth natural looping animation, "
    "maintain exact original character design and proportions, "
    "the character seamlessly returns to its starting pose by the end of the clip for perfect looping."
)


def generate_motion_prompt_from_content(client, lines_text: str, bg_desc: str = "") -> str:
    """
    Gemini LLM을 활용하여 내레이션 내용 맥락을 분석하고,
    캐릭터가 수행할 가장 자연스럽고 적절한 2D 애니메이션 동작 프롬프트를 자동 생성합니다.
    배경색 설명이 포함됩니다.
    """
    sys_instruction = (
        "You are an expert AI video animator. "
        "Analyze the provided Korean announcement narration text, and write a concise 1-2 sentence English prompt for Veo Image-to-Video. "
        "The prompt MUST describe how the cute 2D illustrated character acts out the feeling or gesture matching the narration (e.g. waving hello, pointing to an event sign, clapping happily, looking around curiously, or floating gently). "
        "The character MUST perform a seamless looping motion that naturally returns to its starting pose by the end of the clip. "
        f"The background MUST be described as: '{bg_desc}'. Do NOT use black, dark, or transparent background. "
        "Always end the prompt with: 'Camera stays perfectly still, smooth natural looping animation, maintain exact original character design and proportions.'"
    )
    try:
        res = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Narration text:\n{lines_text}",
            config={"system_instruction": sys_instruction}
        )
        prompt_text = res.text.strip()
        if prompt_text:
            print(f"  🧠 Gemini가 내용 분석으로 자동 생성한 동작 프롬프트:\n     \"{prompt_text}\"")
            return prompt_text
    except Exception as e:
        print(f"  ⚠️ 내용 분석 프롬프트 생성 실패, 기본 인사 모션 적용: {e}")
    base = MOTION_PROMPTS["인사"]
    return f"{base}{bg_desc}. {PROMPT_SUFFIX}"


def animate_character(
    char_image_path: str,
    motion: str = "기본",
    lines_text: str = "",
    bg_colors: dict = None,
    output_dir: str = ".",
    duration_sec: int = 8,
    timeout_sec: int = 180,
) -> str:
    """
    캐릭터 PNG를 Veo API로 애니메이션 MP4로 변환합니다.

    Args:
        char_image_path: 캐릭터 PNG 이미지 절대 경로
        motion: 동작 타입 (인사/소개/박수/깜짝/댄스/걷기/두리번/통통/기본)
        lines_text: 내레이션 텍스트 (내용 기반 자동 동작 결정용)
        bg_colors: 배경 테마 색상 dict {"top": "#hex", "bot": "#hex"}
        output_dir: 출력 디렉터리 절대 경로
        duration_sec: 생성 영상 길이(초)
        timeout_sec: API 응답 대기 최대 시간(초)

    Returns:
        생성된 MP4 파일 절대 경로

    Raises:
        RuntimeError: API 호출 실패 또는 타임아웃
    """
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        raise RuntimeError(
            "google-genai 패키지가 필요합니다.\n"
            "pip install google-genai 로 설치해 주세요."
        )

    api_key = os.environ.get("GOOGLE_AI_API_KEY", "")
    if not api_key:
        raise RuntimeError(
            "GOOGLE_AI_API_KEY 환경변수가 설정되지 않았습니다.\n"
            ".env 파일을 확인해 주세요."
        )

    # 캐시 확인: 동일 캐릭터+모션+배경 조합으로 최근 생성된 영상이 있으면 재활용
    char_basename = os.path.basename(char_image_path).replace(".png", "")
    hex_code = (bg_colors.get("solid") or bg_colors.get("top") or "bed36c").replace("#", "")
    cache_key = f"cache_anim_{char_basename}_{motion}_{hex_code}.mp4"
    cache_path = os.path.join(output_dir, cache_key)
    if os.path.exists(cache_path) and (time.time() - os.path.getmtime(cache_path) < 86400 * 7): # 7일 이내 캐시
        print(f"  ⚡ 캐시된 AI 캐릭터 영상 재사용: {cache_key}")
        return cache_path

    # 클라이언트 초기화
    client = genai.Client(api_key=api_key)

    # 배경색 프롬프트 조각 생성
    bg_desc = _bg_prompt_fragment(bg_colors)

    # 내용 기반 자동 분석 동작 프롬프트 생성
    if lines_text and lines_text.strip():
        prompt = generate_motion_prompt_from_content(client, lines_text, bg_desc=bg_desc)
    else:
        base = MOTION_PROMPTS.get(motion, MOTION_PROMPTS["기본"])
        prompt = f"{base}{bg_desc}. {PROMPT_SUFFIX}"

    # 이미지 로드
    if not os.path.exists(char_image_path):
        raise FileNotFoundError(f"캐릭터 이미지를 찾을 수 없습니다: {char_image_path}")

    print(f"  🤖 Veo API 호출 중... (동작: {motion})")
    print(f"     이미지: {os.path.basename(char_image_path)}")

    # 이미지 파일 읽기
    with open(char_image_path, "rb") as f:
        image_bytes = f.read()

    image = types.Image(
        image_bytes=image_bytes,
        mime_type="image/png",
    )

    # 비디오 생성 요청
    try:
        operation = client.models.generate_videos(
            model="veo-3.1-generate-preview",
            prompt=prompt,
            image=image,
            config=types.GenerateVideosConfig(
                aspect_ratio="9:16",
                number_of_videos=1,
            ),
        )
    except Exception as e:
        raise RuntimeError(f"Veo API 요청 실패: {e}")

    # 생성 완료 대기
    print(f"  ⏳ 영상 생성 대기 중... (최대 {timeout_sec}초)")
    start = time.time()
    while not operation.done:
        elapsed = time.time() - start
        if elapsed > timeout_sec:
            raise RuntimeError(
                f"Veo 영상 생성 타임아웃 ({timeout_sec}초 초과). "
                "네트워크 상태를 확인하고 다시 시도해 주세요."
            )
        print(f"     ... {int(elapsed)}초 경과", end="\r")
        time.sleep(10)
        try:
            operation = client.operations.get(operation)
        except Exception as e:
            raise RuntimeError(f"Veo 상태 확인 실패: {e}")

    # 결과 저장
    if not operation.response or not operation.response.generated_videos:
        raise RuntimeError("Veo API가 영상을 생성하지 못했습니다. 프롬프트를 수정하거나 다시 시도해 주세요.")

    os.makedirs(output_dir, exist_ok=True)
    stamp = time.strftime("%y%m%d%H%M%S")
    out_name = f"animated_{stamp}.mp4"
    out_path = os.path.join(output_dir, out_name)

    generated_video = operation.response.generated_videos[0]
    # SDK 버전에 따라 다른 저장 방식 시도
    try:
        client.files.download(file=generated_video.video)
        generated_video.video.save(out_path)
    except AttributeError:
        # 대체 저장 방식
        try:
            with open(out_path, "wb") as f:
                f.write(generated_video.video.video_bytes)
        except Exception:
            # 최종 폴백: video 객체에서 직접 데이터 추출
            video_data = generated_video.video
            if hasattr(video_data, "read"):
                with open(out_path, "wb") as f:
                    f.write(video_data.read())
            else:
                raise RuntimeError("Veo 영상 저장 실패. SDK 버전을 확인해 주세요.")

    elapsed_total = round(time.time() - start, 1)
    print(f"  ✅ AI 캐릭터 영상 생성 완료! ({elapsed_total}초)")
    print(f"     → {out_path}")

    # 캐시 복사 저장
    try:
        shutil.copy(out_path, cache_path)
    except Exception:
        pass

    return out_path


if __name__ == "__main__":
    # 단독 테스트
    import sys
    img = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(HERE), "my-video", "public", "characters", "char_main.png"
    )
    motion = sys.argv[2] if len(sys.argv) > 2 else "인사"
    out = os.path.join(os.path.dirname(HERE), "my-video", "public", "animated")
    result = animate_character(img, motion=motion, output_dir=out)
    print(f"\n결과: {result}")
