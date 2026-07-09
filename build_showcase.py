# -*- coding: utf-8 -*-
"""
찬찬이 프로젝트 쇼케이스 페이지 빌더
이미지·샘플영상을 base64로 임베드한 자체완결 HTML 1개를 생성 → Artifact로 게시.
"""
import os, io, json, base64, subprocess, tempfile
from PIL import Image
import imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CUT = os.path.join(HERE, "stickers_cutout")
OUTV = os.path.join(ROOT, "my-video", "out")
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
stores = json.load(open(os.path.join(HERE, "stores.json"), encoding="utf-8"))


def png_datauri(path, width):
    im = Image.open(path).convert("RGBA")
    h = round(im.height * width / im.width)
    im = im.resize((width, h), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=82, method=6)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()


def rembg_datauri(path, width):
    from rembg import remove, new_session
    sess = new_session("u2net")
    out = remove(Image.open(path), session=sess, alpha_matting=True,
                 alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=15)
    bb = out.getbbox()
    if bb:
        out = out.crop(bb)
    h = round(out.height * width / out.width)
    out = out.resize((width, h), Image.LANCZOS)
    buf = io.BytesIO()
    out.save(buf, "WEBP", quality=82, method=6)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()


def video_datauri(path, width, crf):
    tmp = tempfile.mktemp(suffix=".mp4")
    subprocess.run([FFMPEG, "-y", "-i", path, "-vf", f"scale={width}:-2",
                    "-c:v", "libx264", "-crf", str(crf), "-preset", "veryslow",
                    "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", tmp],
                   check=True, capture_output=True)
    data = open(tmp, "rb").read()
    os.remove(tmp)
    print(f"  video {os.path.basename(path)} → {round(len(data)/1024)}KB")
    return "data:video/mp4;base64," + base64.b64encode(data).decode()


print("에셋 인코딩 중…")
hero = png_datauri(os.path.join(CUT, "main_찬찬이.png"), 560)
neuru = rembg_datauri(os.path.join(ROOT, "3D_느루(도토리캐릭터)_정면.png"), 300)
chanchan_body = png_datauri(os.path.join(CUT, "main_찬찬이.png"), 360)
grid = []
for s in stores:
    uri = png_datauri(os.path.join(CUT, f"{s['id']}_{s['name']}.png"), 210)
    grid.append((s["id"], s["name"], s["concept"], uri))
vid_intro = video_datauri(os.path.join(OUTV, "광화문점.mp4"), 480, 32)
vid_event = video_datauri(os.path.join(OUTV, "이벤트_광화문_독서의달.mp4"), 480, 32)
print("에셋 준비 완료. HTML 조립…")

COLORS = [
    ("찬찬 연두", "#BED36C", "바디 메인 · 종이/펠트 질감"),
    ("찬찬 주황", "#F17829", "배낭(등껍질) · 활력"),
    ("찬찬 베이지", "#F6DFBA", "얼굴 하단 · 배"),
    ("찬찬 노랑", "#FEE03C", "몽당연필 · 기록의 영감"),
]

grid_html = "\n".join(
    f'''<figure class="store">
      <div class="store-img"><img src="{uri}" alt="{name} 찬찬이" loading="lazy"></div>
      <figcaption><span class="num">{sid}</span>{name}</figcaption>
    </figure>''' for sid, name, concept, uri in grid)

color_html = "\n".join(
    f'''<div class="sw"><span class="chip" style="background:{hexv}"></span>
      <div><b>{nm}</b><code>{hexv}</code><small>{desc}</small></div></div>'''
    for nm, hexv, desc in COLORS)

HTML = f'''<title>찬찬이 — 점포 영상 제작 자동화</title>
<meta name="description" content="교보문고 점포사업본부 캐릭터 찬찬이와 28개 점포 캐릭터, 그리고 안내 영상 자동 제작 시스템.">
<style>
  :root{{
    --paper:#F4F6EC; --card:#FBFCF6; --ink:#3A3F24; --ink-soft:#6B7150;
    --green:#BED36C; --green-deep:#7E9A3A; --orange:#F17829; --acorn:#8A5A36;
    --beige:#F6DFBA; --line:#dfe4ce;
    --maxw:1040px;
  }}
  *{{box-sizing:border-box}}
  html{{scroll-behavior:smooth}}
  body{{
    margin:0; background:var(--paper); color:var(--ink);
    font-family:"Apple SD Gothic Neo","Pretendard",-apple-system,system-ui,"Malgun Gothic",sans-serif;
    line-height:1.6; -webkit-font-smoothing:antialiased;
  }}
  .wrap{{max-width:var(--maxw); margin:0 auto; padding:0 24px}}
  .eyebrow{{font-size:13px; letter-spacing:.18em; text-transform:uppercase; color:var(--green-deep); font-weight:800}}
  h2{{font-size:clamp(26px,4vw,38px); font-weight:800; margin:.2em 0 .4em; text-wrap:balance; letter-spacing:-.01em}}
  section{{padding:74px 0; border-top:1px dashed var(--line)}}
  .lead{{color:var(--ink-soft); font-size:18px; max-width:60ch}}

  /* HERO */
  .hero{{position:relative; overflow:hidden; padding:0; border:0;
    background:radial-gradient(120% 90% at 50% 0%, #d6e6a4 0%, #BED36C 55%, #a8c45f 100%);}}
  .hero .wrap{{display:grid; grid-template-columns:1.1fr .9fr; gap:20px; align-items:center;
    min-height:min(86vh,760px); padding-top:48px; padding-bottom:48px}}
  .hero-copy .slogan{{font-size:clamp(30px,5.2vw,56px); font-weight:800; line-height:1.18; color:#fff;
    text-wrap:balance; margin:14px 0 18px; text-shadow:0 2px 0 rgba(120,140,60,.18)}}
  .hero-copy .name{{display:inline-block; font-size:15px; font-weight:800; letter-spacing:.2em;
    color:#fff; background:rgba(58,63,36,.28); padding:7px 16px; border-radius:999px}}
  .hero-copy p{{color:#41481f; font-size:17px; max-width:42ch}}
  .hero-copy .meta{{margin-top:22px; font-size:14px; color:#4c5526; font-weight:700}}
  .hero-art{{justify-self:center; position:relative}}
  .hero-art img{{width:min(46vw,420px); display:block; filter:drop-shadow(0 26px 30px rgba(60,70,30,.28));
    animation:floatSlow 5.5s ease-in-out infinite}}
  @keyframes floatSlow{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-18px)}}}}

  /* CHARACTER */
  .duo{{display:grid; grid-template-columns:1fr 1fr; gap:22px}}
  .char{{background:var(--card); border:2px dashed var(--line); border-radius:24px; padding:26px;
    display:flex; gap:20px; align-items:center}}
  .char img{{width:130px; flex:0 0 130px}}
  .char .acorn img{{width:108px; flex-basis:108px}}
  .char h3{{margin:0 0 4px; font-size:22px}}
  .char .role{{font-size:13px; color:var(--green-deep); font-weight:800; letter-spacing:.04em}}
  .char p{{margin:.5em 0 0; font-size:15px; color:var(--ink-soft)}}
  .chips{{display:flex; flex-wrap:wrap; gap:7px; margin-top:12px}}
  .chips span{{font-size:12.5px; background:#eef3df; color:#5c7a2f; padding:4px 11px; border-radius:999px; font-weight:700}}
  .acorn .chips span{{background:#f0e3d4; color:var(--acorn)}}

  /* COLORS */
  .swatches{{display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:14px}}
  .sw{{display:flex; gap:14px; align-items:center; background:var(--card); border:1px solid var(--line); border-radius:16px; padding:14px}}
  .sw .chip{{width:46px; height:46px; border-radius:12px; flex:0 0 46px; box-shadow:inset 0 0 0 1px rgba(0,0,0,.06)}}
  .sw b{{display:block; font-size:15px}}
  .sw code{{display:block; font-size:12.5px; color:var(--ink-soft); font-variant-numeric:tabular-nums}}
  .sw small{{display:block; font-size:12px; color:var(--ink-soft); margin-top:2px}}

  /* STORE GRID */
  .grid{{display:grid; grid-template-columns:repeat(auto-fill,minmax(140px,1fr)); gap:14px}}
  .store{{margin:0; background:var(--card); border:1px solid var(--line); border-radius:18px; padding:10px 8px 12px; text-align:center; transition:transform .18s ease, box-shadow .18s ease}}
  .store:hover{{transform:translateY(-4px); box-shadow:0 12px 22px rgba(120,140,60,.14)}}
  .store-img{{aspect-ratio:1/1; display:flex; align-items:center; justify-content:center;
    background:radial-gradient(70% 70% at 50% 35%, #fff 0%, #f3f6e8 100%); border-radius:14px}}
  .store-img img{{width:84%; height:84%; object-fit:contain}}
  .store figcaption{{font-size:13.5px; font-weight:700; margin-top:8px}}
  .store .num{{display:block; font-size:11px; color:var(--green-deep); font-weight:800; letter-spacing:.08em; font-variant-numeric:tabular-nums}}

  /* SYSTEM */
  .pipe{{display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px; margin-top:6px}}
  .step{{background:var(--card); border:1px solid var(--line); border-radius:16px; padding:18px}}
  .step .k{{font-size:12px; font-weight:800; color:var(--orange); letter-spacing:.04em}}
  .step h4{{margin:6px 0 4px; font-size:16px}}
  .step p{{margin:0; font-size:13.5px; color:var(--ink-soft)}}
  .ways{{display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:14px; margin-top:26px}}
  .way{{background:var(--card); border:2px dashed var(--line); border-radius:20px; padding:20px}}
  .way h4{{margin:0 0 6px; font-size:18px}}
  .way p{{margin:0; font-size:14px; color:var(--ink-soft)}}
  .vids{{display:grid; grid-template-columns:1fr 1fr; gap:18px; margin-top:30px}}
  .vid{{background:var(--card); border:1px solid var(--line); border-radius:20px; padding:14px; text-align:center}}
  .vid video{{width:100%; max-width:280px; border-radius:14px; background:#000; display:block; margin:0 auto}}
  .vid .cap{{font-size:14px; font-weight:700; margin-top:10px}}
  .vid .sub{{font-size:12.5px; color:var(--ink-soft)}}

  footer{{padding:46px 0 70px; text-align:center; color:var(--ink-soft); font-size:13px; border-top:1px dashed var(--line)}}
  footer .acornmark{{font-size:22px}}

  @media (max-width:760px){{
    .hero .wrap{{grid-template-columns:1fr; text-align:center; min-height:auto}}
    .hero-art{{order:-1}} .hero-copy p{{margin-inline:auto}}
    .duo,.vids{{grid-template-columns:1fr}}
    .char{{flex-direction:column; text-align:center}}
  }}
  @media (prefers-reduced-motion:reduce){{
    .hero-art img{{animation:none}} html{{scroll-behavior:auto}} .store{{transition:none}}
  }}
</style>

<header class="hero">
  <div class="wrap">
    <div class="hero-copy">
      <span class="name">CHANCHANI · 찬찬이</span>
      <div class="slogan">조금 느려도 괜찮아,<br>결국엔 나만의 이야기가<br>될 테니까</div>
      <p>교보문고 점포사업본부의 아기 거북이 캐릭터. 28개 점포의 특색을 입고, 점포 안내 영상까지 스스로 만들어 냅니다.</p>
      <div class="meta">2026 · 교보문고 점포사업본부</div>
    </div>
    <div class="hero-art"><img src="{hero}" alt="찬찬이 메인 캐릭터"></div>
  </div>
</header>

<section id="character">
  <div class="wrap">
    <span class="eyebrow">The Characters</span>
    <h2>책의 숲에서 온 두 친구</h2>
    <p class="lead">속도보다 방향을, 결과보다 과정을 아끼는 찬찬이. 그리고 늘 머리 위에서 함께 세상을 바라보는 도토리, 느루.</p>
    <div class="duo" style="margin-top:26px">
      <div class="char">
        <img src="{chanchan_body}" alt="찬찬이">
        <div>
          <div class="role">아기 거북이</div>
          <h3>찬찬이</h3>
          <p>펠트 질감의 연두 바디, 등껍질을 닮은 주황 배낭, 영감을 적는 노란 몽당연필. 느릿하지만 작은 이야기를 놓치지 않는 수집가.</p>
          <div class="chips"><span>차분함</span><span>호기심</span><span>기록·독서</span></div>
        </div>
      </div>
      <div class="char acorn">
        <div class="acorn"><img src="{neuru}" alt="느루 도토리"></div>
        <div>
          <div class="role">도토리 동반자</div>
          <h3>느루</h3>
          <p>찬찬이의 머리 위에서 함께 지내는 도토리. 다리가 없어 걷진 못하지만 데구루루 잘 굴러다니죠. 모자처럼 숨었다가 쏙 등장합니다.</p>
          <div class="chips"><span>머리 위 동거</span><span>굴러서 이동</span><span>모자↔등장</span></div>
        </div>
      </div>
    </div>
    <div style="margin-top:30px">
      <span class="eyebrow">Color System</span>
      <div class="swatches" style="margin-top:14px">{color_html}</div>
    </div>
  </div>
</section>

<section id="stores">
  <div class="wrap">
    <span class="eyebrow">28 Stores</span>
    <h2>점포마다 다른 옷을 입은 찬찬이</h2>
    <p class="lead">광화문의 장군부터 창원의 벚꽃까지. 28개 교보문고 점포의 지역·역사·문화를 담은 캐릭터 시리즈.</p>
    <div class="grid" style="margin-top:26px">{grid_html}</div>
  </div>
</section>

<section id="system">
  <div class="wrap">
    <span class="eyebrow">Video Automation</span>
    <h2>내용만 입력하면, 영상이 됩니다</h2>
    <p class="lead">점포 소개·이벤트·공지·교육 영상을 데이터 한 번 입력으로 자동 제작. 무료 음성 합성과 코드 기반 렌더링으로 28편을 일관되게 양산합니다.</p>
    <div class="pipe">
      <div class="step"><div class="k">01 데이터</div><h4>점포·내용 입력</h4><p>점포 정보와 안내 문구를 폼이나 MD로 작성</p></div>
      <div class="step"><div class="k">02 음성</div><h4>무료 TTS</h4><p>edge-tts 한국어 음성 (여·남·여아·남아)</p></div>
      <div class="step"><div class="k">03 자막·캐릭터</div><h4>동기화 합성</h4><p>문장별 자막 + 움직이는 찬찬이</p></div>
      <div class="step"><div class="k">04 렌더</div><h4>Remotion 출력</h4><p>1080×1920 세로 영상으로 자동 렌더</p></div>
    </div>
    <div class="ways">
      <div class="way"><h4>웹앱</h4><p>브라우저 폼에서 선택·입력 → 즉석 1편. 목소리·배경·동작(인사·댄스·걷기·두리번) 커스터마이징.</p></div>
      <div class="way"><h4>MD 일괄</h4><p>콘텐츠 MD 한 파일 편집 → 여러 편 한 번에 양산.</p></div>
      <div class="way"><h4>Remotion Studio</h4><p>디자인을 직접 미세조정하는 코드 기반 편집.</p></div>
    </div>
    <div class="vids">
      <figure class="vid">
        <video src="{vid_intro}" controls preload="metadata" playsinline></video>
        <div class="cap">점포 소개 — 광화문점</div>
        <div class="sub">장군 콘셉트 · 인트로·본문·아웃트로</div>
      </figure>
      <figure class="vid">
        <video src="{vid_event}" controls preload="metadata" playsinline></video>
        <div class="cap">이벤트 안내 — 독서의 달</div>
        <div class="sub">유형 배지 · 기간·장소 자동 표시</div>
      </figure>
    </div>
  </div>
</section>

<footer>
  <div class="wrap">
    <div class="acornmark">🌰</div>
    <p>찬찬이와 느루가 함께 만든 점포 영상 자동화 · 2026 교보문고 점포사업본부<br>
    <small>샘플 영상의 음성은 무료 TTS(edge-tts)로 생성되었습니다. 실제 운영 시 고품질 음성·AI 모션으로 교체 가능합니다.</small></p>
  </div>
</footer>'''

out = os.path.join(HERE, "showcase.html")
open(out, "w", encoding="utf-8").write(HTML)
print(f"\n완료: {out}  ({round(len(HTML)/1024/1024,2)} MB)")
