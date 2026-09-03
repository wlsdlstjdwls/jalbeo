# -*- coding: utf-8 -*-
"""기존 조사 결과 -> Supabase 시드 CSV.

출력: db/seed/items.csv             (집필 대기열 포함 품목 마스터)
      db/seed/guideline_verdicts.csv (환경부 별표1 판정 73건)

품목은 게이트 1에서 검색량이 실측된 것만 담는다. 볼륨이 없는 품목은
'모름'이지 '0'이 아니지만(docs/09), 작업 우선순위를 정할 근거가 없으므로 제외한다.
"""
import csv
import json
import os
import re
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = os.path.join(ROOT, "db", "seed")

# 국어의 로마자 표기법(2000) 기준. 음운 변화는 반영하지 않는다 — slug 용도라 충분하다.
ONSET = ["g", "kk", "n", "d", "tt", "r", "m", "b", "pp", "s", "ss", "",
         "j", "jj", "ch", "k", "t", "p", "h"]
NUCLEUS = ["a", "ae", "ya", "yae", "eo", "e", "yeo", "ye", "o", "wa", "wae",
           "oe", "yo", "u", "wo", "we", "wi", "yu", "eu", "ui", "i"]
CODA = ["", "k", "k", "k", "n", "n", "n", "t", "l", "k", "m", "l", "l", "l",
        "p", "l", "m", "p", "p", "t", "t", "ng", "t", "t", "k", "t", "p", "t"]
assert len(ONSET) == 19 and len(NUCLEUS) == 21 and len(CODA) == 28


def romanize(text):
    out = []
    for ch in text:
        code = ord(ch)
        if 0xAC00 <= code <= 0xD7A3:
            i = code - 0xAC00
            out.append(ONSET[i // 588] + NUCLEUS[(i % 588) // 28] + CODA[i % 28])
        elif ch.isalnum():
            out.append(ch.lower())
        else:
            out.append("-")
    slug = re.sub(r"-+", "-", "".join(out)).strip("-")
    return slug


def load_volumes():
    """게이트 1 실측 -> 품목별 합계."""
    path = os.path.join(ROOT, "data", "keywords", "gate1-volumes.csv")
    vol = defaultdict(int)
    with open(path, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["on_axis"] == "1" and r["item"]:
                vol[r["item"]] += int(r["volume"])
    return vol


def load_region_varies():
    """자동완성에서 지역 수식어가 붙은 품목 (docs/07)."""
    path = os.path.join(ROOT, "data", "keywords", "items.csv")
    out = {}
    with open(path, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            out[re.sub(r"\s+", "", r["item"])] = r["has_region_modifier"] == "1"
            for v in filter(None, r["variants"].split("|")):
                out.setdefault(re.sub(r"\s+", "", v), r["has_region_modifier"] == "1")
    return out


def load_competitor():
    """블리스고 보유 품목 (docs/10). 사이트맵에서 뽑은 품목명."""
    path = os.path.join(ROOT, "data", "raw", "blisgo-items.json")
    if not os.path.exists(path):
        return set()
    with open(path, encoding="utf-8") as f:
        return {re.sub(r"\s+", "", n) for n in json.load(f)}


def main():
    vol = load_volumes()
    varies = load_region_varies()
    competitor = load_competitor()
    norm = lambda s: re.sub(r"\s+", "", s)

    rows = []
    seen = set()
    for name, v in sorted(vol.items(), key=lambda x: -x[1]):
        slug = romanize(name)
        if not slug or slug in seen:
            continue
        seen.add(slug)
        n = norm(name)
        rows.append({
            "slug": slug,
            "name": name,
            "monthly_volume": v,
            "region_varies": "true" if varies.get(n) else "false",
            "competitor_has": "true" if any(n in c or c in n for c in competitor) else "false",
            "housing_split": "false",
            "published": "false",
        })

    with open(os.path.join(SEED, "items.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # 환경부 별표1 판정
    src = os.path.join(ROOT, "data", "guidelines", "item-verdicts.csv")
    rules = json.load(open(os.path.join(ROOT, "data", "guidelines", "disposal-rules.json"),
                           encoding="utf-8"))["source"]
    gv = []
    with open(src, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            gv.append({
                "item_name": r["item"], "verdict": r["verdict"],
                "category": r["category"], "subitem": r["subitem"], "basis": r["basis"],
                "source_url": rules["source_url"], "as_of": rules["issued"],
            })
    with open(os.path.join(SEED, "guideline_verdicts.csv"), "w",
              encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(gv[0].keys()))
        w.writeheader()
        w.writerows(gv)

    gap = [r for r in rows if r["competitor_has"] == "false"]
    print("items.csv              %d개 (블리스고 미보유 %d개)" % (len(rows), len(gap)))
    print("guideline_verdicts.csv %d건" % len(gv))
    print("\n블리스고 빈틈 상위 20 — 파일럿 후보:")
    for r in gap[:20]:
        print("  %-12s %-22s %8s" % (r["name"], r["slug"], format(r["monthly_volume"], ",")))


if __name__ == "__main__":
    main()
