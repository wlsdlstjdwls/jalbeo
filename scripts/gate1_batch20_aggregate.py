# -*- coding: utf-8 -*-
"""실측 20차 집계 -- 생리대 축 3주제 + 지식iN 씨앗 2회차 62주제.

입력: data/keywords/gate1-20/*.xlsx  (키워드도구 '다운로드' 산출물)
      scripts/build_kin_batch20.py  (주제 -> 축 -> 키워드)
출력: data/keywords/gate1-volumes-20.csv

19차와 같다. '<10'은 5로 근사하고, 안 걸린 키워드는 0이 아니라 빈칸이다
(미측정은 null).

19차와 다른 것 하나. **합계를 19차(8,375)와 나란히 찍는다.** 판단 62번대로
한 씨앗 출처는 회차 두 번을 못 버티므로, 이 비가 다음 회차를 같은 출처로
짤지를 정한다 (Q&A는 15,890 -> 2,460으로 6.5분의 1이 됐다).
"""
import csv
import glob
import io
import os
import re
import sys

import openpyxl

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_kin_batch20 import SUFFIXES, TOPICS  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KW = os.path.join(ROOT, "data", "keywords")
SRC = os.path.join(KW, "gate1-20", "*.xlsx")
OUT = os.path.join(KW, "gate1-volumes-20.csv")

PREV_TOTAL = 8375          # 실측 19차, 지식iN 씨앗 1회차
FLOOR_NOTE = "발행분 최저: 화병 35, 나뭇가지 40, 선반 40, 우드락 95"


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
        sys.exit("%s 에 엑셀이 없다. gate1-batches-20.md 묶음을 먼저 돌린다." % SRC)

    files, best = read_all()
    rows, missing = [], []

    for name, axis, mod, why in TOPICS:
        vals = {}
        for suf in SUFFIXES:
            kw = "%s %s" % (name, suf)
            v = best.get(norm(kw))
            if v is None:
                missing.append(kw)
            vals[suf] = v
        got = [v for v in vals.values() if v is not None]
        rows.append({
            "topic": name,
            "axis": axis,
            SUFFIXES[0]: "" if vals[SUFFIXES[0]] is None else vals[SUFFIXES[0]],
            SUFFIXES[1]: "" if vals[SUFFIXES[1]] is None else vals[SUFFIXES[1]],
            "total": sum(got) if len(got) == len(SUFFIXES) else "",
            "modifiers": mod,
            "why": why,
        })

    fields = ["topic", "axis", SUFFIXES[0], SUFFIXES[1],
              "total", "modifiers", "why"]
    with io.open(OUT, "w", encoding="utf-8-sig", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=fields)
        wr.writeheader()
        wr.writerows(sorted(rows, key=lambda r: -(r["total"] or 0)))

    print("파일 %d개 / 수집 키워드 %d개 / 계획 %d개 중 %d개 측정"
          % (len(files), len(best), len(TOPICS) * len(SUFFIXES),
             len(TOPICS) * len(SUFFIXES) - len(missing)))
    if missing:
        print("조회에 안 걸림 %d개: %s" % (len(missing), ", ".join(missing)))

    done = [r for r in rows if r["total"] != ""]
    total = sum(r["total"] for r in done)
    print("\n합계 %s / 주제 %d개 / %s"
          % (format(total, ","), len(done), FLOOR_NOTE))
    print("19차(지식iN 1회차) %s 대비 %.2f배 (판단 62: 한 출처는 회차 둘을 못 버틴다)"
          % (format(PREV_TOTAL, ","), total / float(PREV_TOTAL)))

    # 생리대 축은 따로 본다. 탐폰(355) 보류를 닫는 자리다 (docs/49)
    axis_w = [r for r in rows if r["axis"] == "위생"]
    if axis_w:
        print("\n[생리대 축] 탐폰 355, 기저귀 85와 견준다")
        for r in axis_w:
            print("  %-8s %9s" % (r["topic"],
                  format(r["total"], ",") if r["total"] != "" else "-"))

    print("\n%-14s %5s %9s %9s %9s  %s"
          % ("주제", "축", "버리는법", "분리수거", "합계", "무엇이 갈리나"))
    for r in sorted(rows, key=lambda r: -(r["total"] or 0)):
        print("%-14s %5s %9s %9s %9s  %s"
              % (r["topic"], r["axis"],
                 format(r[SUFFIXES[0]], ",") if r[SUFFIXES[0]] != "" else "-",
                 format(r[SUFFIXES[1]], ",") if r[SUFFIXES[1]] != "" else "-",
                 format(r["total"], ",") if r["total"] != "" else "-",
                 r["why"]))

    # 어미가 뒤집히는지 (판단 9번). 어느 쪽이 큰지가 품목마다 다르다
    flip = [r for r in done if r[SUFFIXES[1]] > r[SUFFIXES[0]]]
    print("\n분리수거가 더 큰 주제 %d/%d개: %s"
          % (len(flip), len(done), ", ".join(r["topic"] for r in flip)))

    print("\n-> %s" % OUT)
    print("다음: 위에서부터 '무엇이 갈리나'를 조사한다. 안 갈리면 별칭이다.")


if __name__ == "__main__":
    main()
