# -*- coding: utf-8 -*-
"""품목별 수수료 통계 생성. 페이지의 '비용' 섹션에 주입할 데이터.

입력: data/processed/fees.csv, site/src/data/items.json
출력: site/src/data/fees.json

지자체마다 금액이 몇 배씩 다르므로 단일 값을 못 박지 않는다. 중앙값과
사분위 범위, 표본 지역 수를 함께 낸다. 근거로 쓸 지역별 샘플도 남긴다.
"""
import csv
import io
import json
import os
import re
import statistics
import sys
from collections import defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEES = os.path.join(ROOT, "data", "processed", "fees.csv")
ITEMS = os.path.join(ROOT, "site", "src", "data", "items.json")
OUT = os.path.join(ROOT, "site", "src", "data", "fees.json")

# 원본 표기가 우리 품목명과 다른 경우. 왼쪽이 원본 토큰, 오른쪽이 우리 slug.
EXTRA_ALIAS = {
    "카펫": "reogeu", "카페트": "reogeu", "카펫트": "reogeu",
    "전기밥솥": "bapsot", "압력밥솥": "bapsot",
    "전기레인지": "gaseureinji", "가스렌지": "gaseureinji",
    "디지털피아노": "jeonjapiano", "전자올겐": "jeonjapiano",
    "장농": "jangrong",
    "헬맷": "helmet",
    # 별칭이지만 수수료 축이 다른 것. 식기세척기는 4,000~14,000, 건조기는 0~2,000이라
    # 한 중앙값에 섞으면 건조기 페이지가 세척기 요금표를 보여 준다 (판단 39).
    "식기세척기": None, "팩스": None, "팩시밀리": None, "팩스기": None, "팩스기기": None,   # 하남시 표기. 오타는 별칭이 아니라 여기서 접는다 (판단 33, 36)
    "진공청소기": "cheongsogi",
    "봉제인형": "inhyeong",
    "화장다이": "hwajangdae", "경대": "hwajangdae",
    "서랍": "seorapjang", "수납장": "seorapjang",
    "건조대": "ppalraegeonjodae", "빨래걸이": "ppalraegeonjodae",
    "자토바이": None,   # 자전거 오탐 방지용 자리표시
    # 19차 잔여 판정(docs/50)에서 별칭을 붙이자마자 걸린 둘.
    # 고무 페이지는 수수료 행이 0건인데 '풍선'이 광고용 에어간판을 끌어왔다.
    # 의정부 '에어간판, 풍선인형(업소용)', 강북구 '입간판(풍선형)',
    # 남동구 '광고용 풍선대야'. 우리가 말하는 고무 풍선이 아니다 (판단 47).
    "풍선": None,
    # 마네킹은 인형과 등재 수도 값도 자릿수가 다르다. 붙이자 인형 중앙값이
    # 2,000(11곳) -> 3,000(25곳), 최대 3,000 -> 7,500으로 뛰었다 (판단 39, 42).
    "마네킹": None,
    # 실측 20차 판정(docs/51)에서 붙이자마자 걸린 둘.
    # '흙'이 접미 일치로 부산 동구 '(돌옥흙) 1인용 15,000'을 끌어왔다.
    # 흙침대, 돌침대 행이라 화분 최대가 4,500에서 15,000이 됐다 (판단 70).
    "흙": None, "분갈이 흙": None, "정원 흙": None, "화단 흙": None,
    # 라켓은 골프채와 답이 같고 값만 다르다. 화성시 500원, 광진구 배드민턴
    # 500원이 들어와 골프채 중앙값이 1,500(8곳)에서 1,000(11곳)으로 내려갔다.
    # 별칭으로 받되 과금은 가른다 (판단 42).
    "라켓": None, "배드민턴채": None, "테니스채": None,
    # 스피커 페이지 별칭. 오디오(전축)는 세트라 값이 스피커 낱개의 두 배 가까이 된다.
    # 섞으면 스피커 중앙값이 2,000에서 3,500으로 뛴다 (docs/39, 판단 39).
    "오디오": None, "전축": None, "오디오세트": None, "앰프": None,
    # --- 실측 22차 별칭(docs/57). 붙이기 전에 행을 펴서 열 건이 걸렸다 (판단 70).
    # 프린터(8곳, 2,500~7,500)에 복사기를 붙이면 39행이 들어온다. 광진구
    # '복사기(복합기, 영업용프린터) 10,000'처럼 영업용이 섞여 등재 수가
    # 자릿수로 다르다 (판단 39). 검색은 받되 과금은 가른다.
    "복사기": None, "복합기": None, "스캐너": None,
    # 건조기(13곳)에 의류관리기를 붙이면 스타일러 행이 들어온다. 옷을 말리는
    # 물건과 옷을 터는 물건이고 값도 5,000~8,000으로 다르다 (판단 42).
    "의류관리기": None, "스타일러": None, "의류 건조기": None,
    # 공유기는 수수료 행이 0건인데 '셋톱박스'가 남동구 1행을 끌어온다.
    # 본체가 0이면 요금표가 통째로 별칭 것이 된다 (판단 47).
    "셋톱박스": None, "셋탑박스": None,
    # 나뭇가지도 0건인데 '잔디'가 강북구 '인조잔디'를 끌어온다. 인조잔디는
    # 깎아 낸 풀이 아니라 깔아 둔 매트다.
    "잔디": None,
    # 정수기(24곳)에 제빙기를 붙이면 광진구 2행이 섞인다. 얼음정수기가 아니라
    # 업소용 제빙기 값이다.
    "제빙기": None,
    # 연고는 0건인데 '파스'가 양천구 '소파스툴' 2행을 접미로 먹는다.
    "파스": None,
    # 우산 페이지에 '우산 비닐'을 붙이면 남동구 '우산 비닐꽂이'가 걸린다.
    # 비닐꽂이는 우산이 아니라 현관에 두는 통이다.
    "우산 비닐": None, "우산비닐": None,
    # 박스 페이지(골판지)는 수수료 축이 없다. 접미 일치가 아이스박스, 콘솔박스,
    # 공간박스를 끌어온다 (docs/39).
    "박스": None, "상자": None, "택배박스": None, "택배상자": None, "종이박스": None,
    "종이상자": None, "골판지": None, "골판지상자": None, "라면박스": None,
    "피자박스": None, "치킨박스": None,
    # 대형폐기물 품목표의 '조명', '형광등'은 램프가 아니라 등기구다. 램프는
    # 형광등 수거함으로 가는 물건이라 애초에 대형폐기물 신고 대상이 아니다.
    # 그래서 형광등 페이지가 아니라 전등(등기구) 페이지로 보낸다.
    "조명기구": "jeondeung", "조명": "jeondeung", "전등": "jeondeung",
    "형광등": "jeondeung", "led등": "jeondeung", "전등틀": "jeondeung",
    # 토스트기는 에어프라이어 별칭인데 수수료표에 따로 오른 곳(1,000~2,000)이
    # 에어프라이어 중앙값을 3,000에서 2,750으로 끌어내린다 (docs/40, 판단 42).
    "토스트기": None, "토스터": None, "토스터기": None, "토스트 기계": None,
    # 커피머신도 같은 자리다. '커피메이트'(2,000)와 '전기스토브(커피메이커)'가
    # 에어프라이어 최저가를 3,000에서 2,500으로 끌어내린다 (판단 42).
    "커피머신": None, "커피메이커": None, "커피메이트": None,
    "캡슐커피머신": None, "에스프레소머신": None, "제빵기": None, "제빵기계": None,
    # 신발 페이지 별칭 '인라인스케이트'. 신발은 6곳(중앙값 3,000)인데 인라인이
    # 6곳(중앙값 2,000)을 더 얹는다. 훈령이 같은 줄에 적은 물건이라 별칭이지만
    # 과금은 신발이 아니라 스포츠용품 쪽에 붙는다 (docs/45, 판단 42).
    "인라인스케이트": None, "인라인": None, "롤러스케이트": None, "스케이트": None,
    # 퍼즐매트 페이지 별칭 '쿨매트'. 강북구가 쿨매트를 '1인용 마다' 1,000원으로
    # 따로 올려 두었는데 퍼즐매트(8곳, 중앙값 2,750)에 섞으면 최저가가
    # 2,000에서 1,000으로, 중앙값이 2,500으로 내려간다. 답이 같아 별칭으로
    # 받되 과금 축은 갈라 둔다 (docs/48, 판단 42).
    "쿨매트": None, "냉매트": None, "쿨링매트": None,
    # 도자기 페이지는 수수료 축이 없다. 품목표에 '도자기'라는 이름으로 오른 곳이
    # 남광주 '잡재물류' 한 칸뿐이고, '자기'가 접미 일치로 **타자기**를 끌어온다
    # (docs/49, 판단 44). 이름째 막는다 (판단 47).
    "도자기": None, "자기": None, "타자기": None, "사기그릇": None, "도기": None,
    # 지자체 품목표의 '마대'는 **버리는 자루가 아니라 담으라고 파는 마대**다.
    # 춘천시 '기타, 마대(10kg 미만)', 포항시 '마대(80킬로그램 쌀포대기준)'이
    # 전부 특수규격마대 값이다. 마대자루 페이지가 말하는 물건이 아니다 (판단 47).
    "마대": None, "마대자루": None, "마대 자루": None, "자루": None,
    "포대자루": None, "쌀포대": None, "쌀 포대": None, "사료포대": None,
    "사료 포대": None, "pp마대": None, "피피마대": None, "비료포대": None,
    "곡물포대": None, "밀가루 포대": None, "양파망 자루": None,
    # 폐목재의 '목재'는 재질 표기라 가구 행에 그대로 붙어 있다. 강북구
    # '식탁/탁자/테이블(목재)', 양천구 '침대(목재)', 화성시 '캐비닛 (철재,목재)'가
    # 폐목재 중앙값에 섞여 범위가 750~15,000으로 벌어졌다. 재질 표기는 막고
    # 품목 표기('폐목재', '합판', '파렛트')만 남긴다 (판단 39).
    "목재": None, "목재류": None,
    # 파렛트는 산업용 운반대다. 폐목재 별칭으로 검색은 받되 과금은 가른다 -
    # 9곳이 폐목재 4곳보다 많아 통계를 주도하고, 남동구 '항공용' 15,000이
    # 최대값을 만든다 (판단 39, 42).
    "파렛트": None, "파 렛 트": None, "팔레트": None, "나무 팔레트": None,
    # 합판도 같다. 폐목재는 무게 과금(5kg당 1,000원)이고 합판은 장당
    # 2,000~3,000원이라 섞으면 본체 중앙값이 1,500에서 2,000으로 뛴다.
    # 답이 같아 별칭으로 받되 값은 본문이 갈라 적는다 (판단 42).
    "합판": None, "합판 조각": None, "mdf": None, "엠디에프": None,
    # 바이올린 페이지 별칭 '악기'는 양천구 '악기류'(피아노 15,000 포함)를 통째로
    # 끌어와 지역값이 4,500이 된다. 악기 통계는 안 모으고 본문이 지역별로 적는다.
    "악기": None, "현악기": None, "기타 악기": None, "바이올린 케이스": None,
    "첼로": None, "통기타": None, "우쿨렐레": None, "비올라": None,
    # 21차 하위 구간 별칭에서 걸린 셋 (docs/54, 판단 70). 붙이자마자
    # `build_fee_stats` 전후 diff가 잡았다.
    #   '온풍기', '히터' -> 품목표가 **에어컨과 한 칸**에 적는다
    #   (강북구 '에어컨/온풍기' 3,000~20,000, 오산시 '에어컨,온풍기').
    #   전기장판 중앙값이 3,000에서 4,500으로 뛰었다 (판단 39, 56).
    #   '전기히터'는 21차 전부터 있던 별칭이라 건드리지 않는다 - 막으면
    #   전기장판이 30곳 3,000에서 26곳 3,500으로 움직인다.
    "온풍기": None, "히터": None,
    #   '그릴' -> 정원용 바비큐 그릴(양평, 오산, 화성 2,000~3,000)이다.
    #   프라이팬에 얹는 미니그릴이 아니다. 3곳 2,000이 6곳 2,500이 됐다.
    "그릴": None, "바비큐그릴": None,
    #   '재' -> 접미 일치로 목재, 배관재, 포장재를 끌어왔다. 타일은 수수료
    #   축이 0건인데 10곳짜리 폐목재 요금표가 생겼다 (판단 47).
    "재": None, "연탄재": None, "연탄": None,
    # 샴푸 페이지(28차 신설)는 액체라 수수료 축이 아예 없다. 그런데 별칭
    # '컨디셔너'가 접미 일치로 **에어컨디셔너**(에어컨) 6행을 끌어와
    # '5곳, 중앙값 6,000원'을 만들었다. 액체 세정제 페이지에 에어컨
    # 요금표가 뜰 뻔했다 (docs/54, 판단 47, 70). 이름째 막는다.
    "샴푸": None, "린스": None, "컨디셔너": None, "트리트먼트": None,
    "바디워시": None, "바디로션": None, "로션": None, "스킨": None,
    "토너": None, "에센스": None,
    # 연고, 마라탕, 여권도 같다. 수수료 축이 없는데 짧은 이름이 접미
    # 일치로 끌려간다.
    "연고": None, "마라탕": None, "국물": None, "건더기": None,
    "여권": None, "전자여권": None,
    # 축구공 페이지 별칭 '공'. 접미 일치로 **볼링공** 7행을 통째로 끌어왔다.
    # 축구공, 농구공, 골프공은 품목표에 0건이라 그 페이지의 '7곳, 중앙값
    # 2,000원'이 전부 볼링공 값이었다 (docs/54, 판단 47). 공은 바람 빼고
    # 종량제봉투인데 대형폐기물 요금표가 떠 있었으니 답까지 반대였다.
    "공": None, "농구공": None, "배구공": None, "야구공": None,
    "테니스공": None, "골프공": None,
    # 크리스마스트리 페이지 별칭 '트리'. 강북구 '인조나무/트리/화환'은 조화가
    # '화환'으로 이미 받는 행이고, 높이 50cm'마다' 1,000원이라 통짜 값도 아니다.
    # 크리스마스트리 자체 행 4곳만 남긴다 (docs/46, 판단 24, 47).
    "트리": None, "인조나무": None,
    # --- 짧은 별칭 전수 점검 (docs/55, 판단 83) ---
    # '욕조' -> 아기욕조. 본체 행이 0건인데 성인 욕조 74행이 40곳짜리 요금표를
    # 만들고 있었다(최대 20,000원, 부산 동구 '욕 조'). 아기욕조는 플라스틱
    # 대야다. 유아용 표기만 남긴다 (판단 47).
    "욕조": None, "반신욕조": None, "월풀욕조": None,
    "유아용욕조": "agiyokjo",
    # '보행기' -> 휠체어. 품목표의 '보행기'는 거의 전부 **유모차와 한 칸**이다
    # (파주 '유모차,보행기', 광진 '유아용 보행기'). 유아용 보행기지 노인
    # 보행보조기가 아니다. 휠체어는 자기 이름으로 26곳이 있다 (판단 39, 56).
    "보행기": None,
    # '식기' -> 그릇. 끌어온 행이 오산 '식기(세척)건조기'와 광진 '반려견 급식기'
    # 뿐이다. 그릇 자체 행은 남광주 '잡재물류' 한 곳이라, 5곳짜리 요금표의
    # 4곳이 식기건조기와 개밥그릇이었다 (판단 47).
    "식기": None, "식기류": None,
    # '화환' -> 조화. 조화는 자기 이름으로 오른 곳이 0건인데 화환 14곳이
    # 요금표를 통째로 만들고 있었다. 조화 페이지의 답은 종량제봉투인데
    # 대형폐기물 요금표가 떠 있었다 (판단 47, docs/54의 축구공과 같다).
    "화환": None, "근조화환": None, "축하화환": None,
    # '펜' -> 볼펜. 접미 일치로 연수구 '씰링펜(전등)'을 끌어왔다. 실링팬이다.
    "펜": None, "볼펜": None, "사인펜": None, "네임펜": None, "형광펜": None,
    # '장류' -> 된장 고추장. 접미 일치로 함양군 '진열장류(책장+장식장+...)'를
    # 끌어왔다. 장(醬)이 아니라 진열장이다.
    "장류": None, "된장": None, "고추장": None, "간장": None, "쌈장": None,
    # '휠' -> 타이어. 광진구 '캣휠'(고양이 쳇바퀴)을 끌어왔다.
    "휠": None, "알루미늄휠": None,
    # '차탁자' -> 밥상. 포항 '차탁자(응접세트)', 광명 '차탁자(티테이블)'는
    # 소파 앞 테이블이지 밥상이 아니다. 밥상은 자기 이름으로 16곳이 있다.
    "차탁자": None, "티테이블": None,
}

# 표기는 우리 것이 맞는데 **그 행**이 다른 물건인 경우. EXTRA_ALIAS의 None은
# 표기째 막는 것이라 여기엔 못 쓴다 - '건조대'를 막으면 빨래건조대가 자기 행도
# 잃고, '침대'를 막으면 침대 페이지가 통째로 빈다. 행 쪽에서 거른다 (판단 83).
DENY_ROWS = [
    # 신발 별칭 '부츠'. 5곳 중 4곳이 스키 장비와 한 칸이다(광명 '스키+보드+부츠',
    # 강북 '스키부츠'). 인라인스케이트를 막은 것과 같은 자리다 (docs/45, 판단 42).
    ("부츠", re.compile(r"스키|보드")),
    # 침대는 두 글자라 접미 일치가 **받침대**를 통째로 먹는다. 텔레비전 받침대,
    # 수족관 받침대, 오디오 받침대, 가스레인지 받침대가 침대 요금에 섞여 있었다.
    # 침대받침대와 매트리스 받침대는 진짜 침대 부품이라 남긴다.
    ("침대", re.compile(r"(텔레비전|TV|오디오|수족관|수조관|가스레인지|화한|거실장)")),
    ("침대", re.compile(r"^\(?받침대\)?$")),
    # 빨래건조대 별칭 '건조대'가 식기건조대(그릇 말리는 선반)를 끌어온다.
    ("건조대", re.compile(r"식기")),
    # 스탠드 조명 별칭 '스탠드'. 제주 '옷걸이(스탠드, 행거)'는 세우는 옷걸이다.
    ("스탠드", re.compile(r"옷걸이")),
]

# 과금 단위. 통짜 한 개에 얼마가 아니라 '단위 얼마'로 매기는 품목이 있다.
# 장롱은 1쪽당, 카펫은 3.3㎡당, 장판은 5m당, 깨진 유리는 kg당이다.
# 단위가 다른 값을 같은 중앙값에 섞으면 배수만큼 틀린다 (docs/12).
#
# '이상', '미만'이 붙은 규격 구간과 구별해야 한다. 냉장고 '300ℓ 이상'은
# 크기 구간이지 과금 단위가 아니다. 그래서 '당'이 붙은 표기만 단위로 본다.
UNIT_RE = re.compile(r"(1?\s*쪽\s*당|\(?1\s*쪽\)?|쪽당|1\s*짝|짝문|당\s*1쪽"
                     r"|짝당|폭당|칸당|한\s*짝당"
                     # 강북구는 '당' 대신 '마다'로 적는다 ('서랍장 1단마다',
                     # '인덕션 류 1구 마다'). 같은 뜻이다 (docs/46, 판단 24)
                     r"|단\s*마다|칸\s*마다|쪽\s*마다|구\s*마다"
                     # 세는 낱단위(쪽, 짝, 폭, 칸, 단, 구) 뒤에 붙는 꼬리는
                     # '당', '마다', '기준'이 다 온다. 사이에 괄호가 끼기도
                     # 한다(제주시 '병풍 1폭(가로 30cm)당'). scripts/
                     # check_fee_units.py가 빠진 표기를 찾아 준다
                     r"|(?:쪽|짝|폭|칸|단|구)\s*(?:\([^)]*\))?\s*(?:당|마다|기준))")

# 마대, 자루, 포대, 묶음처럼 담는 그릇을 세는 표기. 그릇 자체는 규격이 없지만
# 지자체가 그릇 크기를 ℓ이나 kg으로 적어 둔다 ('100ℓ 자루당', '20㎏마대기준').
# 적어 둔 그 규격이 곧 환산 기준이다 (docs/29).
SACK = r"(?:마대|자루|포대|봉투|묶음|박스)"
# '당', '기준', '1개당'처럼 단위임을 알리는 꼬리. 이게 없으면 규격 구간이다.
# 담는 그릇 앞에 개수가 붙기도 한다 (청양군 '나무류 100ℓ 1묶음 당').
TAIL = r"(?:\s*(?:\d+\s*)?(?:자루|마대|포대|봉투|묶음)?\s*(?:1\s*개)?\s*(?:당|기준|마다))"

# (단위 이름, 기준 단위, 수량+단위 정규식, 기준 단위 환산 계수)
# 수량이 안 적힌 'kg당', '㎡당'은 1로 본다.
# '당', '기준' 말고 '마다'로 적는 지자체가 있다. 강북구 품목표 55행이 전부
# 그렇고("가장 긴 면이 50cm마다 1,000원"), '마다'를 못 읽으면 그 값이 통짜
# 요금으로 들어가 강북구가 어느 품목에서나 최저가가 된다 (docs/46, 판단 24).
UNIT_TAIL = r"(?:당|기준|마다)"

MEASURED = [
    # 무게. 'kg당' 말고 '20㎏마대기준', 'PP포대 당(25킬로그램)'도 같은 뜻이다.
    ("weight", "kg", re.compile(
        r"(\d+(?:\.\d+)?)?\s*(kg|㎏|킬로그램|킬로|톤|t)\s*(?:%s)?\s*%s"
        % (SACK, UNIT_TAIL), re.I), {"톤": 1000, "t": 1000}),
    # '1㎡초과 시 마다'(대덕구), '1제곱미터초과시마다'(서구)도 같은 뜻이다.
    # 광진구, 연수구는 제곱미터를 'm²'(윗첨자)로 적는다. '㎡' 한 글자와
    # 다른 문자열이라 이걸 빠뜨리면 21행이 통짜 요금이 된다.
    ("area", "㎡", re.compile(r"(\d+(?:\.\d+)?)?\s*(㎡|m2|m²|제곱미터|평)"
                             r"\s*(?:초과\s*시)?\s*(?:\([^)]*\))?\s*%s"
                             % UNIT_TAIL, re.I), {"평": 3.3}),
    ("length", "m", re.compile(r"(\d+(?:\.\d+)?)?\s*(m|미터|cm|㎝)\s*%s"
                              % UNIT_TAIL, re.I), {"cm": 0.01, "㎝": 0.01}),
    # 부피. '100ℓ 자루당', '100리터 봉투기준', '20ℓ당'. 기준 단위는 1ℓ다.
    # 냉장고 '500ℓ 이상'은 꼬리가 없어서 여기 안 걸린다 (확정 판단 24번).
    ("volume", "ℓ", re.compile(r"(\d+(?:\.\d+)?)\s*(ℓ|l|리터|L)%s" % TAIL), {}),
    # 세제곱미터는 리터로 환산하지 않는다. 수족관 '1㎥당 6,000원'을 ℓ로 펴면
    # '1ℓ당 6원'이 되어 화면이 못 읽을 숫자가 된다. 단위를 따로 둔다 (docs/46).
    ("volume_m3", "㎥", re.compile(r"(\d+(?:\.\d+)?)?\s*(㎥|m3|세제곱미터)"
                                  r"\s*(?:이상)?\s*(?:\([^)]*\))?\s*%s"
                                  % UNIT_TAIL, re.I), {}),
]


def unit_of(item, spec):
    """과금 단위와 기준 단위 환산 계수를 돌려준다.

    ('area', 3.3) 이면 그 행의 금액은 3.3㎡ 값이라는 뜻이다. 금액을
    3.3으로 나눠야 다른 지자체의 1㎡당 값과 같은 자리에 놓인다.
    """
    s = item + " " + spec
    if UNIT_RE.search(s):
        return "panel", 1.0
    for name, _base, pat, scale in MEASURED:
        m = pat.search(s)
        if not m:
            continue
        qty = float(m.group(1)) if m.group(1) else 1.0
        qty *= scale.get(m.group(2).lower(), scale.get(m.group(2), 1))
        if qty <= 0:
            continue
        return name, qty
    return "whole", 1.0


# 화면과 본문에서 쓰는 단위 이름.
UNIT_LABEL = {"whole": "전후", "panel": "1쪽당", "area": "1㎡당",
              "length": "1m당", "weight": "1kg당", "volume": "1ℓ당",
              "volume_m3": "1㎥당"}


SPLIT = re.compile(r"[,/·]|및|그리고")
PAREN = re.compile(r"[()（）\[\]]")


def tokens(item):
    """'장롱(옷장)', '비디오, 청소기, 선풍기' 같은 표기를 낱개로 쪼갠다."""
    s = PAREN.sub(",", item)
    out = []
    for t in SPLIT.split(s):
        t = re.sub(r"\s+", "", t).strip(".·-")
        if not t:
            continue
        out.append(t)
        # '피아노류'·'카펫트류'처럼 묶음 접미가 붙은 표기도 같은 품목으로 본다.
        if len(t) > 2 and t.endswith("류"):
            out.append(t[:-1])
    return out


def build_matcher(items):
    """토큰 → slug. 긴 이름을 먼저 보게 해서 전자피아노가 피아노로 새지 않게 한다."""
    table = {}
    for it in items:
        names = [it["name"]] + (it.get("aliases") or [])
        for n in names:
            table[re.sub(r"\s+", "", n)] = it["slug"]
    for k, v in EXTRA_ALIAS.items():
        if v:
            table[k] = v
        else:
            # None은 '이 표기는 수수료를 안 모은다'는 뜻이다. items의 별칭에서 들어온
            # 같은 표기를 지워야 막힌다 (docs/36 판단 42, docs/39 스피커/박스)
            table.pop(k, None)
    return table, sorted(table, key=len, reverse=True)


def matched_name(token, table, order):
    """토큰이 어느 표기에 걸렸는지. 접미 일치도 그 표기를 돌려준다."""
    if token in table:
        return token
    # '전기밥솥'처럼 수식어가 붙은 표기는 접미 일치로 받는다. 긴 후보가 우선이다.
    for name in order:
        if len(token) > len(name) and token.endswith(name):
            return name
    return None


def match(token, table, order, raw=""):
    name = matched_name(token, table, order)
    if name is None:
        return None
    # 표기는 맞는데 그 행이 다른 물건이면 안 센다 (DENY_ROWS 참조)
    for deny_name, pat in DENY_ROWS:
        if name == deny_name and pat.search(raw):
            return None
    return table[name]


def summarize(per_region):
    """지역별 대표값 목록에서 통계를 낸다. 표본이 3곳 미만이면 버린다."""
    vals = sorted(per_region.values())
    if len(vals) < 3:
        return None
    cheapest = min(per_region.items(), key=lambda kv: kv[1])
    dearest = max(per_region.items(), key=lambda kv: kv[1])
    return {
        "median": int(statistics.median(vals)),
        "min": vals[0],
        "max": vals[-1],
        "q1": vals[len(vals) // 4],
        "q3": vals[(len(vals) * 3) // 4],
        "regions": len(vals),
        "cheapest": {"region": cheapest[0], "fee": cheapest[1]},
        "dearest": {"region": dearest[0], "fee": dearest[1]},
        "by_region": dict(sorted(per_region.items(), key=lambda kv: kv[1])),
    }


def main():
    items = json.load(io.open(ITEMS, encoding="utf-8"))
    rows = list(csv.DictReader(io.open(FEES, encoding="utf-8")))
    table, order = build_matcher(items)

    # EXTRA_ALIAS는 slug를 손으로 적는다. 개명하면(판단 41) 그 slug가 고아가
    # 되는데, 산출물은 멀쩡해 보인다 - 없어진 slug로 키가 하나 더 생길 뿐이다.
    # 실제로 LED등 -> 전등 개명에서 조명기구 23곳이 통째로 고아 키에 남았다.
    # "막았다고 적은 코드는 막고 있는지 돌려 본다"의 다른 얼굴이다 (판단 44).
    slugs = {it["slug"] for it in (items if isinstance(items, list)
                                  else items.get("items", []))}
    orphans = sorted({v for v in EXTRA_ALIAS.values() if v and v not in slugs})
    if orphans:
        sys.exit("EXTRA_ALIAS가 없는 slug를 가리킨다: %s. "
                 "개명했으면 여기 slug도 같이 고친다." % ", ".join(orphans))

    # slug → 과금단위 → 지역 → 금액들
    buckets = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    base_dates = defaultdict(list)
    for r in rows:
        fee = int(r["fee"])
        if fee <= 0:
            continue
        unit, qty = unit_of(r["item"], r["spec"])
        if qty != 1.0:
            fee = int(round(fee / qty))
            if fee <= 0:
                continue
        region = (r["sido"] + " " + r["sigungu"]).strip()
        seen = set()
        for tok in tokens(r["item"]):
            slug = match(tok, table, order, r["item"])
            if slug and slug not in seen:
                seen.add(slug)
                buckets[slug][unit][region].append(fee)
                if r["base_date"]:
                    base_dates[slug].append(r["base_date"])

    out = {}
    for slug, by_unit in buckets.items():
        stats = {}
        for unit, regions in by_unit.items():
            per_region = {k: int(statistics.median(sorted(v))) for k, v in regions.items()}
            st = summarize(per_region)
            if st:
                stats[unit] = st
        if not stats:
            continue
        # 어느 단위가 다수인지. 쪽당이 다수면 화면에서 그걸 먼저 말해야 한다.
        # 같은 지역 수면 통짜를 앞에 둔다. 읽는 사람이 기대하는 쪽이다.
        order = ["whole", "panel", "area", "length", "weight", "volume",
                 "volume_m3"]
        primary = max(order, key=lambda u: (stats.get(u, {}).get("regions", 0),
                                            -order.index(u)))
        entry = {
            "primary": primary,
            "base_date": max(base_dates[slug]) if base_dates[slug] else "",
        }
        for unit in order:
            if unit in stats:
                entry[unit] = stats[unit]
        out[slug] = entry

    # 키 순서는 CSV를 훑은 순서라 품목이 하나만 늘어도 전체가 밀린다.
    # 값이 그대로인데 파일 전체가 diff로 잡히면 뭐가 바뀌었는지 안 보인다.
    io.open(OUT, "w", encoding="utf-8").write(
        json.dumps(dict(sorted(out.items())), ensure_ascii=False, indent=2) + "\n"
    )

    print("품목 %d개 집계" % len(out))
    for it in items:
        e = out.get(it["slug"])
        if not e:
            print("  %-8s  —" % it["name"])
            continue
        parts = []
        for unit in ("whole", "panel", "area", "length", "weight", "volume"):
            if unit in e:
                st = e[unit]
                parts.append("%s %s원(%d지역)"
                             % (UNIT_LABEL[unit], f"{st['median']:,}",
                                st["regions"]))
        star = ""
        if e["primary"] != "whole":
            star = " <-%s 우세" % UNIT_LABEL[e["primary"]]
        print("  %-8s %s%s" % (it["name"], " / ".join(parts), star))


if __name__ == "__main__":
    main()
