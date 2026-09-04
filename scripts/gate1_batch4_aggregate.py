# -*- coding: utf-8 -*-
"""실측 4차(1차 품목 두 어미 재측정) 검색량 집계.

입력: data/keywords/gate1-4/*.xlsx  (키워드도구 '다운로드' 산출물 35개)
출력: data/keywords/gate1-volumes-4.csv

`docs/14`가 남긴 숙제다. 1차(`gate1-volumes.csv`)는 씨앗 실측이 아니라 연관어
덤프였다. 품목마다 걸린 어미가 달라 합계의 기준이 제각각이었다. 2차와 같은 자
(`버리는법` + `분리수거` 두 씨앗)로 다시 잰다. 판정용이 아니라 정렬 기준 통일용.

2차와 같은 규칙:
  - 씨앗으로 넣은 두 어미만 본다. 연관어는 품목축이 아니므로 버린다
  - '<10'은 5로 근사한다. 같은 키워드가 여러 파일에 나오면 최대값만 센다
  - 안 돌린 어미는 0이 아니라 빈칸이다
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
KW = os.path.join(ROOT, "data", "keywords")
SRC = os.path.join(KW, "gate1-4", "*.xlsx")
ITEMS = os.path.join(ROOT, "site", "src", "data", "items.json")
V1 = os.path.join(KW, "gate1-volumes.csv")
OUT = os.path.join(KW, "gate1-volumes-4.csv")

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


def read_v1():
    """1차 덤프의 품목별 합계. 재측정 전후 비교용이다."""
    tot = {}
    with open(V1, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["on_axis"] == "1" and r["item"]:
                tot[r["item"]] = tot.get(r["item"], 0) + int(r["volume"])
    return tot


def main():
    items = json.load(open(ITEMS, encoding="utf-8"))
    files, best = read_all()
    v1 = read_v1()

    rows = []
    used = set()
    for it in items:
        keys = [norm(it["name"])] + [norm(a) for a in it.get("aliases", [])]
        rec = {"slug": it["slug"], "name": it["name"]}
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
            rec[suf] = "" if vol is None else vol
            total += vol or 0
        if not hit:
            continue
        rec["total"] = total
        old = v1.get(it["name"])
        rec["v1_total"] = old if old is not None else ""
        rec["ratio"] = "%.2f" % (total / old) if old else ""
        rows.append(rec)

    rows.sort(key=lambda r: -r["total"])
    with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["slug", "name", "버리는법", "분리수거",
                                          "total", "v1_total", "ratio"])
        w.writeheader()
        w.writerows(rows)

    dropped = sorted(set(best) - used, key=lambda k: -best[k])
    print("파일 %d개 / 키워드 %d개 -> 품목 %d개 측정" % (len(files), len(best), len(rows)))
    print("씨앗 밖 연관어 %d개 버림 (상위: %s)"
          % (len(dropped), ", ".join(dropped[:5])))
    print("4차 합계 %s / 같은 품목 1차 합계 %s"
          % (format(sum(r["total"] for r in rows), ","),
             format(sum(r["v1_total"] or 0 for r in rows), ",")))
    print()
    print("%-14s %9s %9s %9s %9s %6s"
          % ("품목", "버리는법", "분리수거", "합계", "1차", "비율"))
    fmt = lambda v: "-" if v == "" else format(v, ",")
    for r in rows[:30]:
        print("%-14s %9s %9s %9s %9s %6s"
              % (r["name"][:14], fmt(r["버리는법"]), fmt(r["분리수거"]),
                 fmt(r["total"]), fmt(r["v1_total"]), r["ratio"] or "-"))
    half = [r["name"] for r in rows if "" in (r["버리는법"], r["분리수거"])]
    print("\n어미 한쪽만 측정된 품목 %d개: %s" % (len(half), ", ".join(half)))
    print("\n-> %s" % OUT)


if __name__ == "__main__":
    main()
