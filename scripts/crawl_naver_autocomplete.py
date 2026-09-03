# -*- coding: utf-8 -*-
"""네이버 자동완성 재귀 크롤링 -> 품목 시드 리스트 생성.

출처: https://ac.search.naver.com/nx/ac
docs/06-action-plan.md 3번 작업. 산출물은 게이트 1(키워드 볼륨 실측)의 입력값.

품목은 "실제 자동완성에 등장한 것"만 채택한다. 씨앗 명사는 질의로만 쓰이고,
응답에 나타나지 않으면 결과에 들어가지 않는다.
"""
import csv
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict

AC = "https://ac.search.naver.com/nx/ac"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw", "autocomplete-crawl.jsonl")
OUT = os.path.join(ROOT, "data", "keywords", "items.csv")
DELAY = 0.35
MAX_QUERIES = 2000

# 배출 의도를 나타내는 어미. 긴 것부터 매칭해야 "버리는법"이 "버리는"에 먹히지 않는다.
SUFFIXES = [
    "버리는 방법", "버리는방법", "버리는 법", "버리는법", "버리는 비용", "버리는 가격",
    "버리는 곳", "버리는",
    "분리수거 방법", "분리수거", "분리배출", "재활용",
    "음식물쓰레기", "음식물 쓰레기", "음식물",
    "일반쓰레기", "일반 쓰레기", "종량제봉투", "종량제",
    "대형폐기물", "폐기물", "폐기 비용", "폐기",
    "어디에 버려", "어떻게 버려", "버려도 되나요", "버려도 되나",
]
SUFFIXES.sort(key=len, reverse=True)

# 레벨 0. 품목이 앞에 붙어 돌아오는 질의들.
SEED_PATTERNS = [
    "버리는법", "버리는 방법", "버리는 비용", "분리수거", "분리수거 방법", "분리배출",
    "음식물쓰레기", "음식물", "일반쓰레기", "종량제봉투", "폐기물", "대형폐기물",
    "재활용", "어디에 버려", "버려도 되나요",
]

# 질의용 씨앗 명사. 채택 여부는 응답이 결정한다.
SEED_NOUNS = """
매트리스 침대 쇼파 소파 책상 의자 옷장 서랍장 화장대 식탁 선반 행거 거울 카펫 러그
냉장고 김치냉장고 세탁기 건조기 에어컨 TV 모니터 노트북 컴퓨터 프린터 청소기 전자레인지
밥솥 정수기 가습기 제습기 선풍기 히터 온수매트 전기장판 공기청정기 오븐 에어프라이어
프라이팬 후라이팬 냄비 그릇 접시 유리컵 머그컵 텀블러 도마 칼 커터칼 수저 젓가락 보온병
아이스팩 보냉백 스티로폼 비닐 페트병 유리병 캔 우유팩 종이컵 컵라면 빨대 랩 은박지 호일
건전지 형광등 전구 LED 콘센트 멀티탭 충전기 전선 케이블 보조배터리 휴대폰 배터리
옷 옷걸이 신발 운동화 가방 캐리어 우산 양산 모자 벨트 인형 장난감 이불 베개 토퍼 커튼 수건
책 잡지 신문 노트 종이 앨범 사진 CD DVD 액자 상장 명함
화분 흙 나뭇가지 낙엽 조화 화병
약 영양제 화장품 향수 매니큐어 렌즈 안경 마스크 기저귀 물티슈 칫솔 치약 면도기
계란껍질 달걀껍질 치킨뼈 갈비뼈 생선뼈 조개껍질 과일껍질 수박껍질 바나나껍질 양파껍질
커피찌꺼기 티백 견과류껍질 옥수수대 고추씨 김치 된장 라면국물 식용유 기름
자전거 유모차 카시트 킥보드 골프채 헬스기구 러닝머신 어항 피아노 소화기 가스레인지
보일러 변기 세면대 타일 장판 벽지 문짝 방충망 빨래건조대 다리미 재봉틀 금고 가구
""".split()

session_log = []
seen_queries = set()


def fetch(q):
    if q in seen_queries or len(seen_queries) >= MAX_QUERIES:
        return []
    seen_queries.add(q)
    url = AC + "?" + urllib.parse.urlencode({
        "q": q, "st": 100, "r_format": "json", "r_enc": "UTF-8",
        "q_enc": "UTF-8", "r_lt": 100, "frm": "nx",
    })
    for attempt in range(3):
        try:
            raw = urllib.request.urlopen(url, timeout=10).read().decode("utf-8")
            break
        except Exception as e:
            if attempt == 2:
                sys.stderr.write("FAIL %s: %s\n" % (q, e))
                return []
            time.sleep(1.5 * (attempt + 1))
    out = []
    try:
        data = json.loads(raw)
    except ValueError:
        return []
    for group in data.get("items") or []:
        for entry in group:
            if entry and entry[0]:
                out.append(entry[0])
    session_log.append({"query": q, "suggestions": out})
    time.sleep(DELAY)
    return out


BAD = {
    "", "쓰레기", "생활", "재활용", "분리", "음식물", "일반", "대형", "폐기물",
    "종량제", "가정", "집", "아파트", "우리집", "그", "이", "저", "다",
}
OK_CHARS = re.compile(r"^[가-힣A-Za-z0-9]+(?: [가-힣A-Za-z0-9]+)?$")
# 배출과 무관한 문맥. 꿈해몽 / 인체 / 반려동물 / 상표 검색이 섞여 들어온다.
NOISE = re.compile(r"(꿈|삼킴|먹으면|강아지|고양이|안까짐|해몽|사주|증상|병원)")


def split_item(s):
    """자동완성 문자열을 (품목, 수식어, 패턴)으로 분해. 실패 시 None."""
    for suf in SUFFIXES:
        idx = s.find(suf)
        if idx > 0:
            item = s[:idx].strip()
            modifier = s[idx + len(suf):].strip()
            return item, modifier, suf
    return None


def acceptable(item):
    if item in BAD or NOISE.search(item):
        return False
    if not (1 < len(item) <= 12):
        return False
    return bool(OK_CHARS.match(item))


def main():
    items = defaultdict(lambda: {
        "freq": 0, "patterns": Counter(), "modifiers": Counter(),
        "queries": set(), "sample": "",
    })

    def absorb(query, suggestions):
        for s in suggestions:
            parsed = split_item(s)
            if not parsed:
                continue
            item, modifier, suf = parsed
            if not acceptable(item):
                continue
            rec = items[item]
            rec["freq"] += 1
            rec["patterns"][suf] += 1
            rec["queries"].add(query)
            if modifier and not NOISE.search(modifier):
                rec["modifiers"][modifier] += 1
            if not rec["sample"]:
                rec["sample"] = s

    # 레벨 0 — 어미만으로 질의
    for pat in SEED_PATTERNS:
        absorb(pat, fetch(pat))
    print("L0 done: %d items / %d queries" % (len(items), len(seen_queries)))

    # 레벨 1 — 씨앗 명사 x 주요 어미
    for noun in SEED_NOUNS:
        for pat in ("버리는", "분리수거", "음식물"):
            absorb(noun, fetch("%s %s" % (noun, pat)))
    print("L1 done: %d items / %d queries" % (len(items), len(seen_queries)))

    # 레벨 2 — 발견된 품목 재귀 확장 (하위 변종 확보: 젤/곡물/PCM 아이스팩 형태)
    frontier = sorted(items.keys())
    for item in frontier:
        for pat in ("버리는법", "분리수거"):
            absorb(item, fetch("%s %s" % (item, pat)))
    print("L2 done: %d items / %d queries" % (len(items), len(seen_queries)))

    rows = []
    for item, rec in items.items():
        rows.append({
            "item": item,
            "freq": rec["freq"],
            "n_queries": len(rec["queries"]),
            "patterns": "|".join(p for p, _ in rec["patterns"].most_common()),
            "top_modifiers": "|".join(m for m, _ in rec["modifiers"].most_common(6)),
            "sample_suggestion": rec["sample"],
        })
    rows.sort(key=lambda r: (-r["freq"], r["item"]))

    with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "item", "freq", "n_queries", "patterns", "top_modifiers", "sample_suggestion"])
        w.writeheader()
        w.writerows(rows)

    with open(RAW, "w", encoding="utf-8") as f:
        for entry in session_log:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print("items: %d -> %s" % (len(rows), OUT))
    print("queries: %d -> %s" % (len(session_log), RAW))


if __name__ == "__main__":
    main()
