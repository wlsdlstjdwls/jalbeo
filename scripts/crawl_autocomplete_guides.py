# -*- coding: utf-8 -*-
"""절차 축 자동완성 크롤 — `/guides/` 4번째 페이지 후보를 캔다.

지금까지의 크롤(`crawl_naver_autocomplete.py`, `crawl_autocomplete_r2.py`)은
씨앗이 전부 **품목명**이었다. 그래서 절차 질의가 들어와도 앞의 품목만 떼어내
"헌책 방문수거"를 헌책이라는 품목 후보로 기록하고 "방문수거"는 버렸다.
`docs/14` 확정 판단 10번대로 절차는 품목 페이지가 못 받는 축인데, 정작 그 축의
후보 목록이 없다.

바뀐 점 3가지:
  1. 씨앗이 절차 명사다 (종량제봉투, 분리배출, 대형폐기물 스티커, 의류수거함...).
     품목은 씨앗에 넣지 않는다 — 품목 축은 이미 167개가 덮었다
  2. 자동완성 문자열을 **통째로** 남긴다. 품목 크롤은 어미를 잘라 품목만
     세지만, 절차는 어미 쪽이 본체다 ("종량제봉투 가격"에서 값은 "가격"에 있다)
  3. 기존 3개 가이드와 발행 품목 167개에 이미 걸리는 질의를 뺀다. 남는 게 후보다

출력:
  data/keywords/candidates-guides.csv        후보 질의 (군집 머리말 기준 정렬)
  data/raw/autocomplete-crawl-guides.jsonl   원본 응답
"""
import csv
import io
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

AC = "https://ac.search.naver.com/nx/ac"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEMS = os.path.join(ROOT, "site", "src", "data", "items.json")
GUIDE_DIR = os.path.join(ROOT, "site", "src", "content", "guides")
RAW = os.path.join(ROOT, "data", "raw", "autocomplete-crawl-guides.jsonl")
OUT = os.path.join(ROOT, "data", "keywords", "candidates-guides.csv")
DELAY = 0.35
MAX_QUERIES = 3000

# 레벨 0 씨앗. 전부 절차/제도 명사다. 품목은 한 개도 넣지 않는다.
SEEDS = [
    # 봉투와 규격
    "종량제봉투", "종량제 봉투 가격", "쓰레기봉투", "재활용 봉투", "마대",
    "음식물쓰레기 봉투", "음식물 종량제",
    # 신고와 스티커
    "대형폐기물 스티커", "폐기물 스티커", "폐기물 신고", "인터넷 배출신고",
    "대형폐기물 수수료",
    # 수거 서비스
    "무상수거", "무료수거", "방문수거", "수거 신청", "재활용센터",
    "의류수거함", "헌옷 수거", "헌책 수거", "고물상",
    # 배출 규칙과 시간
    "분리배출", "분리수거 요일", "쓰레기 버리는 시간", "쓰레기 버리는 요일",
    "아파트 분리수거", "원룸 쓰레기", "자취방 쓰레기", "클린하우스",
    "분리배출 표시", "재활용 안되는 것",
    # 제도와 벌칙
    "쓰레기 무단투기", "종량제 위반 과태료", "쓰레기 과태료", "폐기물 신고포상금",
    # 상황
    "이사 쓰레기", "이사할 때 쓰레기", "대청소 쓰레기", "유품정리",
    "인테리어 폐자재", "공사장 폐기물",
]

# 레벨 1에서 씨앗에 붙일 어미. 절차 질의가 실제로 갈라지는 지점들이다.
L1_PATTERNS = (
    "신청", "신청 방법", "방법", "가격", "비용", "수수료",
    "어디서", "파는곳", "요일", "시간", "규격", "종류", "과태료", "환불",
)
# 레벨 2는 새로 나온 머리말만 한 겹 더 판다.
L2_PATTERNS = ("방법", "신청", "가격")

# 배출과 무관한 문맥.
NOISE = re.compile(r"(꿈|해몽|사주|주식|게임|노래|가사|드라마|영화|다이어트)")
# 지역명이 박힌 질의는 B층(품목 x 지자체) 폐기 판단과 같은 이유로 뺀다.
REGION = re.compile(
    r"(서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남"
    r"|경북|경남|제주|시청|구청|주민센터|[가-힣]{1,3}(시|군|구)\s)")

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
    raw = None
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


def norm(s):
    return s.replace(" ", "").lower()


def head_of(s):
    """군집 머리말. 앞 두 어절까지를 한 덩어리로 본다."""
    parts = s.split()
    return " ".join(parts[:2]) if len(parts) > 1 else s


def main():
    rows = json.load(io.open(ITEMS, encoding="utf-8"))
    item_names = set()
    for r in rows:
        item_names.add(norm(r["name"]))
        for a in (r.get("aliases") or []):
            item_names.add(norm(a))

    guides = sorted(f[:-3] for f in os.listdir(GUIDE_DIR) if f.endswith(".md"))
    print("발행 품목 %d개(별칭 포함 표기 %d) / 가이드 %d개"
          % (len(rows), len(item_names), len(guides)))

    hits = defaultdict(lambda: {"freq": 0, "queries": set()})

    def absorb(query, suggestions):
        for s in suggestions:
            s = s.strip()
            if not s or NOISE.search(s) or REGION.search(s + " "):
                continue
            if len(s) > 30:
                continue
            rec = hits[s]
            rec["freq"] += 1
            rec["queries"].add(query)

    for seed in SEEDS:
        absorb(seed, fetch(seed))
    print("L0: %d개 질의 / %d건 수집" % (len(seen_queries), len(hits)))

    for seed in SEEDS:
        for pat in L1_PATTERNS:
            absorb(seed, fetch("%s %s" % (seed, pat)))
    print("L1: %d개 질의 / %d건 수집" % (len(seen_queries), len(hits)))

    # 레벨 2 대상: 씨앗에 없던 새 머리말만. 아는 걸 또 파면 아는 것만 나온다.
    seed_heads = {norm(head_of(s)) for s in SEEDS}
    frontier = sorted({head_of(s) for s in hits
                       if norm(head_of(s)) not in seed_heads})
    for head in frontier[:120]:
        for pat in L2_PATTERNS:
            absorb(head, fetch("%s %s" % (head, pat)))
    print("L2: %d개 질의 / %d건 수집 (frontier %d)"
          % (len(seen_queries), len(hits), len(frontier)))

    # 품목 페이지가 이미 받는 질의를 뺀다. 첫 어절이 발행 품목이면 품목 축이다.
    out = []
    dropped_item = 0
    for s, rec in hits.items():
        first = s.split()[0]
        if norm(first) in item_names or norm(s) in item_names:
            dropped_item += 1
            continue
        out.append({
            "query": s,
            "head": head_of(s),
            "freq": rec["freq"],
            "n_queries": len(rec["queries"]),
            "seeds": "|".join(sorted(rec["queries"])[:4]),
        })

    heads = Counter(r["head"] for r in out)
    out.sort(key=lambda r: (-heads[r["head"]], r["head"], -r["freq"], r["query"]))

    with io.open(OUT, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["query", "head", "freq", "n_queries", "seeds"])
        w.writeheader()
        w.writerows(out)
    with io.open(RAW, "w", encoding="utf-8") as f:
        for entry in session_log:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print("수집 %d건 중 품목 축 제외 %d -> 후보 %d건, 머리말 %d개"
          % (len(hits), dropped_item, len(out), len(heads)))
    print("상위 머리말: %s" % ", ".join("%s(%d)" % (h, n) for h, n in heads.most_common(15)))
    print("-> %s" % OUT)


if __name__ == "__main__":
    main()
