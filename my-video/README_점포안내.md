# 찬찬이 점포 안내 영상 — Remotion 운영본

로컬 Remotion(코드 기반)으로 28개 점포 안내 영상을 데이터 주도로 양산하는 프로젝트입니다.
누끼 캐릭터 + 내레이션 음성 + 자막을 동일 템플릿에 데이터만 바꿔 렌더합니다.

## 구조
```
my-video/
 ├ public/
 │   ├ characters/char_001.png …   누끼 캐릭터 28종
 │   └ audio/001.mp3 …             점포별 통합 내레이션 28종
 ├ src/
 │   ├ data.ts                     점포 메타+자막 타이밍 (자동 생성, 직접 수정 금지)
 │   ├ StoreVideo.tsx              영상 템플릿 (인트로+본문+자막+아웃트로)
 │   └ Root.tsx                    28개 컴포지션 자동 등록 (Store-001 … Store-028)
 ├ render-all.mjs                  28편 일괄 렌더 헬퍼
 └ out/                            렌더 결과 mp4
```

## 사용법

### 미리보기 (Remotion Studio)
```bash
cd my-video && npm run dev
```
브라우저에서 Store-001 ~ Store-028 컴포지션을 실시간 확인·수정.

### 1편 렌더
```bash
npx remotion render Store-001 out/광화문점.mp4
```

### 28편 일괄 렌더
```bash
npm run render-all              # 전체
node render-all.mjs 001 013     # 특정 점포만
```

## 데이터 갱신 사이클
1. 점포 정보/이벤트 변경 → `../점포안내영상_자동화/stores.json` 또는 `scripts.json` 수정
2. 에셋 재생성:
   ```bash
   cd ../점포안내영상_자동화 && python3 prepare_remotion.py        # 전체
   python3 prepare_remotion.py 001                                # 특정 점포
   ```
   → public/audio·characters + src/data.ts 자동 갱신
3. `npm run render-all` 로 재렌더

## 사양
- 해상도 1080×1920 (세로, 모바일·사이니지) · 30fps · 점포당 약 26~33초
- 폰트: Noto Sans KR (@remotion/google-fonts)
- 브랜드 컬러: 연두 #BED36C / 주황 #F17829

## 운영 전환 포인트 (데모 → 실제)
| 요소 | 현재(데모) | 실제 운영 |
| --- | --- | --- |
| 음성 | macOS `say`(Yuna) | **Clova Voice mp3**로 `public/audio/*.mp3` 교체 (파일명 동일하면 코드 수정 불필요) |
| 캐릭터 | 누끼 정지 PNG + 플로팅 | **Veo/Kling AI 클립**(mp4)로 교체 시 `<Img>`를 `<Video>`로 변경 |
| 배경/효과 | 단색 그라데이션 | 모션그래픽·BGM·트랜지션 추가 |

> 음성을 Clova로 바꿀 때는 mp3의 문장별 길이가 달라지므로, 자막 싱크를 위해
> `prepare_remotion.py`의 음성 생성 부분만 Clova 호출로 교체하면 timings가 자동 재계산됩니다.
