# -*- coding: utf-8 -*-
"""실측 9차 집계 -- PP마대.

입력: data/keywords/gate1-9/*.xlsx  (키워드도구 '다운로드' 산출물)
      scripts/build_guide_batch2.py  (주제 -> 키워드 목록)
출력: data/keywords/gate1-volumes-9.csv

8차 집계기와 다른 점 하나: **판정 합계에 참고 주제를 안 넣는다.**
'PP마대 중고', '톤마대'는 포장 자재를 사려는 검색이라 이 사이트가 답할
질문이 아니다. 재기는 재되 하한선 판정에서는 뺀다.

'<10'은 5로 근사하고, 안 걸린 키워드는 0이 아니라 빈칸이다 (미측정은 null).
"""
import csv
import glob
import io
import os
import re
import sys

import openpyxl

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_guide_batch2 import TOPICS  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KW = os.path.join(ROOT, "data", "keywords")
SRC = os.path.join(KW, "gate1-9", "*.xlsx")
OUT = os.path.join(KW, "gate1-volumes-9.csv")

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
        sys.exit("%s 에 엑셀이 없다. gate1-batches-9.md 묶음을 먼저 돌린다." % SRC)

    files, best = read_all()
    rows, missing = [], []

    for label, counts, words in TOPICS:
        for w in words:
            k = norm(w)
            v = best.get(k)
            if v is None:
                missing.append(w)
            rows.append({"topic": label, "counts": "y" if counts else "",
                         "keyword": w, "volume": "" if v is None else v})

    with io.open(OUT, "w", encoding="utf-8-sig", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=["topic", "counts", "keyword", "volume"])
        wr.writeheader()
        wr.writerows(rows)

    print("파일 %d개 / 수집 키워드 %d개 / 계획 %d개 중 %d개 측정"
          % (len(files), len(best), len(rows), len(rows) - len(missing)))
    if missing:
        print("조회에 안 걸림 %d개: %s" % (len(missing), ", ".join(missing)))

    judged = 0
    for label, counts, words in TOPICS:
        vals = [r["volume"] for r in rows if r["topic"] == label and r["volume"] != ""]
        total = sum(vals)
        if counts:
            judged = total
        print("\n[%s] 합계 %s%s"
              % (label, format(total, ","), "" if counts else "  (판정 제외)"))
        for r in sorted([r for r in rows if r["topic"] == label],
                        key=lambda r: -(r["volume"] or 0)):
            print("   %-22s %9s" % (r["keyword"],
                                    "-" if r["volume"] == "" else format(r["volume"], ",")))

    print("\n배출 맥락 합계 %s / 하한선 %s -> %s"
          % (format(judged, ","), format(FLOOR, ","),
             "별도 가이드로 낸다" if judged >= FLOOR
             else "종량제봉투 가이드의 절로 둔다 (종결)"))
    print("-> %s" % OUT)


if __name__ == "__main__":
    main()
