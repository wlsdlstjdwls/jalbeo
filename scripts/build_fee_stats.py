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
    "진공청소기": "cheongsogi",
    "봉제인형": "inhyeong",
    "화장다이": "hwajangdae", "경대": "hwajangdae",
    "서랍": "seorapjang", "수납장": "seorapjang",
    "건조대": "ppalraegeonjodae", "빨래걸이": "ppalraegeonjodae",
    "자토바이": None,   # 자전거 오탐 방지용 자리표시
    # 대형폐기물 품목표의 '조명', '형광등'은 램프가 아니라 등기구다. 램프는
    # 형광등 수거함으로 가는 물건이라 애초에 대형폐기물 신고 대상이 아니다.
    # 그래서 형광등 페이지가 아니라 LED등(등기구) 페이지로 보낸다.
    "조명기구": "leddeung", "조명": "leddeung", "전등": "leddeung",
    "형광등": "leddeung", "led등": "leddeung", "전등틀": "leddeung",
}

# 과금 단위. 통짜 한 개에 얼마가 아니라 '단위 얼마'로 매기는 품목이 있다.
# 장롱은 1쪽당, 카펫은 3.3㎡당, 장판은 5m당, 깨진 유리는 kg당이다.
# 단위가 다른 값을 같은 중앙값에 섞으면 배수만큼 틀린다 (docs/12).
#
# '이상', '미만'이 붙은 규격 구간과 구별해야 한다. 냉장고 '300ℓ 이상'은
# 크기 구간이지 과금 단위가 아니다. 그래서 '당'이 붙은 표기만 단위로 본다.
UNIT_RE = re.compile(r"(1?\s*쪽\s*당|\(?1\s*쪽\)?|쪽당|1\s*짝|짝문|당\s*1쪽"
                     r"|짝당|폭당|칸당|한\s*짝당)")

# (단위 이름, 기준 단위, 수량+단위 정규식, 기준 단위 환산 계수)
# 수량이 안 적힌 'kg당', '㎡당'은 1로 본다.
MEASURED = [
    ("weight", "kg", re.compile(r"(\d+(?:\.\d+)?)?\s*(kg|㎏|킬로그램|킬로|톤|t)\s*당",
                                re.I), {"톤": 1000, "t": 1000}),
    ("area", "㎡", re.compile(r"(\d+(?:\.\d+)?)?\s*(㎡|m2|제곱미터|평)"
                             r"\s*(?:\([^)]*\))?\s*당", re.I), {"평": 3.3}),
    ("length", "m", re.compile(r"(\d+(?:\.\d+)?)?\s*(m|미터|cm|㎝)\s*당", re.I),
     {"cm": 0.01, "㎝": 0.01}),
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
UNIT_LABEL = {"whole": "전후", "panel": "1쪽당",
              "area": "1㎡당", "length": "1m당", "weight": "1kg당"}


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
    return table, sorted(table, key=len, reverse=True)


def match(token, table, order):
    if token in table:
        return table[token]
    # '전기밥솥'처럼 수식어가 붙은 표기는 접미 일치로 받는다. 긴 후보가 우선이다.
    for name in order:
        if len(token) > len(name) and token.endswith(name):
            return table[name]
    return None


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
            slug = match(tok, table, order)
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
        order = ["whole", "panel", "area", "length", "weight"]
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
        for unit in ("whole", "panel", "area", "length", "weight"):
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
