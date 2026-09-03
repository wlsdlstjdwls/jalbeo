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
    "옷장": "jangrong", "장농": "jangrong",
    "진공청소기": "cheongsogi",
    "봉제인형": "inhyeong",
    "화장다이": "hwajangdae", "경대": "hwajangdae",
    "서랍": "seorapjang", "수납장": "seorapjang",
    "건조대": "ppalraegeonjodae", "빨래걸이": "ppalraegeonjodae",
    "자토바이": None,   # 자전거 오탐 방지용 자리표시
}

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


def main():
    items = json.load(io.open(ITEMS, encoding="utf-8"))
    rows = list(csv.DictReader(io.open(FEES, encoding="utf-8")))
    table, order = build_matcher(items)

    # slug → 지역별 금액. 같은 지역에 여러 규격이 있으면 최빈 구간을 쓰려고 다 모은다.
    buckets = defaultdict(lambda: defaultdict(list))
    for r in rows:
        fee = int(r["fee"])
        if fee <= 0:
            continue
        seen = set()
        for tok in tokens(r["item"]):
            slug = match(tok, table, order)
            if slug and slug not in seen:
                seen.add(slug)
                region = (r["sido"] + " " + r["sigungu"]).strip()
                buckets[slug][region].append((fee, r["spec"], r["base_date"], r["source_url"]))

    out = {}
    for slug, regions in buckets.items():
        # 지역마다 대표값 하나(중앙값)를 뽑아 지역 간 비교가 되게 한다.
        per_region = {}
        for reg, vals in regions.items():
            fees = sorted(v[0] for v in vals)
            per_region[reg] = int(statistics.median(fees))
        vals = sorted(per_region.values())
        if len(vals) < 3:
            continue
        q1 = vals[len(vals) // 4]
        q3 = vals[(len(vals) * 3) // 4]
        cheapest = min(per_region.items(), key=lambda kv: kv[1])
        dearest = max(per_region.items(), key=lambda kv: kv[1])
        sample = next(iter(regions.values()))[0]
        out[slug] = {
            "median": int(statistics.median(vals)),
            "min": vals[0],
            "max": vals[-1],
            "q1": q1,
            "q3": q3,
            "regions": len(vals),
            "cheapest": {"region": cheapest[0], "fee": cheapest[1]},
            "dearest": {"region": dearest[0], "fee": dearest[1]},
            "base_date": sample[2],
            "by_region": dict(sorted(per_region.items(), key=lambda kv: kv[1])),
        }

    io.open(OUT, "w", encoding="utf-8").write(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n"
    )

    print("품목 %d개 집계" % len(out))
    for it in items:
        s = out.get(it["slug"])
        if s:
            print("  %-8s %2d지역  중앙 %6s원  %s~%s"
                  % (it["name"], s["regions"], f"{s['median']:,}",
                     f"{s['min']:,}", f"{s['max']:,}"))
        else:
            print("  %-8s  —" % it["name"])


if __name__ == "__main__":
    main()
