# -*- coding: utf-8 -*-
"""
공용 모듈: 내레이션 음성(mp3) + 자막 타이밍 생성
무료 TTS = Microsoft edge-tts (키 불필요, 고품질 한국어 신경망 음성).
한국어 음성은 여성(SunHi)/남성(InJoon) 2종이라, 남아·여아는 피치 시프트로 구현.
edge-tts 사용 불가 시 macOS `say`(Yuna)로 자동 폴백.
"""
import os, wave, shutil, subprocess, tempfile, asyncio
import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
INTRO, OUTRO, GAP = 2.6, 2.6, 0.45

# 목소리 카테고리 → (음성 엔진/이름, rate/option, pitch)
VOICES = {
    "여성": ("ko-KR-SunHiNeural", "+0%", "+0Hz"),
    "남성": ("ko-KR-InJoonNeural", "+0%", "+0Hz"),
    "여아": ("ko-KR-SunHiNeural", "+12%", "+38Hz"),
    "남아": ("ko-KR-InJoonNeural", "+14%", "+42Hz"),
    "[Google AI] 찬찬이": ("gemini-Puck", "+0%", "+0Hz"),
    "[Google AI] 느루": ("gemini-Kore", "+0%", "+0Hz"),
}
VOICE_LABELS = {
    "여성": "여성",
    "남성": "남성",
    "여아": "여자아이",
    "남아": "남자아이",
    "[Google AI] 찬찬이": "Google AI 찬찬이 (고품질 고정)",
    "[Google AI] 느루": "Google AI 느루 (고품질 고정)",
}


def _wav_dur(p):
    with wave.open(p, "rb") as w:
        return w.getnframes() / float(w.getframerate())


def _run(a):
    subprocess.run(a, check=True, capture_output=True)


def _edge_synth(text, out_mp3, voice, rate, pitch):
    import edge_tts
    async def go():
        await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(out_mp3)
    asyncio.run(go())


def _gemini_synth(text, out_raw):
    from google import genai
    from google.genai import types
    api_key = os.environ.get("GOOGLE_AI_API_KEY", "")
    if not api_key:
        raise RuntimeError("GOOGLE_AI_API_KEY가 없습니다.")
    client = genai.Client(api_key=api_key)
    res = client.models.generate_content(
        model="gemini-3.1-flash-tts-preview",
        contents=text,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck")
                )
            )
        )
    )
    audio_data = None
    for part in res.candidates[0].content.parts:
        if hasattr(part, "inline_data") and part.inline_data:
            audio_data = part.inline_data.data
            break
    if not audio_data:
        raise RuntimeError("Gemini 오디오 데이터를 받지 못했습니다.")
    with open(out_raw, "wb") as f:
        f.write(audio_data)


def _synth_to_wav(text, wav_path, voice_key, work, idx):
    """문장 → wav. Gemini / edge-tts 우선, 실패 시 macOS say 폴백."""
    voice, rate, pitch = VOICES.get(voice_key, VOICES["여성"])
    raw = os.path.join(work, f"raw_{idx}")
    if voice_key.startswith("[Google AI]"):
        try:
            pcm = raw + ".pcm"
            _gemini_synth(text, pcm)
            _run([FFMPEG, "-y", "-f", "s16le", "-ar", "24000", "-ac", "1", "-i", pcm, "-ar", "44100", "-ac", "1", wav_path])
            return "Google AI (Gemini)"
        except Exception as e:
            print(f"⚠️ Gemini TTS 실패, edge-tts 폴백: {e}")
            voice = "ko-KR-SunHiNeural"
    try:
        mp3 = raw + ".mp3"
        _edge_synth(text, mp3, voice, rate, pitch)
        _run([FFMPEG, "-y", "-i", mp3, "-ar", "44100", "-ac", "1", wav_path])
        return "edge-tts"
    except Exception:
        aiff = raw + ".aiff"
        _run(["say", "-v", "Yuna", "-r", "175", "-o", aiff, text])
        _run([FFMPEG, "-y", "-i", aiff, "-ar", "44100", "-ac", "1", wav_path])
        return "say"


def make_narration(sents, out_mp3, voice_key="여성", intro=INTRO, outro=OUTRO, gap=GAP):
    """문장 리스트 → 통합 mp3. (captions, totalSec, introSec, outroSec, engine) 반환."""
    work = tempfile.mkdtemp(prefix="narr_")
    engine = "edge"
    try:
        durs, wavs = [], []
        for i, s in enumerate(sents):
            wv = os.path.join(work, f"{i}.wav")
            engine = _synth_to_wav(s, wv, voice_key, work, i)
            durs.append(_wav_dur(wv))
            wavs.append(wv)

        sil_i = os.path.join(work, "si.wav"); sil_o = os.path.join(work, "so.wav"); silg = os.path.join(work, "g.wav")
        for path, d in [(sil_i, intro), (sil_o, outro), (silg, gap)]:
            _run([FFMPEG, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", f"{d}", path])

        seq = [sil_i]
        for wv in wavs:
            seq += [wv, silg]
        seq.append(sil_o)
        listf = os.path.join(work, "list.txt")
        open(listf, "w").write("\n".join(f"file '{p}'" for p in seq))
        os.makedirs(os.path.dirname(out_mp3), exist_ok=True)
        _run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", listf,
              "-ar", "44100", "-ac", "2", "-b:a", "160k", out_mp3])

        seg = [d + gap for d in durs]
        caps = [{"text": s,
                 "fromMs": round((intro + sum(seg[:i])) * 1000),
                 "toMs": round((intro + sum(seg[:i + 1])) * 1000)}
                for i, s in enumerate(sents)]
        total = round(intro + sum(seg) + outro, 3)
        return caps, total, intro, outro, engine
    finally:
        shutil.rmtree(work, ignore_errors=True)
