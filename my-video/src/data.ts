// 자동 생성됨 (build_from_md.py). 직접 수정하지 마세요. 원본: 점포_영상콘텐츠.md
export type Caption = { text: string; fromMs: number; toMs: number };
export type Info = { label: string; value: string };
export type Video = {
  id: string; title: string; type: string; storeId: string; storeName: string;
  neuru: string; char: string; audio: string; info: Info[];
  introSec: number; outroSec: number; totalSec: number; captions: Caption[];
};

export const FPS = 30;
export const VIDEOS: Video[] = [
  {
    "id": "v001",
    "title": "광화문점 점포 소개",
    "type": "소개",
    "storeId": "001",
    "storeName": "광화문점",
    "neuru": "appear",
    "char": "characters/char_001.png",
    "audio": "audio/v001.mp3",
    "info": [
      {
        "label": "운영시간",
        "value": "09:30-22:00"
      },
      {
        "label": "오시는길",
        "value": "5호선 광화문역 4번 출구 직결"
      }
    ],
    "introSec": 2.6,
    "outroSec": 2.6,
    "totalSec": 33.016,
    "captions": [
      {
        "text": "조금 느려도 괜찮아요, 광화문점에 오신 걸 환영해요.",
        "fromMs": 2600,
        "toMs": 6831
      },
      {
        "text": "오늘은 늠름한 장군이 되어 여러분을 맞이할게요.",
        "fromMs": 6831,
        "toMs": 10565
      },
      {
        "text": "1층에선 따끈한 신간과 베스트셀러를 만나보세요.",
        "fromMs": 10565,
        "toMs": 14716
      },
      {
        "text": "2층 인문·문학 서가엔 깊은 이야기가 가득하답니다.",
        "fromMs": 14716,
        "toMs": 19099
      },
      {
        "text": "지금은 6월 독서의 달 스탬프 투어가 열리고 있어요.",
        "fromMs": 19099,
        "toMs": 23008
      },
      {
        "text": "5호선 광화문역 4번 출구에서 바로 이어져요.",
        "fromMs": 23008,
        "toMs": 26741
      },
      {
        "text": "느루와 함께, 당신만의 이야기를 기다릴게요.",
        "fromMs": 26741,
        "toMs": 30416
      }
    ]
  },
  {
    "id": "v002",
    "title": "은평점 점포 소개",
    "type": "소개",
    "storeId": "002",
    "storeName": "은평점",
    "neuru": "hat",
    "char": "characters/char_002.png",
    "audio": "audio/v002.mp3",
    "info": [
      {
        "label": "운영시간",
        "value": "10:00-22:00"
      },
      {
        "label": "오시는길",
        "value": "3호선·6호선 연신내역 인근"
      }
    ],
    "introSec": 2.6,
    "outroSec": 2.6,
    "totalSec": 29.319,
    "captions": [
      {
        "text": "천천히 오세요, 은평점에서 인사드려요.",
        "fromMs": 2600,
        "toMs": 6021
      },
      {
        "text": "단정한 선비 차림으로 여러분을 맞이할게요.",
        "fromMs": 6021,
        "toMs": 9376
      },
      {
        "text": "1층엔 신간과 베스트셀러가 기다리고 있어요.",
        "fromMs": 9376,
        "toMs": 13109
      },
      {
        "text": "2층은 아이들과 함께하는 아동·학습 서가예요.",
        "fromMs": 13109,
        "toMs": 16959
      },
      {
        "text": "지금은 전통문화 도서전이 열리고 있답니다.",
        "fromMs": 16959,
        "toMs": 20310
      },
      {
        "text": "3호선과 6호선 연신내역에서 가까워요.",
        "fromMs": 20310,
        "toMs": 23811
      },
      {
        "text": "느루와 함께 포근한 하루를 선물할게요.",
        "fromMs": 23811,
        "toMs": 26719
      }
    ]
  },
  {
    "id": "v003",
    "title": "합정점 점포 소개",
    "type": "소개",
    "storeId": "003",
    "storeName": "합정점",
    "neuru": "appear",
    "char": "characters/char_003.png",
    "audio": "audio/v003.mp3",
    "info": [
      {
        "label": "운영시간",
        "value": "10:00-22:00"
      },
      {
        "label": "오시는길",
        "value": "2호선·6호선 합정역 연결"
      }
    ],
    "introSec": 2.6,
    "outroSec": 2.6,
    "totalSec": 28.256,
    "captions": [
      {
        "text": "조금 느려도 괜찮아요, 합정점이에요.",
        "fromMs": 2600,
        "toMs": 5868
      },
      {
        "text": "오늘은 붓을 든 화가가 되어볼게요.",
        "fromMs": 5868,
        "toMs": 8707
      },
      {
        "text": "1층엔 신간과 예술·디자인 책이 가득해요.",
        "fromMs": 8707,
        "toMs": 12638
      },
      {
        "text": "2층 문학·인문 서가도 둘러보세요.",
        "fromMs": 12638,
        "toMs": 15848
      },
      {
        "text": "지금은 아트북 페어와 원화 전시가 열려요.",
        "fromMs": 15848,
        "toMs": 18991
      },
      {
        "text": "2호선과 6호선 합정역과 바로 연결돼요.",
        "fromMs": 18991,
        "toMs": 22596
      },
      {
        "text": "느루와 함께 영감 가득한 하루 보내요.",
        "fromMs": 22596,
        "toMs": 25656
      }
    ]
  },
  {
    "id": "v004",
    "title": "건대스타시티점 점포 소개",
    "type": "소개",
    "storeId": "004",
    "storeName": "건대스타시티점",
    "neuru": "appear",
    "char": "characters/char_004.png",
    "audio": "audio/v004.mp3",
    "info": [
      {
        "label": "운영시간",
        "value": "10:30-22:00"
      },
      {
        "label": "오시는길",
        "value": "2호선·7호선 건대입구역 스타시티몰 연결"
      }
    ],
    "introSec": 2.6,
    "outroSec": 2.6,
    "totalSec": 29.7,
    "captions": [
      {
        "text": "반가워요, 건대스타시티점에 오셨군요.",
        "fromMs": 2600,
        "toMs": 6129
      },
      {
        "text": "대학생 친구처럼 산뜻하게 맞이할게요.",
        "fromMs": 6129,
        "toMs": 9565
      },
      {
        "text": "지하층엔 모든 분야의 책이 모여 있어요.",
        "fromMs": 9565,
        "toMs": 12696
      },
      {
        "text": "B1 학습·수험서 코너도 든든하게 채웠어요.",
        "fromMs": 12696,
        "toMs": 16503
      },
      {
        "text": "지금은 대학생 추천도서전이 열리고 있어요.",
        "fromMs": 16503,
        "toMs": 19982
      },
      {
        "text": "2호선·7호선 건대입구역 스타시티몰과 이어져요.",
        "fromMs": 19982,
        "toMs": 24133
      },
      {
        "text": "느루와 함께 당신의 내일을 응원할게요.",
        "fromMs": 24133,
        "toMs": 27100
      }
    ]
  },
  {
    "id": "v005",
    "title": "동대문점 점포 소개",
    "type": "소개",
    "storeId": "005",
    "storeName": "동대문점",
    "neuru": "hat",
    "char": "characters/char_005.png",
    "audio": "audio/v005.mp3",
    "info": [
      {
        "label": "운영시간",
        "value": "10:00-22:00"
      },
      {
        "label": "오시는길",
        "value": "1호선·4호선 동대문역 인근"
      }
    ],
    "introSec": 2.6,
    "outroSec": 2.6,
    "totalSec": 27.761,
    "captions": [
      {
        "text": "어서 오세요, 동대문점이에요.",
        "fromMs": 2600,
        "toMs": 5323
      },
      {
        "text": "고운 한복을 입고 여러분을 맞이할게요.",
        "fromMs": 5323,
        "toMs": 8550
      },
      {
        "text": "1층엔 신간과 베스트셀러가 기다려요.",
        "fromMs": 8550,
        "toMs": 11911
      },
      {
        "text": "2층은 문학과 실용서가 가득한 서가예요.",
        "fromMs": 11911,
        "toMs": 15319
      },
      {
        "text": "지금은 한복·전통 도서전이 열리고 있어요.",
        "fromMs": 15319,
        "toMs": 18890
      },
      {
        "text": "1호선과 4호선 동대문역에서 가까워요.",
        "fromMs": 18890,
        "toMs": 22391
      },
      {
        "text": "느루와 함께 따뜻한 이야기를 나눠요.",
        "fromMs": 22391,
        "toMs": 25161
      }
    ]
  },
  {
    "id": "v006",
    "title": "수유점 점포 소개",
    "type": "소개",
    "storeId": "006",
    "storeName": "수유점",
    "neuru": "hat",
    "char": "characters/char_006.png",
    "audio": "audio/v006.mp3",
    "info": [
      {
        "label": "운영시간",
        "value": "10:00-22:00"
      },
      {
        "label": "오시는길",
        "value": "4호선 수유역 인근"
      }
    ],
    "introSec": 2.6,
    "outroSec": 2.6,
    "totalSec": 27.657,
    "captions": [
      {
        "text": "조금 느려도 괜찮아요, 수유점이에요.",
        "fromMs": 2600,
        "toMs": 5693
      },
      {
        "text": "오늘은 산을 오르는 등산객이 되어볼게요.",
        "fromMs": 5693,
        "toMs": 8974
      },
      {
        "text": "1층엔 신간과 실용·여행 책이 가득해요.",
        "fromMs": 8974,
        "toMs": 12672
      },
      {
        "text": "지금은 북한산 트레킹 도서전이 열려요.",
        "fromMs": 12672,
        "toMs": 15931
      },
      {
        "text": "건강과 아웃도어 책도 함께 추천드려요.",
        "fromMs": 15931,
        "toMs": 19263
      },
      {
        "text": "4호선 수유역에서 천천히 찾아오세요.",
        "fromMs": 19263,
        "toMs": 22497
      },
      {
        "text": "느루와 함께 푸른 하루를 걸어가요.",
        "fromMs": 22497,
        "toMs": 25057
      }
    ]
  },
  {
    "id": "v007",
    "title": "청량리점 점포 소개",
    "type": "소개",
    "storeId": "007",
    "storeName": "청량리점",
    "neuru": "appear",
    "char": "characters/char_007.png",
    "audio": "audio/v007.mp3",
    "info": [
      {
        "label": "운영시간",
        "value": "10:00-22:00"
      },
      {
        "label": "오시는길",
        "value": "1호선·경의중앙선 청량리역 연결"
      }
    ],
    "introSec": 2.6,
    "outroSec": 2.6,
    "totalSec": 28.073,
    "captions": [
      {
        "text": "천천히 오세요, 청량리점에서 인사드려요.",
        "fromMs": 2600,
        "toMs": 6207
      },
      {
        "text": "오늘은 역무원이 되어 길을 안내할게요.",
        "fromMs": 6207,
        "toMs": 9267
      },
      {
        "text": "1층엔 신간과 여행 책이 기다리고 있어요.",
        "fromMs": 9267,
        "toMs": 12675
      },
      {
        "text": "2층은 문학과 실용서로 가득하답니다.",
        "fromMs": 12675,
        "toMs": 15851
      },
      {
        "text": "지금은 기차여행 테마 도서전이 열려요.",
        "fromMs": 15851,
        "toMs": 18982
      },
      {
        "text": "1호선·경의중앙선 청량리역과 이어져요.",
        "fromMs": 18982,
        "toMs": 22831
      },
      {
        "text": "느루와 함께 설레는 여행을 떠나봐요.",
        "fromMs": 22831,
        "toMs": 25473
      }
    ]
  },
  {
    "id": "v008",
    "title": "목동점 점포 소개",
    "type": "소개",
    "storeId": "008",
    "storeName": "목동점",
    "neuru": "appear",
    "char": "characters/char_008.png",
    "audio": "audio/v008.mp3",
    "info": [
      {
        "label": "운영시간",
        "value": "10:00-22:00"
      },
      {
        "label": "오시는길",
        "value": "5호선 오목교역 인근"
      }
    ],
    "introSec": 2.6,
    "outroSec": 2.6,
    "totalSec": 27.633,
    "captions": [
      {
        "text": "조금 느려도 괜찮아요, 목동점이에요.",
        "fromMs": 2600,
        "toMs": 5821
      },
      {
        "text": "동그란 안경을 쓰고 차분히 맞이할게요.",
        "fromMs": 5821,
        "toMs": 9152
      },
      {
        "text": "지하층엔 학습·참고서가 가득 모여 있어요.",
        "fromMs": 9152,
        "toMs": 12746
      },
      {
        "text": "1층은 신간과 아동 책으로 채웠답니다.",
        "fromMs": 12746,
        "toMs": 16096
      },
      {
        "text": "지금은 학년별 추천도서전이 열리고 있어요.",
        "fromMs": 16096,
        "toMs": 19599
      },
      {
        "text": "5호선 오목교역에서 가깝답니다.",
        "fromMs": 19599,
        "toMs": 22531
      },
      {
        "text": "느루와 함께 차근차근 배워가요.",
        "fromMs": 22531,
        "toMs": 25033
      }
    ]
  },
  {
    "id": "v009",
    "title": "영등포점 점포 소개",
    "type": "소개",
    "storeId": "009",
    "storeName": "영등포점",
    "neuru": "appear",
    "char": "characters/char_009.png",
    "audio": "audio/v009.mp3",
    "info": [
      {
        "label": "운영시간",
        "value": "10:30-22:00"
      },
      {
        "label": "오시는길",
        "value": "1호선 영등포역 백화점 연결"
      }
    ],
    "introSec": 2.6,
    "outroSec": 2.6,
    "totalSec": 26.121,
    "captions": [
      {
        "text": "어서 오세요, 영등포점이에요.",
        "fromMs": 2600,
        "toMs": 5323
      },
      {
        "text": "양손 가득 즐거운 마음으로 맞이할게요.",
        "fromMs": 5323,
        "toMs": 8510
      },
      {
        "text": "지하층엔 모든 분야의 책이 모여 있어요.",
        "fromMs": 8510,
        "toMs": 11641
      },
      {
        "text": "지금은 라이프스타일 도서전이 열려요.",
        "fromMs": 11641,
        "toMs": 14598
      },
      {
        "text": "예쁜 굿즈와 문구도 함께 만나보세요.",
        "fromMs": 14598,
        "toMs": 17692
      },
      {
        "text": "1호선 영등포역 백화점과 바로 이어져요.",
        "fromMs": 17692,
        "toMs": 21123
      },
      {
        "text": "느루와 함께 설레는 하루 보내요.",
        "fromMs": 21123,
        "toMs": 23521
      }
    ]
  },
  {
    "id": "v010",
    "title": "가든파이브점 점포 소개",
    "type": "소개",
    "storeId": "010",
    "storeName": "가든파이브점",
    "neuru": "appear",
    "char": "characters/char_010.png",
    "audio": "audio/v010.mp3",
    "info": [
      {
        "label": "운영시간",
        "value": "10:30-22:00"
      },
      {
        "label": "오시는길",
        "value": "8호선 장지역 가든파이브 연결"
      }
    ],
    "introSec": 2.6,
    "outroSec": 2.6,
    "totalSec": 27.4,
    "captions": [
      {
        "text": "조금 느려도 괜찮아요, 가든파이브점이에요.",
        "fromMs": 2600,
        "toMs": 6123
      },
      {
        "text": "작은 화분을 안고 푸르게 맞이할게요.",
        "fromMs": 6123,
        "toMs": 9056
      },
      {
        "text": "1층엔 신간과 실용·라이프 책이 가득해요.",
        "fromMs": 9056,
        "toMs": 12952
      },
      {
        "text": "지금은 가드닝과 식물 도서전이 열려요.",
        "fromMs": 12952,
        "toMs": 16095
      },
      {
        "text": "홈 인테리어 책도 함께 추천드려요.",
        "fromMs": 16095,
        "toMs": 18997
      },
      {
        "text": "8호선 장지역 가든파이브와 이어져요.",
        "fromMs": 18997,
        "toMs": 22089
      },
      {
        "text": "느루와 함께 싱그러운 하루 가꿔봐요.",
        "fromMs": 22089,
        "toMs": 24800
      }
    ]
  },
  {
    "id": "v011",
    "title": "강남점 점포 소개",
    "type": "소개",
    "storeId": "011",
    "storeName": "강남점",
    "neuru": "hat",
    "char": "characters/char_011.png",
    "audio": "audio/v011.mp3",
    "info": [
      {
        "label": "운영시간",
        "value": "10:30-22:00"
      },
      {
        "label": "오시는길",
        "value": "신분당선·2호선 강남역 직결"
      }
    ],
    "introSec": 2.6,
    "outroSec": 2.6,
    "totalSec": 28.506,
    "captions": [
      {
        "text": "반가워요, 강남점에 오셨군요.",
        "fromMs": 2600,
        "toMs": 5549
      },
      {
        "text": "세련된 차림으로 산뜻하게 맞이할게요.",
        "fromMs": 5549,
        "toMs": 8712
      },
      {
        "text": "지하 1층엔 모든 분야의 책이 모여 있어요.",
        "fromMs": 8712,
        "toMs": 12017
      },
      {
        "text": "지하 2층은 외서와 전문서로 가득해요.",
        "fromMs": 12017,
        "toMs": 15148
      },
      {
        "text": "지금은 자기계발·경제경영 도서전이 열려요.",
        "fromMs": 15148,
        "toMs": 19126
      },
      {
        "text": "신분당선·2호선 강남역과 바로 이어져요.",
        "fromMs": 19126,
        "toMs": 22788
      },
      {
        "text": "느루와 함께 당신의 성장을 응원할게요.",
        "fromMs": 22788,
        "toMs": 25906
      }
    ]
  },
  {
    "id": "v012",
    "title": "원그로브점 점포 소개",
    "type": "소개",
    "storeId": "012",
    "storeName": "원그로브점",
    "neuru": "appear",
    "char": "characters/char_012.png",
    "audio": "audio/v012.mp3",
    "info": [
      {
        "label": "운영시간",
        "value": "10:00-21:00"
      },
      {
        "label": "오시는길",
        "value": "원그로브 빌딩 내 위치"
      }
    ],
    "introSec": 2.6,
    "outroSec": 2.6,
    "totalSec": 27.134,
    "captions": [
      {
        "text": "천천히 오세요, 원그로브점이에요.",
        "fromMs": 2600,
        "toMs": 5534
      },
      {
        "text": "커피 한 잔과 함께 다정히 맞이할게요.",
        "fromMs": 5534,
        "toMs": 8904
      },
      {
        "text": "1층엔 신간과 경제경영 책이 가득해요.",
        "fromMs": 8904,
        "toMs": 12486
      },
      {
        "text": "지금은 직장인 점심 독서 이벤트가 열려요.",
        "fromMs": 12486,
        "toMs": 15930
      },
      {
        "text": "바쁜 하루 속 작은 쉼표를 선물할게요.",
        "fromMs": 15930,
        "toMs": 19065
      },
      {
        "text": "원그로브 빌딩 안에서 만나요.",
        "fromMs": 19065,
        "toMs": 21614
      },
      {
        "text": "느루와 함께 잠시 쉬어가도 괜찮아요.",
        "fromMs": 21614,
        "toMs": 24534
      }
    ]
  },
  {
    "id": "v013",
    "title": "잠실점 점포 소개",
    "type": "소개",
    "storeId": "013",
    "storeName": "잠실점",
    "neuru": "appear",
    "char": "characters/char_013.png",
    "audio": "audio/v013.mp3",
    "info": [
      {
        "label": "운영시간",
        "value": "10:30-22:00"
      },
      {
        "label": "오시는길",
        "value": "2호선·8호선 잠실역 롯데몰 연결"
      }
    ],
    "introSec": 2.6,
    "outroSec": 2.6,
    "totalSec": 27.472,
    "captions": [
      {
        "text": "조금 느려도 괜찮아요, 잠실점이에요.",
        "fromMs": 2600,
        "toMs": 5914
      },
      {
        "text": "곰돌이 머리띠를 하고 신나게 맞이할게요.",
        "fromMs": 5914,
        "toMs": 9326
      },
      {
        "text": "지하층엔 모든 분야의 책이 모여 있어요.",
        "fromMs": 9326,
        "toMs": 12457
      },
      {
        "text": "지금은 가족 나들이 도서전이 열리고 있어요.",
        "fromMs": 12457,
        "toMs": 15716
      },
      {
        "text": "아이와 함께 볼 그림책도 가득하답니다.",
        "fromMs": 15716,
        "toMs": 18776
      },
      {
        "text": "2호선·8호선 잠실역 롯데몰과 이어져요.",
        "fromMs": 18776,
        "toMs": 22416
      },
      {
        "text": "느루와 함께 즐거운 하루 보내요.",
        "fromMs": 22416,
        "toMs": 24872
      }
    ]
  },
  {
    "id": "v014",
    "title": "광교점 점포 소개",
    "type": "소개",
    "storeId": "014",
    "storeName": "광교점",
    "neuru": "appear",
    "char": "characters/char_014.png",
    "audio": "audio/v014.mp3",
    "info": [
      {
        "label": "운영시간",
        "value": "10:00-22:00"
      },
      {
        "label": "오시는길",
        "value": "신분당선 광교중앙역 인근"
      }
    ],
    "introSec": 2.6,
    "outroSec": 2.6,
    "totalSec": 27.453,
    "captions": [
      {
        "text": "천천히 오세요, 광교점에서 인사드려요.",
        "fromMs": 2600,
        "toMs": 6021
      },
      {
        "text": "피크닉 바구니를 들고 가볍게 맞이할게요.",
        "fromMs": 6021,
        "toMs": 9345
      },
      {
        "text": "1층엔 신간과 라이프 책이 가득해요.",
        "fromMs": 9345,
        "toMs": 12556
      },
      {
        "text": "2층은 아동과 문학 서가로 채웠답니다.",
        "fromMs": 12556,
        "toMs": 15766
      },
      {
        "text": "지금은 피크닉 독서 이벤트가 열려요.",
        "fromMs": 15766,
        "toMs": 18770
      },
      {
        "text": "신분당선 광교중앙역에서 가까워요.",
        "fromMs": 18770,
        "toMs": 22072
      },
      {
        "text": "느루와 함께 호숫가의 여유를 즐겨요.",
        "fromMs": 22072,
        "toMs": 24853
      }
    ]
  },
  {
    "id": "v015",
    "title": "판교점 점포 소개",
    "type": "소개",
    "storeId": "015",
    "storeName": "판교점",
    "neuru": "appear",
    "char": "characters/char_015.png",
    "audio": "audio/v015.mp3",
    "info": [
      {
        "label": "운영시간",
        "value": "10:00-22:00"
      },
      {
        "label": "오시는길",
        "value": "신분당선 판교역 인근"
      }
    ],
    "introSec": 2.6,
    "outroSec": 2.6,
    "totalSec": 26.972,
    "captions": [
      {
        "text": "반가워요, 판교점에 오셨군요.",
        "fromMs": 2600,
        "toMs": 5467
      },
      {
        "text": "노트북을 든 개발자처럼 맞이할게요.",
        "fromMs": 5467,
        "toMs": 8515
      },
      {
        "text": "1층엔 신간과 IT·경제경영 책이 가득해요.",
        "fromMs": 8515,
        "toMs": 12249
      },
      {
        "text": "지금은 IT·개발 도서전이 열리고 있어요.",
        "fromMs": 12249,
        "toMs": 15240
      },
      {
        "text": "스타트업과 트렌드 책도 추천드려요.",
        "fromMs": 15240,
        "toMs": 18369
      },
      {
        "text": "신분당선 판교역에서 가깝답니다.",
        "fromMs": 18369,
        "toMs": 21579
      },
      {
        "text": "느루와 함께 새로운 내일을 만들어가요.",
        "fromMs": 21579,
        "toMs": 24372
      }
    ]
  },
  {
    "id": "v016",
    "title": "평촌점 점포 소개",
    "type": "소개",
    "storeId": "016",
    "storeName": "평촌점",
    "neuru": "hat",
    "char": "characters/char_016.png",
    "audio": "audio/v016.mp3",
    "info": [
      {
        "label": "운영시간",
        "value": "10:00-22:00"
      },
      {
        "label": "오시는길",
        "value": "4호선 범계역 인근"
      }
    ],
    "introSec": 2.6,
    "outroSec": 2.6,
    "totalSec": 26.013,
    "captions": [
      {
        "text": "조금 느려도 괜찮아요, 평촌점이에요.",
        "fromMs": 2600,
        "toMs": 5856
      },
      {
        "text": "고글을 쓰고 활기차게 맞이할게요.",
        "fromMs": 5856,
        "toMs": 8607
      },
      {
        "text": "지하층엔 모든 분야의 책이 모여 있어요.",
        "fromMs": 8607,
        "toMs": 11738
      },
      {
        "text": "지금은 스포츠·건강 도서전이 열려요.",
        "fromMs": 11738,
        "toMs": 15134
      },
      {
        "text": "취미와 레저 책도 함께 추천드려요.",
        "fromMs": 15134,
        "toMs": 18141
      },
      {
        "text": "4호선 범계역에서 가깝답니다.",
        "fromMs": 18141,
        "toMs": 20980
      },
      {
        "text": "느루와 함께 신나는 하루 보내요.",
        "fromMs": 20980,
        "toMs": 23413
      }
    ]
  },
  {
    "id": "v017",
    "title": "송도점 점포 소개",
    "type": "소개",
    "storeId": "017",
    "storeName": "송도점",
    "neuru": "appear",
    "char": "characters/char_017.png",
    "audio": "audio/v017.mp3",
    "info": [
      {
        "label": "운영시간",
        "value": "10:00-22:00"
      },
      {
        "label": "오시는길",
        "value": "인천1호선 센트럴파크역 인근"
      }
    ],
    "introSec": 2.6,
    "outroSec": 2.6,
    "totalSec": 27.827,
    "captions": [
      {
        "text": "천천히 오세요, 송도점에서 인사드려요.",
        "fromMs": 2600,
        "toMs": 5998
      },
      {
        "text": "노를 든 채 바다처럼 시원하게 맞이할게요.",
        "fromMs": 5998,
        "toMs": 9545
      },
      {
        "text": "1층엔 신간과 라이프 책이 가득해요.",
        "fromMs": 9545,
        "toMs": 12756
      },
      {
        "text": "2층은 아동과 문학 서가로 채웠답니다.",
        "fromMs": 12756,
        "toMs": 15966
      },
      {
        "text": "지금은 바다·여행 도서전이 열리고 있어요.",
        "fromMs": 15966,
        "toMs": 19386
      },
      {
        "text": "인천1호선 센트럴파크역에서 가까워요.",
        "fromMs": 19386,
        "toMs": 22829
      },
      {
        "text": "느루와 함께 시원한 하루 보내요.",
        "fromMs": 22829,
        "toMs": 25227
      }
    ]
  },
  {
    "id": "v018",
    "title": "인천점 점포 소개",
    "type": "소개",
    "storeId": "018",
    "storeName": "인천점",
    "neuru": "appear",
    "char": "characters/char_018.png",
    "audio": "audio/v018.mp3",
    "info": [
      {
        "label": "운영시간",
        "value": "10:00-22:00"
      },
      {
        "label": "오시는길",
        "value": "공항철도 인천공항 연결"
      }
    ],
    "introSec": 2.6,
    "outroSec": 2.6,
    "totalSec": 26.022,
    "captions": [
      {
        "text": "반가워요, 인천점에 오셨군요.",
        "fromMs": 2600,
        "toMs": 5467
      },
      {
        "text": "파일럿이 되어 멋지게 맞이할게요.",
        "fromMs": 5467,
        "toMs": 8211
      },
      {
        "text": "1층엔 신간과 여행·외서가 가득해요.",
        "fromMs": 8211,
        "toMs": 11700
      },
      {
        "text": "지금은 세계여행 도서전이 열리고 있어요.",
        "fromMs": 11700,
        "toMs": 14727
      },
      {
        "text": "외국어와 여행 책도 함께 추천드려요.",
        "fromMs": 14727,
        "toMs": 17891
      },
      {
        "text": "공항철도 인천공항과 이어져요.",
        "fromMs": 17891,
        "toMs": 20653
      },
      {
        "text": "느루와 함께 넓은 세상으로 떠나봐요.",
        "fromMs": 20653,
        "toMs": 23422
      }
    ]
  },
  {
    "id": "v019",
    "title": "일산점 점포 소개",
    "type": "소개",
    "storeId": "019",
    "storeName": "일산점",
    "neuru": "appear",
    "char": "characters/char_019.png",
    "audio": "audio/v019.mp3",
    "info": [
      {
        "label": "운영시간",
        "value": "10:00-22:00"
      },
      {
        "label": "오시는길",
        "value": "3호선 정발산역 인근"
      }
    ],
    "introSec": 2.6,
    "outroSec": 2.6,
    "totalSec": 26.687,
    "captions": [
      {
        "text": "조금 느려도 괜찮아요, 일산점이에요.",
        "fromMs": 2600,
        "toMs": 5821
      },
      {
        "text": "꽃 화관을 쓰고 화사하게 맞이할게요.",
        "fromMs": 5821,
        "toMs": 8950
      },
      {
        "text": "1층엔 신간과 라이프 책이 가득해요.",
        "fromMs": 8950,
        "toMs": 12161
      },
      {
        "text": "2층은 아동과 문학 서가로 채웠답니다.",
        "fromMs": 12161,
        "toMs": 15371
      },
      {
        "text": "지금은 꽃축제 연계 도서전이 열려요.",
        "fromMs": 15371,
        "toMs": 18444
      },
      {
        "text": "3호선 정발산역에서 가깝답니다.",
        "fromMs": 18444,
        "toMs": 21503
      },
      {
        "text": "느루와 함께 향기로운 하루 보내요.",
        "fromMs": 21503,
        "toMs": 24087
      }
    ]
  },
  {
    "id": "v020",
    "title": "세종점 점포 소개",
    "type": "소개",
    "storeId": "020",
    "storeName": "세종점",
    "neuru": "hat",
    "char": "characters/char_020.png",
    "audio": "audio/v020.mp3",
    "info": [
      {
        "label": "운영시간",
        "value": "10:00-22:00"
      },
      {
        "label": "오시는길",
        "value": "세종시 중심상업지구 위치"
      }
    ],
    "introSec": 2.6,
    "outroSec": 2.6,
    "totalSec": 27.084,
    "captions": [
      {
        "text": "천천히 오세요, 세종점에서 인사드려요.",
        "fromMs": 2600,
        "toMs": 6021
      },
      {
        "text": "오늘은 책을 든 임금님이 되어볼게요.",
        "fromMs": 6021,
        "toMs": 9035
      },
      {
        "text": "1층엔 신간과 인문 책이 가득해요.",
        "fromMs": 9035,
        "toMs": 12118
      },
      {
        "text": "2층은 아동과 학습 서가로 채웠답니다.",
        "fromMs": 12118,
        "toMs": 15305
      },
      {
        "text": "지금은 한글·세종대왕 도서전이 열려요.",
        "fromMs": 15305,
        "toMs": 18806
      },
      {
        "text": "세종시 중심상업지구에서 만나요.",
        "fromMs": 18806,
        "toMs": 21854
      },
      {
        "text": "느루와 함께 깊은 이야기를 나눠요.",
        "fromMs": 21854,
        "toMs": 24484
      }
    ]
  },
  {
    "id": "v021",
    "title": "천안점 점포 소개",
    "type": "소개",
    "storeId": "021",
    "storeName": "천안점",
    "neuru": "appear",
    "char": "characters/char_021.png",
    "audio": "audio/v021.mp3",
    "info": [
      {
        "label": "운영시간",
        "value": "10:00-22:00"
      },
      {
        "label": "오시는길",
        "value": "1호선·장항선 천안역 인근"
      }
    ],
    "introSec": 2.6,
    "outroSec": 2.6,
    "totalSec": 26.369,
    "captions": [
      {
        "text": "어서 오세요, 천안점이에요.",
        "fromMs": 2600,
        "toMs": 5126
      },
      {
        "text": "고소한 호두과자 옷을 입고 맞이할게요.",
        "fromMs": 5126,
        "toMs": 8434
      },
      {
        "text": "1층엔 신간과 실용서가 가득해요.",
        "fromMs": 8434,
        "toMs": 11505
      },
      {
        "text": "2층은 아동과 문학 서가로 채웠답니다.",
        "fromMs": 11505,
        "toMs": 14716
      },
      {
        "text": "지금은 지역 특산 연계 이벤트가 열려요.",
        "fromMs": 14716,
        "toMs": 17847
      },
      {
        "text": "1호선·장항선 천안역에서 가까워요.",
        "fromMs": 17847,
        "toMs": 21301
      },
      {
        "text": "느루와 함께 정겨운 하루 보내요.",
        "fromMs": 21301,
        "toMs": 23769
      }
    ]
  },
  {
    "id": "v022",
    "title": "대전점 점포 소개",
    "type": "소개",
    "storeId": "022",
    "storeName": "대전점",
    "neuru": "appear",
    "char": "characters/char_022.png",
    "audio": "audio/v022.mp3",
    "info": [
      {
        "label": "운영시간",
        "value": "10:30-22:00"
      },
      {
        "label": "오시는길",
        "value": "1호선 대전시청역 인근"
      }
    ],
    "introSec": 2.6,
    "outroSec": 2.6,
    "totalSec": 27.317,
    "captions": [
      {
        "text": "조금 느려도 괜찮아요, 대전점이에요.",
        "fromMs": 2600,
        "toMs": 5821
      },
      {
        "text": "요리사 모자를 쓰고 달콤하게 맞이할게요.",
        "fromMs": 5821,
        "toMs": 9287
      },
      {
        "text": "지하층엔 모든 분야의 책이 모여 있어요.",
        "fromMs": 9287,
        "toMs": 12418
      },
      {
        "text": "지금은 요리·베이킹 도서전이 열려요.",
        "fromMs": 12418,
        "toMs": 15664
      },
      {
        "text": "지역 빵집과 함께하는 행사도 준비했어요.",
        "fromMs": 15664,
        "toMs": 18980
      },
      {
        "text": "1호선 대전시청역에서 가깝답니다.",
        "fromMs": 18980,
        "toMs": 22180
      },
      {
        "text": "느루와 함께 달콤한 하루 보내요.",
        "fromMs": 22180,
        "toMs": 24717
      }
    ]
  },
  {
    "id": "v023",
    "title": "대구점 점포 소개",
    "type": "소개",
    "storeId": "023",
    "storeName": "대구점",
    "neuru": "appear",
    "char": "characters/char_023.png",
    "audio": "audio/v023.mp3",
    "info": [
      {
        "label": "운영시간",
        "value": "10:30-22:00"
      },
      {
        "label": "오시는길",
        "value": "2호선 반월당역 인근"
      }
    ],
    "introSec": 2.6,
    "outroSec": 2.6,
    "totalSec": 27.324,
    "captions": [
      {
        "text": "천천히 오세요, 대구점에서 인사드려요.",
        "fromMs": 2600,
        "toMs": 5952
      },
      {
        "text": "돋보기를 든 탐정이 되어 맞이할게요.",
        "fromMs": 5952,
        "toMs": 9143
      },
      {
        "text": "지하 1층엔 모든 분야의 책이 모여 있어요.",
        "fromMs": 9143,
        "toMs": 12448
      },
      {
        "text": "지하 2층은 학습과 전문서로 가득해요.",
        "fromMs": 12448,
        "toMs": 15684
      },
      {
        "text": "지금은 추리·미스터리 도서전이 열려요.",
        "fromMs": 15684,
        "toMs": 18953
      },
      {
        "text": "2호선 반월당역에서 가깝답니다.",
        "fromMs": 18953,
        "toMs": 21966
      },
      {
        "text": "느루와 함께 숨은 이야기를 찾아봐요.",
        "fromMs": 21966,
        "toMs": 24724
      }
    ]
  },
  {
    "id": "v024",
    "title": "칠곡점 점포 소개",
    "type": "소개",
    "storeId": "024",
    "storeName": "칠곡점",
    "neuru": "hat",
    "char": "characters/char_024.png",
    "audio": "audio/v024.mp3",
    "info": [
      {
        "label": "운영시간",
        "value": "10:00-22:00"
      },
      {
        "label": "오시는길",
        "value": "칠곡 중심상가 위치"
      }
    ],
    "introSec": 2.6,
    "outroSec": 2.6,
    "totalSec": 26.099,
    "captions": [
      {
        "text": "조금 느려도 괜찮아요, 칠곡점이에요.",
        "fromMs": 2600,
        "toMs": 5891
      },
      {
        "text": "헬멧을 쓰고 씩씩하게 맞이할게요.",
        "fromMs": 5891,
        "toMs": 9006
      },
      {
        "text": "1층엔 신간과 아동 책이 가득해요.",
        "fromMs": 9006,
        "toMs": 12100
      },
      {
        "text": "지금은 가족 자전거 나들이 이벤트가 열려요.",
        "fromMs": 12100,
        "toMs": 15487
      },
      {
        "text": "아이와 함께 볼 그림책도 가득하답니다.",
        "fromMs": 15487,
        "toMs": 18546
      },
      {
        "text": "칠곡 중심상가에서 만나요.",
        "fromMs": 18546,
        "toMs": 21159
      },
      {
        "text": "느루와 함께 신나게 달려봐요.",
        "fromMs": 21159,
        "toMs": 23499
      }
    ]
  },
  {
    "id": "v025",
    "title": "부산점 점포 소개",
    "type": "소개",
    "storeId": "025",
    "storeName": "부산점",
    "neuru": "appear",
    "char": "characters/char_025.png",
    "audio": "audio/v025.mp3",
    "info": [
      {
        "label": "운영시간",
        "value": "10:30-22:00"
      },
      {
        "label": "오시는길",
        "value": "1호선 부산역 인근"
      }
    ],
    "introSec": 2.6,
    "outroSec": 2.6,
    "totalSec": 26.589,
    "captions": [
      {
        "text": "어서 오세요, 부산점이에요.",
        "fromMs": 2600,
        "toMs": 5161
      },
      {
        "text": "선장이 되어 망원경으로 여러분을 찾았어요.",
        "fromMs": 5161,
        "toMs": 8754
      },
      {
        "text": "지하층엔 모든 분야의 책이 모여 있어요.",
        "fromMs": 8754,
        "toMs": 11885
      },
      {
        "text": "지금은 바다·여행 도서전이 열리고 있어요.",
        "fromMs": 11885,
        "toMs": 15305
      },
      {
        "text": "부산을 담은 로컬 기획전도 준비했어요.",
        "fromMs": 15305,
        "toMs": 18543
      },
      {
        "text": "1호선 부산역에서 가깝답니다.",
        "fromMs": 18543,
        "toMs": 21312
      },
      {
        "text": "느루와 함께 넓은 바다로 떠나봐요.",
        "fromMs": 21312,
        "toMs": 23989
      }
    ]
  },
  {
    "id": "v026",
    "title": "센텀시티점 점포 소개",
    "type": "소개",
    "storeId": "026",
    "storeName": "센텀시티점",
    "neuru": "appear",
    "char": "characters/char_026.png",
    "audio": "audio/v026.mp3",
    "info": [
      {
        "label": "운영시간",
        "value": "10:30-22:00"
      },
      {
        "label": "오시는길",
        "value": "2호선 센텀시티역 백화점 연결"
      }
    ],
    "introSec": 2.6,
    "outroSec": 2.6,
    "totalSec": 27.514,
    "captions": [
      {
        "text": "천천히 오세요, 센텀시티점이에요.",
        "fromMs": 2600,
        "toMs": 5812
      },
      {
        "text": "영화 감독이 되어 멋지게 맞이할게요.",
        "fromMs": 5812,
        "toMs": 8790
      },
      {
        "text": "지하층엔 모든 분야의 책이 모여 있어요.",
        "fromMs": 8790,
        "toMs": 11921
      },
      {
        "text": "지금은 영화·영상 도서전이 열리고 있어요.",
        "fromMs": 11921,
        "toMs": 15457
      },
      {
        "text": "영화제와 함께하는 기획전도 준비했어요.",
        "fromMs": 15457,
        "toMs": 18737
      },
      {
        "text": "2호선 센텀시티역 백화점과 이어져요.",
        "fromMs": 18737,
        "toMs": 22075
      },
      {
        "text": "느루와 함께 한 편의 이야기를 즐겨요.",
        "fromMs": 22075,
        "toMs": 24914
      }
    ]
  },
  {
    "id": "v027",
    "title": "울산점 점포 소개",
    "type": "소개",
    "storeId": "027",
    "storeName": "울산점",
    "neuru": "hat",
    "char": "characters/char_027.png",
    "audio": "audio/v027.mp3",
    "info": [
      {
        "label": "운영시간",
        "value": "10:00-22:00"
      },
      {
        "label": "오시는길",
        "value": "울산 중심상업지구 위치"
      }
    ],
    "introSec": 2.6,
    "outroSec": 2.6,
    "totalSec": 26.055,
    "captions": [
      {
        "text": "반가워요, 울산점에 오셨군요.",
        "fromMs": 2600,
        "toMs": 5467
      },
      {
        "text": "안전모를 쓰고 든든하게 맞이할게요.",
        "fromMs": 5467,
        "toMs": 8562
      },
      {
        "text": "1층엔 신간과 실용서가 가득해요.",
        "fromMs": 8562,
        "toMs": 11633
      },
      {
        "text": "2층은 아동과 학습 서가로 채웠답니다.",
        "fromMs": 11633,
        "toMs": 14821
      },
      {
        "text": "지금은 과학·공학 도서전이 열려요.",
        "fromMs": 14821,
        "toMs": 17916
      },
      {
        "text": "울산 중심상업지구에서 만나요.",
        "fromMs": 17916,
        "toMs": 20743
      },
      {
        "text": "느루와 함께 단단한 하루 만들어가요.",
        "fromMs": 20743,
        "toMs": 23455
      }
    ]
  },
  {
    "id": "v028",
    "title": "창원점 점포 소개",
    "type": "소개",
    "storeId": "028",
    "storeName": "창원점",
    "neuru": "appear",
    "char": "characters/char_028.png",
    "audio": "audio/v028.mp3",
    "info": [
      {
        "label": "운영시간",
        "value": "10:00-22:00"
      },
      {
        "label": "오시는길",
        "value": "창원 중심상가 위치"
      }
    ],
    "introSec": 2.6,
    "outroSec": 2.6,
    "totalSec": 27.146,
    "captions": [
      {
        "text": "조금 느려도 괜찮아요, 창원점이에요.",
        "fromMs": 2600,
        "toMs": 5844
      },
      {
        "text": "꽃모자를 쓰고 봄처럼 화사하게 맞이할게요.",
        "fromMs": 5844,
        "toMs": 9449
      },
      {
        "text": "1층엔 신간과 라이프 책이 가득해요.",
        "fromMs": 9449,
        "toMs": 12660
      },
      {
        "text": "2층은 아동과 문학 서가로 채웠답니다.",
        "fromMs": 12660,
        "toMs": 15871
      },
      {
        "text": "지금은 벚꽃축제 연계 도서전이 열려요.",
        "fromMs": 15871,
        "toMs": 19129
      },
      {
        "text": "창원 중심상가에서 만나요.",
        "fromMs": 19129,
        "toMs": 21730
      },
      {
        "text": "느루와 함께 꽃길 같은 하루 보내요.",
        "fromMs": 21730,
        "toMs": 24546
      }
    ]
  },
  {
    "id": "v029",
    "title": "광화문점 독서의 달 스탬프 투어",
    "type": "이벤트",
    "storeId": "001",
    "storeName": "광화문점",
    "neuru": "appear",
    "char": "characters/char_001.png",
    "audio": "audio/v029.mp3",
    "info": [
      {
        "label": "기간",
        "value": "2026.06.01 ~ 06.30"
      },
      {
        "label": "장소",
        "value": "1층 이벤트 존"
      }
    ],
    "introSec": 2.6,
    "outroSec": 2.6,
    "totalSec": 23.927,
    "captions": [
      {
        "text": "조금 느려도 괜찮아요, 찬찬이예요.",
        "fromMs": 2600,
        "toMs": 5705
      },
      {
        "text": "6월 한 달, 독서의 달 스탬프 투어가 열려요.",
        "fromMs": 5705,
        "toMs": 9519
      },
      {
        "text": "책을 읽고 스탬프를 모아보세요.",
        "fromMs": 9519,
        "toMs": 12445
      },
      {
        "text": "다 모으면 특별한 굿즈를 드린답니다.",
        "fromMs": 12445,
        "toMs": 15521
      },
      {
        "text": "1층 이벤트 존에서 천천히 참여해요.",
        "fromMs": 15521,
        "toMs": 18860
      },
      {
        "text": "느루와 함께 기다리고 있을게요!",
        "fromMs": 18860,
        "toMs": 21327
      }
    ]
  },
  {
    "id": "v030",
    "title": "잠실점 가족 그림책 페스티벌",
    "type": "이벤트",
    "storeId": "013",
    "storeName": "잠실점",
    "neuru": "appear",
    "char": "characters/char_013.png",
    "audio": "audio/v030.mp3",
    "info": [
      {
        "label": "기간",
        "value": "2026.07.12 ~ 07.20"
      },
      {
        "label": "장소",
        "value": "지하 1층 아동 코너"
      }
    ],
    "introSec": 2.6,
    "outroSec": 2.6,
    "totalSec": 23.109,
    "captions": [
      {
        "text": "안녕하세요, 잠실점 찬찬이예요.",
        "fromMs": 2600,
        "toMs": 5753
      },
      {
        "text": "온 가족이 즐기는 그림책 페스티벌이 열려요.",
        "fromMs": 5753,
        "toMs": 9277
      },
      {
        "text": "작가님과 함께하는 낭독회도 준비했어요.",
        "fromMs": 9277,
        "toMs": 12582
      },
      {
        "text": "아이와 손잡고 놀러 오세요.",
        "fromMs": 12582,
        "toMs": 14841
      },
      {
        "text": "지하 1층 아동 코너에서 만나요.",
        "fromMs": 14841,
        "toMs": 17577
      },
      {
        "text": "느루도 신나서 폴짝이고 있답니다!",
        "fromMs": 17577,
        "toMs": 20509
      }
    ]
  },
  {
    "id": "v031",
    "title": "도서관 회원카드 만들기 안내",
    "type": "교육",
    "storeId": "008",
    "storeName": "목동점",
    "neuru": "hat",
    "char": "characters/char_008.png",
    "audio": "audio/v031.mp3",
    "info": [
      {
        "label": "문의",
        "value": "고객센터 1599-XXXX"
      }
    ],
    "introSec": 2.6,
    "outroSec": 2.6,
    "totalSec": 27.126,
    "captions": [
      {
        "text": "조금 느려도 괜찮아요, 찬찬이가 알려드릴게요.",
        "fromMs": 2600,
        "toMs": 6367
      },
      {
        "text": "오늘은 회원카드 만드는 법을 소개할게요.",
        "fromMs": 6367,
        "toMs": 9520
      },
      {
        "text": "1층 안내데스크에서 신청서를 작성해요.",
        "fromMs": 9520,
        "toMs": 13113
      },
      {
        "text": "신분증만 있으면 바로 발급된답니다.",
        "fromMs": 13113,
        "toMs": 16521
      },
      {
        "text": "카드가 있으면 적립과 할인이 가능해요.",
        "fromMs": 16521,
        "toMs": 19670
      },
      {
        "text": "천천히 따라오시면 어렵지 않아요.",
        "fromMs": 19670,
        "toMs": 22395
      },
      {
        "text": "느루와 함께 도와드릴게요!",
        "fromMs": 22395,
        "toMs": 24526
      }
    ]
  }
];
