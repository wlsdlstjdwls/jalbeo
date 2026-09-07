# -*- coding: utf-8 -*-
"""절차 축 자동완성 크롤 2차 — 씨앗을 발행분에서 다시 뽑는다.

1차(`crawl_autocomplete_guides.py`)는 씨앗이 손으로 고른 절차 명사 41개였다.
확정 판단 13번대로 두 번째부터는 씨앗을 사람이 아니라 **발행분**에서 뽑는다.
품목 축이 `crawl_autocomplete_r2.py`에서 그렇게 했고, 절차 축도 같다.

씨앗 두 갈래:
  1. 발행된 가이드 5개의 title, seoTitle에서 뽑은 어절
  2. 1차 후보 394건의 머리말 중 1차 씨앗에 없던 것 (= 크롤이 새로 찾아낸 말)

어미도 1차와 겹치지 않게 갈았다. 1차는 신청/방법/가격 축이었고, 2차는
대상/기준/위반/대행처럼 제도의 경계를 묻는 축이다.

출력:
  data/keywords/candidates-guides2.csv       후보 질의 (미커버 우선 정렬)
  data/raw/autocomplete-crawl-guides2.jsonl  원본 응답
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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crawl_autocomplete_guides import SEEDS as R1_SEEDS

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

AC = "https://ac.search.naver.com/nx/ac"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEMS = os.path.join(ROOT, "site", "src", "data", "items.json")
GUIDE_DIR = os.path.join(ROOT, "site", "src", "content", "guides")
R1_CANDIDATES = os.path.join(ROOT, "data", "keywords", "candidates-guides.csv")
RAW = os.path.join(ROOT, "data", "raw", "autocomplete-crawl-guides2.jsonl")
OUT = os.path.join(ROOT, "data", "keywords", "candidates-guides2.csv")
DELAY = 0.35
MAX_QUERIES = 3000

# 2차 어미. 1차(신청/방법/가격/비용/수수료/어디서/파는곳/요일/시간/규격/종류/
# 과태료/환불)와 겹치지 않게 골랐다. 제도의 경계를 묻는 축이다.
L1_PATTERNS = (
    "대상", "기준", "안되는것", "가능", "불가", "위반", "신고", "대행",
    "업체", "전화번호", "인터넷", "앱", "반납", "무료", "차이",
)
L2_PATTERNS = ("기준", "대상", "업체")

NOISE = re.compile(
    r"(꿈|해몽|사주|주식|게임|노래|가사|드라마|영화|다이어트"
    # 낱개 어절 씨앗('신고', '신청', '인터넷')이 끌어온 딴 동네 행정 질의.
    r"|장려금|전입신고|출생신고|사망신고|혼인신고|종합소득세|소득세|연말정산"
    r"|세관|관세|여권|등본|초본|보조금|지원금|청약|실업급여|건강보험"
    r"|성실신고|부가세|세금|민원24|정부24)")
# 1차 REGION은 광역만 막아 부천, 수원 같은 기초 지자체가 새 나갔다. 넓혔다.
REGION = re.compile(
    r"(서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남"
    r"|경북|경남|제주|수원|용인|고양|성남|부천|화성|안산|남양주|안양|평택|시흥"
    r"|파주|김포|의정부|광명|하남|군포|오산|이천|양주|구리|안성|포천|의왕|여주"
    r"|천안|청주|전주|포항|창원|김해|진주|양산|구미|경주|목포|여수|순천|원주"
    r"|춘천|강릉|제천|아산|당진|서산|익산|군산|광양|거제|통영|시청|구청|주민센터"
    r"|[가-힣]{1,3}(시|군|구)\s)")

# 발행 가이드가 이미 답하는 축. 후보에서 지우지 않고 표시만 한다 —
# 지워 버리면 "그 가이드에 절을 붙일 자리"(판단 21번)를 못 본다.
GUIDE_COVER = {
    "jongryangje-bongtu": ("종량제", "쓰레기봉투", "봉투", "무단투기", "과태료"),
    "daehyeong-pyegimul-singo": ("대형폐기물", "스티커", "납부필증", "폐기물신고"),
    "pyegajeon-musang-sugeo": ("무상방문수거", "폐가전", "가전무료", "1599"),
    "pyegagu-mulyo-sugeo": ("폐가구", "가구무료", "재활용센터"),
    "heonot-bangmun-sugeo": ("헌옷", "고물상", "의류수거함", "폐지"),
}

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
    parts = s.split()
    return " ".join(parts[:2]) if len(parts) > 1 else s


# 낱개로는 절차를 못 가리키는 어절. 이걸 씨앗에 넣으면 자동완성이
# 쓰레기와 무관한 행정 질의(전입신고, 근로장려금 신청)로 끌려간다.
GENERIC = {
    "신고", "신청", "방법", "가격", "비용", "규격", "단가", "종류", "기준",
    "인터넷", "버리는", "파는", "kg", "곳", "것",
}
JOSA = re.compile(r"(와|과|의|를|을|이|가|은|는|도)$")


def guide_seeds():
    """발행 가이드 5개의 title, seoTitle에서 절차 표현을 뽑는다.

    낱개 어절은 절차를 못 가리킨다('신고'는 전입신고를 물어온다). 그래서
    두 어절 묶음을 먼저 만들고, 낱개는 그 자체로 절차인 것만 남긴다.
    """
    out = []
    for fn in sorted(os.listdir(GUIDE_DIR)):
        if not fn.endswith(".md"):
            continue
        text = io.open(os.path.join(GUIDE_DIR, fn), encoding="utf-8").read()
        for key in ("title", "seoTitle"):
            m = re.search(r'^%s:\s*"([^"]+)"' % key, text, re.M)
            if not m:
                continue
            toks = []
            for tok in re.split(r"[,\s]+", m.group(1)):
                tok = JOSA.sub("", tok.strip())
                if len(tok) >= 2:
                    toks.append(tok)
            for a, b in zip(toks, toks[1:]):
                if a in GENERIC and b in GENERIC:
                    continue
                out.append("%s %s" % (a, b))
            for tok in toks:
                if tok not in GENERIC and len(tok) >= 3:
                    out.append(tok)
    return out


def r1_seeds():
    """1차 후보의 머리말 중 1차 씨앗에 없던 것. 크롤이 새로 찾아낸 말이다."""
    r1_heads = {norm(head_of(s)) for s in R1_SEEDS} | {norm(s) for s in R1_SEEDS}
    rows = list(csv.DictReader(io.open(R1_CANDIDATES, encoding="utf-8-sig")))
    freq = Counter()
    for r in rows:
        freq[r["head"]] += int(r["freq"])
    out = []
    for head, n in freq.most_common():
        if norm(head) in r1_heads or REGION.search(head + " "):
            continue
        if len(out) >= 60:
            break
        out.append(head)
    return out


def main():
    rows = json.load(io.open(ITEMS, encoding="utf-8"))
    item_names = set()
    for r in rows:
        item_names.add(norm(r["name"]))
        for a in (r.get("aliases") or []):
            item_names.add(norm(a))

    g = guide_seeds()
    r1 = r1_seeds()
    seeds, seen = [], set()
    for s in g + r1:
        if norm(s) in seen or norm(s) in item_names:
            continue
        seen.add(norm(s))
        seeds.append(s)
    print("씨앗 %d개 = 가이드 유래 %d + 1차 머리말 유래 %d (중복, 품목 제외 후)"
          % (len(seeds), len(g), len(r1)))
    print("  가이드 유래: %s" % ", ".join(sorted(set(g))))
    print("  1차 유래 상위 20: %s" % ", ".join(r1[:20]))

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

    for seed in seeds:
        absorb(seed, fetch(seed))
    print("L0: %d개 질의 / %d건 수집" % (len(seen_queries), len(hits)))

    for seed in seeds:
        for pat in L1_PATTERNS:
            absorb(seed, fetch("%s %s" % (seed, pat)))
    print("L1: %d개 질의 / %d건 수집" % (len(seen_queries), len(hits)))

    seed_heads = {norm(head_of(s)) for s in seeds}
    frontier = sorted({head_of(s) for s in hits
                       if norm(head_of(s)) not in seed_heads})
    for head in frontier[:120]:
        for pat in L2_PATTERNS:
            absorb(head, fetch("%s %s" % (head, pat)))
    print("L2: %d개 질의 / %d건 수집 (frontier %d)"
          % (len(seen_queries), len(hits), len(frontier)))

    r1_known = {norm(r["query"]) for r in
                csv.DictReader(io.open(R1_CANDIDATES, encoding="utf-8-sig"))}

    out = []
    dropped_item = 0
    for s, rec in hits.items():
        first = s.split()[0]
        if norm(first) in item_names or norm(s) in item_names:
            dropped_item += 1
            continue
        n = norm(s)
        covered = ""
        for slug, keys in GUIDE_COVER.items():
            if any(k in n for k in keys):
                covered = slug
                break
        out.append({
            "query": s,
            "head": head_of(s),
            "freq": rec["freq"],
            "n_queries": len(rec["queries"]),
            "covered_by": covered,
            "in_round1": "y" if n in r1_known else "",
            "seeds": "|".join(sorted(rec["queries"])[:4]),
        })

    heads = Counter(r["head"] for r in out)
    # 미커버, 1차 미발견을 먼저 본다. 그게 2차를 돌린 이유다.
    out.sort(key=lambda r: (bool(r["covered_by"]), bool(r["in_round1"]),
                            -heads[r["head"]], r["head"], -r["freq"], r["query"]))

    with io.open(OUT, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["query", "head", "freq", "n_queries",
                                          "covered_by", "in_round1", "seeds"])
        w.writeheader()
        w.writerows(out)
    with io.open(RAW, "w", encoding="utf-8") as f:
        for entry in session_log:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    fresh = [r for r in out if not r["covered_by"] and not r["in_round1"]]
    print("수집 %d건 중 품목 축 제외 %d -> 후보 %d건" % (len(hits), dropped_item, len(out)))
    print("  그중 미커버 + 1차 미발견 = %d건" % len(fresh))
    fh = Counter(r["head"] for r in fresh)
    print("신규 머리말 상위: %s"
          % ", ".join("%s(%d)" % (h, n) for h, n in fh.most_common(20)))
    print("-> %s" % OUT)


if __name__ == "__main__":
    main()
