# -*- coding: utf-8 -*-
"""자동완성 재크롤 2차 — 발행 154개를 씨앗으로 새 품목 후보를 캔다.

1차(`crawl_naver_autocomplete.py`)는 손으로 고른 명사 목록을 씨앗으로 썼다.
그 목록이 곧 시드 325개고, 지금 그 풀은 소진됐다(발행 154, 별칭 329, 나머지는
표기변형과 조합어). 더 늘리려면 **씨앗을 사람이 아니라 발행분에서 뽑아야 한다.**

바뀐 점 3가지:
  1. 씨앗 = 발행 품목명 + 별칭 (사람이 떠올린 명사가 아니라 실측이 검증한 명사)
  2. 어미에 거래/절차 축을 더한다 (무상수거, 무료수거, 철거비용, 버리는곳).
     `docs/14`가 실측한 145,940짜리 축인데 1차 어미 목록에는 없었다
  3. 결과에서 이미 아는 것(발행명, 별칭, 시드 325)을 전부 뺀다. 남는 게 후보다

출력:
  data/keywords/candidates-r2.csv       새 후보만
  data/raw/autocomplete-crawl-r2.jsonl  원본 응답
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
SEED_CSV = os.path.join(ROOT, "data", "keywords", "items.csv")
RAW = os.path.join(ROOT, "data", "raw", "autocomplete-crawl-r2.jsonl")
OUT = os.path.join(ROOT, "data", "keywords", "candidates-r2.csv")
DELAY = 0.35
MAX_QUERIES = 3000

# 긴 것부터 매칭해야 "버리는법"이 "버리는"에 먹히지 않는다.
SUFFIXES = [
    "버리는 방법", "버리는방법", "버리는 법", "버리는법", "버리는 비용", "버리는 가격",
    "버리는 곳", "버리는곳", "버리는",
    "분리수거 방법", "분리수거", "분리배출", "재활용",
    "음식물쓰레기", "음식물 쓰레기", "음식물",
    "일반쓰레기", "일반 쓰레기", "종량제봉투", "종량제",
    "대형폐기물", "폐기물", "폐기 비용", "폐기방법", "폐기",
    # 2차에서 더한 거래/절차 축 (docs/14 무상수거 145,940)
    "무상방문수거", "무상수거", "무료수거", "방문수거", "수거 신청", "수거신청",
    "철거 비용", "철거비용", "철거", "처리 방법", "처리방법", "처리 비용", "처리비용",
    "어디에 버려", "어떻게 버려", "버려도 되나요", "버려도 되나",
]
SUFFIXES.sort(key=len, reverse=True)

# 레벨 0. 품목이 앞에 붙어 돌아오는 질의들.
SEED_PATTERNS = [
    "버리는법", "버리는 방법", "버리는 비용", "버리는곳", "분리수거", "분리수거 방법",
    "분리배출", "음식물쓰레기", "음식물", "일반쓰레기", "종량제봉투", "폐기물",
    "대형폐기물", "재활용", "어디에 버려", "버려도 되나요",
    "무상수거", "무료수거", "방문수거", "수거신청", "철거비용", "처리방법",
]

# 레벨 1에서 각 씨앗에 붙일 어미. 1차의 3개에 거래 축 1개를 더했다.
L1_PATTERNS = ("버리는", "분리수거", "음식물", "무상수거")
L2_PATTERNS = ("버리는법", "분리수거")

BAD = {
    "", "쓰레기", "생활", "재활용", "분리", "음식물", "일반", "대형", "폐기물",
    "종량제", "가정", "집", "아파트", "우리집", "그", "이", "저", "다",
    "무상", "무료", "방문", "수거", "철거", "처리", "비용",
}
OK_CHARS = re.compile(r"^[가-힣A-Za-z0-9]+(?: [가-힣A-Za-z0-9]+)?$")
# 배출과 무관한 문맥. 꿈해몽 / 인체 / 반려동물 / 상표 검색이 섞여 들어온다.
NOISE = re.compile(r"(꿈|삼킴|먹으면|강아지|고양이|안까짐|해몽|사주|증상|병원)")

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


def split_item(s):
    """자동완성 문자열을 (품목, 수식어, 어미)로 분해. 실패 시 None."""
    for suf in SUFFIXES:
        idx = s.find(suf)
        if idx > 0:
            return s[:idx].strip(), s[idx + len(suf):].strip(), suf
    return None


def acceptable(item):
    if item in BAD or NOISE.search(item):
        return False
    if not (1 < len(item) <= 12):
        return False
    return bool(OK_CHARS.match(item))


def norm(s):
    """표기변형 판정용. 공백을 지우면 '바나나 껍질'과 '바나나껍질'이 한 덩어리다."""
    return s.replace(" ", "")


def main():
    rows = json.load(io.open(ITEMS, encoding="utf-8"))
    names = [r["name"] for r in rows]
    aliases = [a for r in rows for a in (r.get("aliases") or [])]

    # 이미 아는 것. 후보에서 뺄 집합이다.
    known = set()
    for s in names + aliases:
        known.add(norm(s))
    with io.open(SEED_CSV, encoding="utf-8-sig") as f:
        seed_n = 0
        for row in csv.DictReader(f):
            known.add(norm(row["item"]))
            seed_n += 1
    print("known: 발행 %d + 별칭 %d + 시드 %d -> 고유 %d"
          % (len(names), len(aliases), seed_n, len(known)))

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

    for pat in SEED_PATTERNS:
        absorb(pat, fetch(pat))
    print("L0: %d items / %d queries" % (len(items), len(seen_queries)))

    # 씨앗은 발행 품목명 + 별칭. 별칭까지 넣는 건 표기가 달라지면 자동완성이
    # 다른 이웃을 물어오기 때문이다 (쇼파와 소파의 연관어가 같지 않다).
    for seed in names + aliases:
        for pat in L1_PATTERNS:
            absorb(seed, fetch("%s %s" % (seed, pat)))
    print("L1: %d items / %d queries" % (len(items), len(seen_queries)))

    # 레벨 2는 이번에 새로 나온 것만 넓힌다. 아는 품목을 또 파봐야 아는 것만 나온다.
    frontier = sorted(k for k in items if norm(k) not in known)
    for item in frontier:
        for pat in L2_PATTERNS:
            absorb(item, fetch("%s %s" % (item, pat)))
    print("L2: %d items / %d queries (frontier %d)"
          % (len(items), len(seen_queries), len(frontier)))

    out = []
    for item, rec in items.items():
        if norm(item) in known:
            continue
        out.append({
            "item": item,
            "freq": rec["freq"],
            "n_queries": len(rec["queries"]),
            "patterns": "|".join(p for p, _ in rec["patterns"].most_common(8)),
            "top_modifiers": "|".join(m for m, _ in rec["modifiers"].most_common(6)),
            "sample_suggestion": rec["sample"],
        })
    out.sort(key=lambda r: (-r["freq"], r["item"]))

    with io.open(OUT, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "item", "freq", "n_queries", "patterns", "top_modifiers", "sample_suggestion"])
        w.writeheader()
        w.writerows(out)
    with io.open(RAW, "w", encoding="utf-8") as f:
        for entry in session_log:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print("총 등장 %d개 중 새 후보 %d개 -> %s" % (len(items), len(out), OUT))
    print("질의 %d건 -> %s" % (len(session_log), RAW))


if __name__ == "__main__":
    main()
