# -*- coding: utf-8 -*-
"""실측 8차 집계 -- 절차 축 가이드 후보 8주제.

입력: data/keywords/gate1-8/*.xlsx  (키워드도구 '다운로드' 산출물)
      scripts/build_guide_batch.py   (주제 -> 키워드 목록. 계획서와 같은 자를 쓴다)
출력: data/keywords/gate1-volumes-8.csv

품목 집계기(gate1_batch7_aggregate.py)와 다른 점 하나: 어미 두 개를 더하지 않는다.
절차는 어미가 주제마다 달라서, 그 주제에 속한 키워드를 전부 더한 값이 주제의 크기다.
`docs/14`가 폐가전 무상수거를 145,940으로 잡은 방식과 같다.

'<10'은 5로 근사하고, 안 걸린 키워드는 0이 아니라 빈칸이다.
"""
import csv
import glob
import io
import os
import re
import sys

import openpyxl

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_guide_batch import TOPICS

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KW = os.path.join(ROOT, "data", "keywords")
SRC = os.path.join(KW, "gate1-8", "*.xlsx")
OUT = os.path.join(KW, "gate1-volumes-8.csv")

# 하한선. 발행된 가이드 중 제일 작은 폐가구 무료수거가 16,035이다 (docs/14).
FLOOR = 16035


def volume(cell):
    if cell is None:
        return 0
    s = str(cell).strip().replace(",", "")
    if s.startswith("<"):
        return 5
    return int(s) if s.isdigit() else 0


def norm(s):
    return re.sub(r"\s+", "", str(s)).lower()


def read_all():
    best = {}
    files = sorted(glob.glob(SRC))
    for path in files:
        ws = openpyxl.load_workbook(path, read_only=True).worksheets[0]
        for i, row in enumerate(ws.iter_rows(values_only=True)):
            if i < 2 or not row[0]:
                continue
            kw = norm(row[0])
            best[kw] = max(best.get(kw, 0), volume(row[1]) + volume(row[2]))
    return files, best


def main():
    if not glob.glob(SRC):
        sys.exit("%s 에 엑셀이 없다. gate1-batches-8.md 묶음을 먼저 돌린다." % SRC)

    files, best = read_all()
    used = set()
    rows, missing = [], []

    for label, n_auto, words in TOPICS:
        for w in words:
            k = norm(w)
            if k in best:
                used.add(k)
                rows.append({"topic": label, "keyword": w, "volume": best[k],
                             "auto_freq": n_auto})
            else:
                missing.append(w)
                rows.append({"topic": label, "keyword": w, "volume": "",
                             "auto_freq": n_auto})

    with io.open(OUT, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["topic", "keyword", "volume", "auto_freq"])
        w.writeheader()
        w.writerows(rows)

    totals = []
    for label, n_auto, words in TOPICS:
        vals = [r["volume"] for r in rows if r["topic"] == label and r["volume"] != ""]
        totals.append((sum(vals), label, len(vals), len(words), n_auto,
                       max(vals) if vals else 0,
                       max([r for r in rows if r["topic"] == label and r["volume"] != ""],
                           key=lambda r: r["volume"])["keyword"] if vals else ""))
    totals.sort(reverse=True)

    print("파일 %d개 / 수집 키워드 %d개 / 계획 키워드 %d개 측정"
          % (len(files), len(best), len(used)))
    if missing:
        print("미측정 %d개: %s" % (len(missing), ", ".join(missing)))
    print()
    print("%-32s %9s %8s %6s  %s" % ("주제", "합계", "최대키워드", "자동완성", "판정"))
    for total, label, hit, planned, n_auto, top, topkw in totals:
        verdict = "발행" if total >= FLOOR else "보류"
        print("%-32s %9s %8s %6d  %s  (%s %s)"
              % (label[:32], format(total, ","), format(top, ","), n_auto, verdict,
                 topkw, format(top, ",")))
    print("\n하한선 %s (폐가구 가이드) 이상: %d주제"
          % (format(FLOOR, ","), sum(1 for t in totals if t[0] >= FLOOR)))

    print("\n키워드별 상세")
    for total, label, hit, planned, n_auto, top, topkw in totals:
        print("\n[%s] 합계 %s" % (label, format(total, ",")))
        for r in sorted([r for r in rows if r["topic"] == label],
                        key=lambda r: -(r["volume"] or 0)):
            print("   %-26s %9s" % (r["keyword"],
                                    "-" if r["volume"] == "" else format(r["volume"], ",")))
    print("\n-> %s" % OUT)


if __name__ == "__main__":
    main()
