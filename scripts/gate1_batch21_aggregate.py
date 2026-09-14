# -*- coding: utf-8 -*-
"""실측 21차 집계 -- 지식iN 씨앗 3회차, 크롤 어미를 상태로 늘린 회차.

입력: data/keywords/gate1-21/*.xlsx  (키워드도구 '다운로드' 산출물)
      scripts/build_kin_batch21.py  (주제 -> 축 -> 키워드)
출력: data/keywords/gate1-volumes-21.csv

20차와 같다. '<10'은 5로 근사하고, 안 걸린 키워드는 0이 아니라 빈칸이다
(미측정은 null).

20차와 다른 것 둘.

  1. **합계를 19차, 20차와 나란히 찍는다.** 판단 62번은 한 출처가 회차 둘을
     못 버틴다는 것이고 21차는 같은 출처의 세 번째다. 다만 어미를 늘렸으므로
     (판단 77) 이 비가 재는 것은 '출처가 말랐나'가 아니라 **'어미를 늘린
     것이 출처를 되살렸나'**다. 8,375 -> 6,280에 이어 또 0.75배면 어미로는
     안 되는 것이고, 20차보다 크면 판단 77이 맞은 것이다
  2. **축별 합계를 찍는다.** 이번 회차 주제 절반이 '축 자체가 없는 자리'라
     주제 하나가 아니라 축이 통째로 서는지를 본다. 난방기구(가전 일부),
     숯과 재, 화장품 내용물(생활화학), 국물(음식물 일부), DIY 자재.
     축 합계가 하한선 아래면 그 축은 통째로 안 세운다
"""
import csv
import glob
import io
import os
import re
import sys
from collections import OrderedDict

import openpyxl

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_kin_batch21 import SUFFIXES, TOPICS  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KW = os.path.join(ROOT, "data", "keywords")
SRC = os.path.join(KW, "gate1-21", "*.xlsx")
OUT = os.path.join(KW, "gate1-volumes-21.csv")

PREV = OrderedDict([("19차", 8375), ("20차", 6280)])
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
        sys.exit("%s 에 엑셀이 없다. gate1-batches-21.md 묶음을 먼저 돌린다." % SRC)

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
    for label, prev in PREV.items():
        print("%s(%s) 대비 %.2f배" % (label, format(prev, ","), total / float(prev)))
    print("(판단 77: 이 비가 재는 것은 출처가 말랐나가 아니라 어미가 되살렸나다)")

    # 축별 합계. 이번 회차는 '축 자체가 없는 자리'가 절반이라 주제가 아니라
    # 축이 서는지를 본다
    by_axis = OrderedDict()
    for r in done:
        by_axis.setdefault(r["axis"], []).append(r)
    print("\n[축별] 축 합계가 작으면 그 축은 통째로 안 세운다")
    for axis, rs in sorted(by_axis.items(), key=lambda kv: -sum(r["total"] for r in kv[1])):
        s = sum(r["total"] for r in rs)
        top = max(rs, key=lambda r: r["total"])
        print("  %-6s %9s  (%d주제, 1위 %s %s)"
              % (axis, format(s, ","), len(rs), top["topic"],
                 format(top["total"], ",")))

    print("\n%-12s %5s %9s %9s %9s  %s"
          % ("주제", "축", "버리는법", "분리수거", "합계", "무엇이 갈리나"))
    for r in sorted(rows, key=lambda r: -(r["total"] or 0)):
        print("%-12s %5s %9s %9s %9s  %s"
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
