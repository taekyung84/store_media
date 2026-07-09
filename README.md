# 찬찬이 점포 안내 영상 — 자동화 스타터 키트

교보문고 점포사업본부 캐릭터 **찬찬이**(+도토리 동반자 **느루**)를 활용한
28개 점포별 안내 영상 **하이브리드 자동화** 파이프라인입니다.

- **자동화 영역**: 대본(Claude) → 음성(Clova Voice) → AI 영상 프롬프트 생성
- **수동 영역**: 편집툴(CapCut/Premiere) 템플릿에서 최종 조립
- **캐릭터 연출**: 기존 스티커 PNG를 첫 프레임으로 한 AI image-to-video(Veo/Kling)

---

## 📁 파일 구성

| 파일 | 설명 |
| --- | --- |
| `stores.json` | 28개 점포 데이터 (점포명·콘셉트·costume_keywords·층별·운영시간·이벤트·오시는길·느루동작) |
| `generate.py` | 오케스트레이션 스크립트. stores.json → 점포별 제작 폴더 자동 생성 |
| `scripts.json` | **찬찬이 페르소나로 사전 작성한 28개 점포 내레이션 대본**. generate.py가 Claude API보다 우선 사용 (키 없이도 실제 대본 생성) |
| `프롬프트팩.md` | 대본 생성 프롬프트 + 28개 점포별 AI 영상 프롬프트 + 공통 규칙 |
| `cutout.py` | 스티커 누끼(배경 제거) 스크립트 (rembg 기반) |
| `stickers/` | 시안에서 분할한 28개 점포별 원본 PNG (라벨+카드 포함) |
| `stickers_cutout/` | 배경·라벨 제거 후 **캐릭터만 남긴 투명 PNG** (AI 영상 첫 프레임용) |
| `누끼_컨택트시트.png` | 28개 누끼 결과를 한눈에 보는 검수용 썸네일 시트 (7×4) |
| `README.md` | (이 문서) 사용법 |
| `build/` | 실행 시 생성되는 점포별 산출물 폴더 |

---

## 🚀 빠른 시작

### 1) 구조 먼저 확인 (키 없이, DRY-RUN)
```bash
cd 점포안내영상_자동화
python3 generate.py --only 001,013     # 2개 점포만 미리보기
```
→ `build/001_광화문점/` 등에 `script.txt`, `clip_prompts.txt`, `shotlist.csv` 생성.
별도 설치 불필요(파이썬 표준 라이브러리만 사용).

### 2) 실제 생성 (API 키 설정 후)
```bash
export ANTHROPIC_API_KEY="sk-ant-..."   # 대본 생성
export CLOVA_ID="..."                    # Naver Cloud CLOVA Voice
export CLOVA_SECRET="..."
# 선택: export CLOVA_SPEAKER="ndain"  CLAUDE_MODEL="claude-sonnet-4-6"

python3 generate.py                      # 28개 점포 전체 생성
```
→ 각 폴더에 문장별 `vo_01.mp3 …` 음성까지 자동 생성.

### 3) AI 캐릭터 클립 생성
각 폴더의 `clip_prompts.txt`(또는 `프롬프트팩.md`)의 프롬프트로
**Veo 3 / Kling** 등에서 image-to-video 실행.
- **입력 첫 프레임**: 해당 점포 스티커 PNG (예: `001_광화문점.png`)
- motion strength **LOW**, 4초 루프, 9:16

### 4) 편집툴에서 조립 (수동)
CapCut/Premiere 마스터 템플릿에 점포 폴더 에셋을 배치:
```
[인트로 5s]  찬찬이 로고 + 슬로건 (28편 공통 고정)
[본문]       AI클립 + vo_*.mp3 + shotlist.csv의 caption 자막 + 점포정보 그래픽
[아웃트로 5s] 점포명·지도·QR + "또 만나요" (공통 고정)
[BGM]        공통 트랙 1개 / 자막 컬러 #BED36C·#F17829 고정
```
`shotlist.csv`의 `est_sec`로 장면 길이 가이드, `vo_*.mp3` 실제 길이에 맞춰 미세조정.

---

## 🗂 점포별 제작 폴더 구조 (자동 생성)
```
build/001_광화문점/
 ├─ script.txt        # 내레이션 대본 (한 줄 = 한 자막)
 ├─ vo_01.mp3 …        # 문장별 음성 (Clova)
 ├─ clip_prompts.txt   # 장면별 AI 영상 프롬프트
 └─ shotlist.csv       # scene·narration·vo_file·est_sec·caption·clip_prompt
```

---

## ⚙️ 커스터마이즈 포인트

| 항목 | 위치 |
| --- | --- |
| 점포 정보·이벤트 수정 | `stores.json` (운영 데이터는 여기만 갱신하면 재생성) |
| 찬찬이 말투·대본 구성 | `generate.py` → `build_script_prompt()` |
| 음성 화자/속도 | 환경변수 `CLOVA_SPEAKER`(기본 ndain) / `CLOVA_SPEED` |
| 장면별 모션 연출 | `generate.py` → `build_clip_prompt()` / `NEURU_MOTION` |
| 자막·브랜드 컬러 | `generate.py` → `BRAND` 딕셔너리 |

---

## 🔁 운영 사이클 (지속 자동화)
1. 이벤트/운영시간 변경 → `stores.json` 수정
2. `python3 generate.py` 재실행 → 대본·음성 갱신
3. 변경 점포만 AI 클립 재생성(필요 시)
4. 템플릿에서 재조립 → 배포

> 인트로/아웃트로/BGM/자막 스타일을 **템플릿에 고정**해 두면, 데이터만 바꿔 28편을
> 일관된 품질로 반복 생산할 수 있습니다.

---

## 📌 참고
- 캐릭터 설정·컬러·점포 콘셉트 원본: 상위 폴더 `찬찬이_캐릭터_분석.md`
- 기존 캐릭터 에셋: 28종 스티커 시안 / 3D 정면·측면·뒷면 / 느루 / 응용동작
- TTS: Naver Cloud Platform CLOVA Voice Premium (`tts-premium/v1/tts`)
- 대본 LLM: Claude (Anthropic Messages API)
