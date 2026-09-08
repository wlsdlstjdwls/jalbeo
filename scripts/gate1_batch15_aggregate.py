# -*- coding: utf-8 -*-
"""실측 15차 집계 -- 저본체 별칭.

입력: data/keywords/gate1-15/*.xlsx  (키워드도구 '다운로드' 산출물)
      scripts/build_low_owner_alias_batch.py  (별칭 -> 본체 -> 키워드)
출력: data/keywords/gate1-volumes-15.csv

6차(`scripts/gate1_batch6_aggregate.py`)와 같은 축이다. 별칭 합계를 본체
검색량으로 나눈 배수를 같이 낸다. '<10'은 5로 근사하고, 조회에 안 걸린
키워드는 0이 아니라 빈칸이다(미측정은 null).

배수만으로 처분이 정해지지 않는다. 2배를 넘은 것만 조사 대상이고, 개명인지
분리인지는 판단 40번(그 페이지의 첫 문단이 이 사람의 질문인가)으로 가른다.
"""
import csv
import glob
import io
import os
import re
import sys

import openpyxl

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_low_owner_alias_batch import SUFFIXES, grouped, load  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KW = os.path.join(ROOT, "data", "keywords")
SRC = os.path.join(KW, "gate1-15", "*.xlsx")
OUT = os.path.join(KW, "gate1-volumes-15.csv")

# 판단 12번의 선. 6차에서 40개 중 5개가 넘었다.
SPLIT_RATIO = 2.0


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


def verdict(total, owner_vol):
    if total == "" or not owner_vol:
        return ""
    if total >= owner_vol * SPLIT_RATIO:
        return "조사"
    if total >= owner_vol:
        return "재검토"
    return "유지"


def main():
    if not glob.glob(SRC):
        sys.exit("%s 에 엑셀이 없다. gate1-batches-15.html 묶음을 먼저 돌린다." % SRC)

    files, best = read_all()
    keep, _ = load()
    rows, missing = [], []

    for alias, owner, slug, owner_vol in keep:
        vals = {}
        for suf in SUFFIXES:
            kw = "%s %s" % (alias, suf)
            v = best.get(norm(kw))
            if v is None:
                missing.append(kw)
            vals[suf] = v
        got = [v for v in vals.values() if v is not None]
        total = sum(got) if len(got) == len(SUFFIXES) else ""
        rows.append({
            "alias": alias,
            "owner": owner,
            "owner_slug": slug,
            "owner_volume": owner_vol or "",
            SUFFIXES[0]: "" if vals[SUFFIXES[0]] is None else vals[SUFFIXES[0]],
            SUFFIXES[1]: "" if vals[SUFFIXES[1]] is None else vals[SUFFIXES[1]],
            "total": total,
            "ratio": ("%.1f" % (total / float(owner_vol)))
                     if total != "" and owner_vol else "",
            "verdict": verdict(total, owner_vol),
        })

    fields = ["alias", "owner", "owner_slug", "owner_volume",
              SUFFIXES[0], SUFFIXES[1], "total", "ratio", "verdict"]
    with io.open(OUT, "w", encoding="utf-8-sig", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=fields)
        wr.writeheader()
        wr.writerows(sorted(rows, key=lambda r: -(r["total"] or 0)))

    done = [r for r in rows if r["total"] != ""]
    print("파일 %d개 / 수집 키워드 %d개 / 계획 %d개 중 %d개 측정"
          % (len(files), len(best), len(keep) * len(SUFFIXES),
             len(keep) * len(SUFFIXES) - len(missing)))
    if missing:
        print("조회에 안 걸림 %d개: %s" % (len(missing), ", ".join(missing[:40])))

    print("\n합계 %s / 별칭 %d개 / 본체 %d개"
          % (format(sum(r["total"] for r in done), ","), len(done),
             len(grouped(keep))))

    print("\n%-16s %-14s %8s %8s %7s %6s  %s"
          % ("별칭", "본체", "본체량", "합계", "배수", "판정", "어미"))
    for r in sorted(rows, key=lambda r: -(r["total"] or 0)):
        print("%-16s %-14s %8s %8s %7s %6s  %s/%s"
              % (r["alias"], r["owner"],
                 format(r["owner_volume"], ",") if r["owner_volume"] else "-",
                 format(r["total"], ",") if r["total"] != "" else "-",
                 r["ratio"] or "-", r["verdict"] or "-",
                 r[SUFFIXES[0]] if r[SUFFIXES[0]] != "" else "-",
                 r[SUFFIXES[1]] if r[SUFFIXES[1]] != "" else "-"))

    hit = [r for r in done if r["verdict"] == "조사"]
    print("\n본체의 %.0f배 이상 %d/%d개: %s"
          % (SPLIT_RATIO, len(hit), len(done),
             ", ".join("%s(%s배, 본체 %s)"
                       % (r["alias"], r["ratio"], r["owner"]) for r in hit)))

    # 판단 9번. 어느 어미가 큰지는 품목마다 뒤집힌다
    flip = [r for r in done if r[SUFFIXES[1]] > r[SUFFIXES[0]]]
    print("분리수거가 더 큰 별칭 %d/%d개" % (len(flip), len(done)))

    print("\n-> %s" % OUT)
    print("다음: '조사'만 본다. 본체 페이지 첫 문단이 그 질문에 답하면 개명, "
          "답이 갈리면 분리다(판단 40). 수수료가 붙으면 판단 39, 42도 본다.")


if __name__ == "__main__":
    main()
