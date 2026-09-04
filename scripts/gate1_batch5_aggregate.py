# -*- coding: utf-8 -*-
"""실측 5차 집계 — 재크롤 2차 신규 후보 + 보류 2개.

입력: data/keywords/gate1-5/*.xlsx  (키워드도구 '다운로드' 산출물)
출력: data/keywords/gate1-volumes-5.csv

2차/4차 집계기(`gate1_batch2_aggregate.py`)는 대상이 items.json이다. 5차는
**아직 발행되지 않은 후보**를 재므로 대상 목록이 다르다. 그래서 별도로 둔다.

씨앗으로 넣은 어미만 본다. 후보는 두 어미(`버리는법`, `분리수거`),
보류 2개(에어컨, 오븐)는 서비스 어미(`무상수거`, `철거비용`)다.
'<10'은 5로 근사하고, 안 돌린 어미는 0이 아니라 빈칸이다.
"""
import csv
import glob
import io
import os
import re
import sys

import openpyxl

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KW = os.path.join(ROOT, "data", "keywords")
SRC = os.path.join(KW, "gate1-5", "*.xlsx")
CAND = os.path.join(KW, "candidates-r2.csv")
OUT = os.path.join(KW, "gate1-volumes-5.csv")

SUFFIXES = ["버리는법", "분리수거"]
HOLD_SUFFIXES = ["무상수거", "철거비용"]
HOLD = ["에어컨", "오븐"]

# 3차와 같은 기준선. 두 어미 합계가 이보다 낮으면 페이지를 만들지 않는다.
BASELINE = 300


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


def measure(name, sufs, best, used):
    rec, total, hit = {}, 0, False
    for suf in sufs:
        kw = norm(name) + suf
        if kw in best:
            rec[suf] = best[kw]
            used.add(kw)
            total += best[kw]
            hit = True
        else:
            rec[suf] = ""
    return (rec, total) if hit else (None, 0)


def main():
    if not glob.glob(SRC):
        sys.exit("%s 에 엑셀이 없다. gate1-batches-5.md 묶음을 먼저 돌린다." % SRC)

    files, best = read_all()
    used = set()

    names = [r["item"] for r in csv.DictReader(io.open(CAND, encoding="utf-8-sig"))]

    rows = []
    for name in names:
        rec, total = measure(name, SUFFIXES, best, used)
        if rec is None:
            continue
        rows.append({"item": name, "kind": "후보",
                     "a": rec[SUFFIXES[0]], "b": rec[SUFFIXES[1]], "total": total,
                     "verdict": "발행" if total >= BASELINE else "보류"})
    rows.sort(key=lambda r: -r["total"])

    hold_rows = []
    for name in HOLD:
        rec, total = measure(name, HOLD_SUFFIXES, best, used)
        if rec is None:
            continue
        hold_rows.append({"item": name, "kind": "보류재측정",
                          "a": rec[HOLD_SUFFIXES[0]], "b": rec[HOLD_SUFFIXES[1]],
                          "total": total, "verdict": "판단필요"})

    all_rows = rows + hold_rows
    with io.open(OUT, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["item", "kind", "a", "b", "total", "verdict"])
        w.writeheader()
        w.writerows(all_rows)

    dropped = sorted(set(best) - used, key=lambda k: -best[k])
    passed = [r for r in rows if r["verdict"] == "발행"]

    print("파일 %d개 / 키워드 %d개 -> 후보 %d개 측정, 보류 %d개"
          % (len(files), len(best), len(rows), len(hold_rows)))
    print("씨앗 밖 연관어 %d개 버림 (상위: %s)" % (len(dropped), ", ".join(dropped[:5])))
    print("기준선 %d 통과: %d개 / 합계 %s"
          % (BASELINE, len(passed), format(sum(r["total"] for r in passed), ",")))
    fmt = lambda v: "-" if v == "" else format(v, ",")

    def table(title, rows_, sufs):
        print()
        print(title)
        print("%-14s %10s %10s %10s  %s" % ("품목", sufs[0], sufs[1], "합계", "판정"))
        for r in rows_:
            print("%-14s %10s %10s %10s  %s"
                  % (r["item"][:14], fmt(r["a"]), fmt(r["b"]),
                     format(r["total"], ","), r["verdict"]))

    # 보류 2개는 어미가 달라 표를 따로 낸다. 한 표에 놓으면 머리글이 거짓말을 한다.
    table("[후보]", rows[:40], SUFFIXES)
    if hold_rows:
        table("[보류 재측정]", hold_rows, HOLD_SUFFIXES)
    print("\n-> %s" % OUT)


if __name__ == "__main__":
    main()
