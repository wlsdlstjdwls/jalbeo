# -*- coding: utf-8 -*-
"""씨앗 배치 실측 결과를 품목 단위로 합산한다 (어미 무관 범용).

`gate1_batch2_aggregate.py`는 발행 품목(items.json)에 붙이는 게 목적이라
아직 페이지가 없는 신규 후보를 못 센다. 이 스크립트는 items.json을 안 보고
키워드에서 어미만 떼어 품목을 만든다.

사용법: python scripts/gate1_seed_aggregate.py <입력디렉터리> <출력csv>
  예)   python scripts/gate1_seed_aggregate.py data/keywords/gate1-3 \
              data/keywords/gate1-volumes-3.csv

'<10'은 5로 근사한다. 씨앗으로 안 넣은 어미는 0이 아니라 빈칸이다.
"""
import csv
import glob
import os
import re
import sys

import openpyxl

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SUFFIXES = ["버리는법", "분리수거"]


def volume(cell):
    if cell is None:
        return 0
    s = str(cell).strip().replace(",", "")
    if s.startswith("<"):
        return 5
    return int(s) if s.isdigit() else 0


def main():
    src, out = sys.argv[1], sys.argv[2]
    files = sorted(glob.glob(os.path.join(src, "*.xlsx")))
    best = {}
    for path in files:
        ws = openpyxl.load_workbook(path, read_only=True).worksheets[0]
        for i, row in enumerate(ws.iter_rows(values_only=True)):
            if i < 2 or not row[0]:
                continue
            kw = re.sub(r"\s+", "", str(row[0]))
            best[kw] = max(best.get(kw, 0), volume(row[1]) + volume(row[2]))

    items = {}
    for kw, vol in best.items():
        for suf in SUFFIXES:
            if kw.endswith(suf):
                name = kw[: -len(suf)]
                items.setdefault(name, {})[suf] = vol
                break

    rows = []
    for name, hit in items.items():
        rec = {"item": name}
        for suf in SUFFIXES:
            rec[suf] = hit.get(suf, "")
        rec["total"] = sum(hit.values())
        rows.append(rec)
    rows.sort(key=lambda r: -r["total"])

    with open(out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["item"] + SUFFIXES + ["total"])
        w.writeheader()
        w.writerows(rows)

    off = [k for k in best if not any(k.endswith(s) for s in SUFFIXES)]
    print("파일 %d개 / 키워드 %d개 -> 품목 %d개 (어미 밖 %d개 버림)"
          % (len(files), len(best), len(rows), len(off)))
    print()
    fmt = lambda v: "-" if v == "" else format(v, ",")
    print("%-12s %9s %9s %9s" % ("품목", "버리는법", "분리수거", "합계"))
    for r in rows:
        print("%-12s %9s %9s %9s"
              % (r["item"][:12], fmt(r["버리는법"]), fmt(r["분리수거"]), fmt(r["total"])))
    print()
    print("-> %s" % out)


if __name__ == "__main__":
    main()
