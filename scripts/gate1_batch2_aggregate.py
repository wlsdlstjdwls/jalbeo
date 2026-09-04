# -*- coding: utf-8 -*-
"""실측 2차(5차 확장 신규 품목) 검색량 집계.

입력: data/keywords/gate1-2/*.xlsx  (키워드도구 '다운로드' 산출물)
출력: data/keywords/gate1-volumes-2.csv

1차(`gate1_aggregate.py`)는 게이트 판정용이라 연관어까지 느슨하게 긁었다.
2차는 판정이 아니라 우선순위용이므로, 씨앗으로 넣은 두 어미만 본다.
  A안 `{품목}버리는법` / B안 `{품목}분리수거`
씨앗이 아닌 연관어(쓰레기봉투가격 등)는 품목축이 아니므로 버린다.

'<10'은 5로 근사한다. 같은 키워드가 여러 파일에 나오면 최대값만 센다.
"""
import csv
import glob
import json
import os
import re
import sys

import openpyxl

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data", "keywords", "gate1-2", "*.xlsx")
ITEMS = os.path.join(ROOT, "site", "src", "data", "items.json")
OUT = os.path.join(ROOT, "data", "keywords", "gate1-volumes-2.csv")

SUFFIXES = ["버리는법", "분리수거"]


def volume(cell):
    if cell is None:
        return 0
    s = str(cell).strip().replace(",", "")
    if s.startswith("<"):
        return 5
    return int(s) if s.isdigit() else 0


def norm(s):
    return re.sub(r"\s+", "", s)


def read_all():
    best = {}
    files = sorted(glob.glob(SRC))
    for path in files:
        ws = openpyxl.load_workbook(path, read_only=True).worksheets[0]
        for i, row in enumerate(ws.iter_rows(values_only=True)):
            if i < 2 or not row[0]:
                continue
            kw = norm(str(row[0]))
            best[kw] = max(best.get(kw, 0), volume(row[1]) + volume(row[2]))
    return files, best


def main():
    items = json.load(open(ITEMS, encoding="utf-8"))
    files, best = read_all()

    rows = []
    used = set()
    for it in items:
        keys = [norm(it["name"])] + [norm(a) for a in it.get("aliases", [])]
        rec = {"slug": it["slug"], "name": it["name"],
               "known_volume": it["monthly_volume"] if it["monthly_volume"] is not None else ""}
        total = 0
        hit = False
        for suf in SUFFIXES:
            vol = None
            for k in keys:
                kw = k + suf
                if kw in best:
                    vol = max(vol or 0, best[kw])
                    used.add(kw)
                    hit = True
            # 안 돌린 어미는 0이 아니라 빈칸이다. 없는 숫자를 지어내지 않는다
            rec[suf] = "" if vol is None else vol
            total += vol or 0
        if not hit:
            continue
        rec["total"] = total
        rows.append(rec)

    rows.sort(key=lambda r: -r["total"])
    with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["slug", "name", "버리는법", "분리수거",
                                          "total", "known_volume"])
        w.writeheader()
        w.writerows(rows)

    dropped = sorted(set(best) - used, key=lambda k: -best[k])
    missing = [it["name"] for it in items
               if it["monthly_volume"] is None
               and it["slug"] not in {r["slug"] for r in rows}]

    print("파일 %d개 / 키워드 %d개 -> 품목 %d개 측정" % (len(files), len(best), len(rows)))
    print("씨앗 밖 연관어 %d개 버림 (상위: %s)"
          % (len(dropped), ", ".join(dropped[:5])))
    print("아직 미측정: %d개 %s" % (len(missing), missing))
    print()
    print("%-14s %9s %9s %9s" % ("품목", "버리는법", "분리수거", "합계"))
    fmt = lambda v: "-" if v == "" else format(v, ",")
    for r in rows[:25]:
        print("%-14s %9s %9s %9s"
              % (r["name"][:14], fmt(r["버리는법"]),
                 fmt(r["분리수거"]), fmt(r["total"])))
    half = [r["name"] for r in rows if "" in (r["버리는법"], r["분리수거"])]
    print("")
    print("어미 한쪽만 측정된 품목 %d개: %s" % (len(half), ", ".join(half)))
    print("\n-> %s" % OUT)


if __name__ == "__main__":
    main()

