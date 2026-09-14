# -*- coding: utf-8 -*-
"""짧은 별칭이 남의 요금 행을 끌어오는지 전수 점검한다 (판단 83).

`build_fee_stats.py`는 품목명과 별칭으로 수수료 행을 모으는데, 짧은 이름은
접미 일치가 엉뚱한 물건을 끌어온다 ('공' -> 볼링공, '히터' -> 에어컨/온풍기,
'재' -> 목재/배관재). 본문은 멀쩡하고 요금표만 틀리므로 `check_fee_claims`도
못 잡는다 - 본문과 통계가 같은 출처라 서로 맞기 때문이다 (판단 47).

유일한 검사는 **행을 여는 것**이다 (판단 56, 70). 이 스크립트는 각 표기가
어떤 원본 품목 문자열을 끌어왔는지 펼쳐서, 사람이 한 번에 훑을 수 있게 한다.

    python scripts/audit_fee_aliases.py            # 의심 표기만
    python scripts/audit_fee_aliases.py --all      # 전부
    python scripts/audit_fee_aliases.py --name 공  # 한 표기만
"""
import io
import json
import os
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_fee_stats as B

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def slug_of(table, name):
    return table[name]


def main():
    argv = sys.argv[1:]
    show_all = "--all" in argv
    only = None
    if "--name" in argv:
        only = argv[argv.index("--name") + 1]

    items = json.load(io.open(B.ITEMS, encoding="utf-8"))
    import csv
    rows = list(csv.DictReader(io.open(B.FEES, encoding="utf-8")))
    table, order = B.build_matcher(items)

    by_slug = {it["slug"]: it for it in items}
    # 표기 -> slug 역인덱스. 어느 표기가 본체 이름인지 구분한다.
    owner_name = {re.sub(r"\s+", "", it["name"]): it["slug"] for it in items}

    # (slug, 매칭표기) -> {원본 item 문자열: [ (지역, 요금) ]}
    hits = defaultdict(lambda: defaultdict(list))
    denied = defaultdict(lambda: defaultdict(set))
    for r in rows:
        fee = int(r["fee"])
        if fee <= 0:
            continue
        region = (r["sido"] + " " + r["sigungu"]).strip()
        seen = set()
        for tok in B.tokens(r["item"]):
            # match()와 같은 순서로 돌되 어떤 표기에 걸렸는지를 기록한다
            hit = B.matched_name(tok, table, order)
            if not hit:
                continue
            # 행 쪽에서 거른 것은 이미 안 세는 행이다. 표시만 하고 넘긴다
            if any(hit == d and pat.search(r["item"]) for d, pat in B.DENY_ROWS):
                denied[slug_of(table, hit)][hit].add(r["item"])
                continue
            slug = table[hit]
            if slug in seen:
                continue
            seen.add(slug)
            hits[slug][hit].append((r["item"], region, fee, tok))

    flagged = 0
    for slug in sorted(hits):
        it = by_slug.get(slug)
        if not it:
            continue
        if only and only != it["name"] and only not in (it.get("aliases") or []):
            continue
        for hit, rec in sorted(hits[slug].items(), key=lambda kv: -len(kv[1])):
            is_owner = owner_name.get(hit) == slug
            # 의심 기준: 본체 이름이 아니고 3자 이하이거나, 접미 일치로만 걸린 행이 있다
            suffix_rows = [x for x in rec if x[3] != hit]
            suspicious = (not is_owner and len(hit) <= 3) or (len(hit) <= 3 and suffix_rows)
            if not (show_all or only or suspicious):
                continue
            flagged += 1
            regions = {x[1] for x in rec}
            kinds = {}
            for raw, region, fee, tok in rec:
                kinds.setdefault(raw, []).append((region, fee))
            tag = "본체" if is_owner else "별칭"
            print("\n[%s] %s  <- %s '%s'  (%d행 / %d지역)"
                  % (slug, it["name"], tag, hit, len(rec), len(regions)))
            for raw in sorted(kinds, key=lambda k: -len(kinds[k]))[:12]:
                sample = kinds[raw][:3]
                print("    %-34s %s%s"
                      % (raw[:34],
                         ", ".join("%s %s원" % (r, f) for r, f in sample),
                         " ..." if len(kinds[raw]) > 3 else ""))
            if len(kinds) > 12:
                print("    ... 원본 표기 %d종 더" % (len(kinds) - 12))

    if denied:
        print("")
        print("=== DENY_ROWS로 거른 행 (통계에 안 들어감) ===")
        for slug in sorted(denied):
            nm = by_slug[slug]["name"] if slug in by_slug else slug
            for hit, raws in denied[slug].items():
                print("  %-12s '%s' <- %s" % (nm, hit, ", ".join(sorted(raws))[:100]))

    print("\n출력 %d건" % flagged)


if __name__ == "__main__":
    main()
