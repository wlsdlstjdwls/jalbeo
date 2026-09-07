# -*- coding: utf-8 -*-
"""실측 10차 집계 -- 검색어 로그 후보.

입력: data/keywords/gate1-10/*.xlsx  (키워드도구 '다운로드' 산출물)
      scripts/build_searchlog_batch.py  (주제 -> 표기 -> 키워드)
출력: data/keywords/gate1-volumes-10.csv

9차 집계기와 다른 점: **하한선 판정이 없다.** 품목 축에는 하한선이 없어서
(발행분 최저가 러닝머신 20) 검색량으로 발행 여부를 못 정한다. 대신 표기별로
두 어미를 합쳐 주제 안에서 줄을 세운다 -- 어느 표기를 페이지 이름으로 쓸지가
이 실측이 답하는 질문이다 (판단 11번, 12번).

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
from build_searchlog_batch import SUFFIXES, TOPICS  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KW = os.path.join(ROOT, "data", "keywords")
SRC = os.path.join(KW, "gate1-10", "*.xlsx")
OUT = os.path.join(KW, "gate1-volumes-10.csv")


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
        sys.exit("%s 에 엑셀이 없다. gate1-batches-10.md 묶음을 먼저 돌린다." % SRC)

    files, best = read_all()
    rows, missing = [], []

    for topic, _, words in TOPICS:
        for w in words:
            for suf in SUFFIXES:
                kw = "%s %s" % (w, suf)
                v = best.get(norm(kw))
                if v is None:
                    missing.append(kw)
                rows.append({"topic": topic, "word": w, "suffix": suf,
                             "keyword": kw, "volume": "" if v is None else v})

    with io.open(OUT, "w", encoding="utf-8-sig", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=["topic", "word", "suffix",
                                           "keyword", "volume"])
        wr.writeheader()
        wr.writerows(rows)

    print("파일 %d개 / 수집 키워드 %d개 / 계획 %d개 중 %d개 측정"
          % (len(files), len(best), len(rows), len(rows) - len(missing)))
    if missing:
        print("조회에 안 걸림 %d개: %s" % (len(missing), ", ".join(missing)))

    for topic, logged, words in TOPICS:
        print("\n[%s]  로그: %s" % (topic, ", ".join(logged)))
        tot = []
        for w in words:
            vals = [r["volume"] for r in rows
                    if r["word"] == w and r["volume"] != ""]
            tot.append((sum(vals), w, len(vals)))
        for s, w, n in sorted(tot, reverse=True):
            print("   %-14s %9s%s" % (w, format(s, ","),
                                      "" if n == len(SUFFIXES) else "  (일부 미측정)"))

    print("\n-> %s" % OUT)
    print("다음: 1위 표기를 페이지 이름으로 두고, 답이 기존 페이지와 갈리는지 조사한다.")


if __name__ == "__main__":
    main()
