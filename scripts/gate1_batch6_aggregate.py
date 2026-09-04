# -*- coding: utf-8 -*-
"""실측 6차 집계 — 별칭 40개 재측정.

입력: data/keywords/gate1-6/*.xlsx  (키워드도구 '다운로드' 산출물)
      data/keywords/gate1-batches-6.md  (대상 목록 = 별칭/본체/본체 검색량)
출력: data/keywords/gate1-volumes-6.csv

5차 집계기와 대상이 다르다. 5차는 미발행 후보를 재서 발행 여부를 봤고,
6차는 **이미 별칭으로 접힌 단어**를 재서 본체와 뒤집혔는지 본다.
그래서 기준선이 아니라 본체 대비 배수로 판정한다.

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
SRC = os.path.join(KW, "gate1-6", "*.xlsx")
PLAN = os.path.join(KW, "gate1-batches-6.md")
OUT = os.path.join(KW, "gate1-volumes-6.csv")

SUFFIXES = ["버리는법", "분리수거"]

# 뒤집힘 판정선. 본체의 2배를 넘으면 개명이나 분리를 검토한다 (docs/18).
FLIP = 2.0


def volume(cell):
    if cell is None:
        return 0
    s = str(cell).strip().replace(",", "")
    if s.startswith("<"):
        return 5
    return int(s) if s.isdigit() else 0


def norm(s):
    # 키워드도구는 영문을 대문자로 되돌려준다 (led등 -> LED등). 대소문자를 접는다.
    return re.sub(r"\s+", "", s).lower()


def read_plan():
    """대상 목록 표에서 (별칭, 본체, 본체 검색량)을 읽는다."""
    rows = []
    for line in io.open(PLAN, encoding="utf-8"):
        m = re.match(r"^\|\s*(\d+)\s*\|(.+?)\|(.+?)\|\s*([\d,]+)\s*\|\s*$", line)
        if m:
            rows.append({"alias": m.group(2).strip(),
                         "host": m.group(3).strip(),
                         "host_vol": int(m.group(4).replace(",", ""))})
    return rows


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


def measure(name, best, used):
    rec, total, hit = {}, 0, False
    for suf in SUFFIXES:
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
        sys.exit("%s 에 엑셀이 없다. gate1-batches-6.md 묶음을 먼저 돌린다." % SRC)

    files, best = read_all()
    used = set()
    plan = read_plan()

    rows, missing = [], []
    for p in plan:
        rec, total = measure(p["alias"], best, used)
        if rec is None:
            missing.append(p["alias"])
            continue
        ratio = total / float(p["host_vol"]) if p["host_vol"] else 0.0
        rows.append({"alias": p["alias"], "host": p["host"], "host_vol": p["host_vol"],
                     "a": rec[SUFFIXES[0]], "b": rec[SUFFIXES[1]], "total": total,
                     "ratio": round(ratio, 2),
                     "verdict": "검토" if ratio >= FLIP else "유지"})
    rows.sort(key=lambda r: -r["ratio"])

    with io.open(OUT, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["alias", "host", "host_vol",
                                          "a", "b", "total", "ratio", "verdict"])
        w.writeheader()
        w.writerows(rows)

    dropped = sorted(set(best) - used, key=lambda k: -best[k])
    flipped = [r for r in rows if r["verdict"] == "검토"]

    print("파일 %d개 / 키워드 %d개 -> 별칭 %d개 측정 (계획 %d개)"
          % (len(files), len(best), len(rows), len(plan)))
    if missing:
        print("미측정 %d개: %s" % (len(missing), ", ".join(missing)))
    print("씨앗 밖 연관어 %d개 버림 (상위: %s)" % (len(dropped), ", ".join(dropped[:5])))
    print("본체의 %.1f배 이상 %d개" % (FLIP, len(flipped)))

    fmt = lambda v: "-" if v == "" else format(v, ",")
    print()
    print("%-12s %-12s %8s %9s %9s %8s %7s  %s"
          % ("별칭", "본체", "본체량", SUFFIXES[0], SUFFIXES[1], "합계", "배수", "판정"))
    for r in rows:
        print("%-12s %-12s %8s %9s %9s %8s %6.2fx  %s"
              % (r["alias"][:12], r["host"][:12], format(r["host_vol"], ","),
                 fmt(r["a"]), fmt(r["b"]), format(r["total"], ","),
                 r["ratio"], r["verdict"]))
    print("\n-> %s" % OUT)


if __name__ == "__main__":
    main()
