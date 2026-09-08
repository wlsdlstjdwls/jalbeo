# -*- coding: utf-8 -*-
"""과금 단위 파서가 못 읽고 지나간 행을 찾는다.

`build_fee_stats.unit_of()`는 spec에 '당', '마다', '기준'이 붙은 표기만
과금 단위로 본다(확정 판단 24). 그 표기 목록이 정규식이라 **적는 방식이
하나 늘어나면 조용히 통짜로 들어간다.** 단위를 못 읽으면 큰 값이 작은 값으로
둔갑하므로 결손이 한 방향으로만 틀린다 - 강북구가 '마다'로 적는 55행을
못 읽어 어느 품목에서나 최저가로 찍혔던 사고가 그것이다(docs/46, 판단 59).

그 사고를 미리 잡는 검사다. 규칙은 하나다.

    물리 단위(㎡, m, kg, ℓ, 쪽 ...) 바로 뒤에 '당/마다/기준'이 붙어 있는데
    unit_of()가 'whole'을 돌려주면 못 읽은 것이다.

**개당, 장당, 대당은 여기서 뺀다.** 그건 물건 하나를 세는 말이라 통짜가
맞다. 이불 '장당'은 이불 한 장 값이고 장롱 '쪽당'은 한 짝 값이라 다르다.

'이상', '미만' 같은 구간 표시가 사이에 끼면 규격 구간이지 단위가 아니다
(냉장고 '300ℓ 이상'). 그건 걸러서 센다.

    python scripts/check_fee_units.py
어긋남이 있으면 exit 1.
"""
import csv
import importlib.util
import io
import os
import re
import sys
from collections import Counter, defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEES = os.path.join(ROOT, "data", "processed", "fees.csv")

# 물리 단위만 넣는다. 개, 장, 대, 매는 물건을 세는 말이라 통짜가 맞다.
MEASURE = (r"(?:kg|㎏|킬로그램|킬로|톤|㎡|m2|m²|제곱미터|평|㎥|m3|세제곱미터"
           r"|ℓ|리터|\d\s*[lL]|미터|cm|㎝|\d\s*m|쪽|짝|폭|칸|구|단)")
TAIL = re.compile(r"(당|마다|기준)")
NEAR = re.compile(MEASURE + r"\s*(?:\([^)]*\))?\s*$", re.I)
RANGE = re.compile(r"(이상|미만|이하|초과|~)")
WINDOW = 10


def load_unit_of():
    path = os.path.join(ROOT, "scripts", "build_fee_stats.py")
    spec = importlib.util.spec_from_file_location("bfs", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.unit_of


def main():
    unit_of = load_unit_of()
    rows = list(csv.DictReader(io.open(FEES, encoding="utf-8-sig")))
    miss = Counter()
    where = defaultdict(list)
    for r in rows:
        item, spec = r.get("item") or "", r.get("spec") or ""
        text = (item + " " + spec).strip()
        if unit_of(item, spec)[0] != "whole":
            continue
        for m in TAIL.finditer(text):
            win = text[max(0, m.start() - WINDOW):m.start()]
            if RANGE.search(win) or not NEAR.search(win):
                continue
            key = (win.strip() + m.group(1))[-12:]
            miss[key] += 1
            where[key].append("%s %s / %s" % (r["sido"][:2], r["sigungu"], text[:52]))
            break

    print("%s행 검사" % f"{len(rows):,}")
    if not miss:
        print("통짜로 샌 단위 표기 없음")
        return 0
    print("!! 단위처럼 보이는데 통짜로 들어간 표기 %d종, %d행"
          % (len(miss), sum(miss.values())))
    for key, n in miss.most_common():
        print("  %-14s %3d행  %s" % (key, n, where[key][0]))
    print("\nbuild_fee_stats.py의 MEASURED 정규식에 그 표기를 넣거나,"
          "\n물건을 세는 말이면 MEASURE에서 빼서 이 검사를 다시 돌린다.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
