# -*- coding: utf-8 -*-
"""품목사전 **유사검색어**에서 씨앗을 캔다.

입력: data/raw/bunri-dictionary-detail.json  (crawl_bunri_detail.py)
출력: data/keywords/candidates-bunri-terms.csv

`extract_bunri_seeds.py`는 품목사전의 **표제어** 770개를 씨앗으로 썼다.
여기는 같은 사전의 다른 칸이다. 상세 화면의 유사검색어는 표제어가 아니라
**그 표제어로 찾아가는 말**이라, 사전이 "이 말로 찾는 사람이 있다"고
인정한 목록이다. 텀블러 밑의 보온도시락통, 컵 워머가 그렇다.

두 갈래로 온다(크롤러 참고).
  - `term_entries` : 품목사전에 표제어가 따로 있는 말. 표제어 씨앗이 이미 봤다
  - `terms`        : 표제어가 없는 말. **이쪽만 씨앗이다**

접기는 `extract_external_seeds`와 같다 - 표기 혼동 집합만 접고 편집거리는
안 쓴다(판단 36). 이미 판정한 외부/품목사전/지식iN 후보도 아는 말로 친다
(판단 50 - 기계로 확인되는 칸은 기계가 채운다).

우리 어휘에 없는 말만 남기고, 그 말을 어느 표제어가 데리고 있는지
(`under`)와 그 표제어의 분류(`cls`)를 같이 적는다. 분류가 곧 답이 갈리는
자리인지를 말해 준다(판단 41).

    python scripts/extract_bunri_term_seeds.py
"""
import csv
import io
import json
import re
import sys
from collections import Counter

sys.path.insert(0, "scripts")
from extract_external_seeds import (  # noqa: E402
    folds_into, is_noise, known_vocabulary, norm,
)

SRC = "data/raw/bunri-dictionary-detail.json"
PRIOR = [
    "data/keywords/candidates-external.csv",
    "data/keywords/candidates-bunri.csv",
    "data/keywords/candidates-kin.csv",
    "data/keywords/candidates-qna.csv",
]
OUT = "data/keywords/candidates-bunri-terms.csv"

BUSINESS = re.compile(r"(업소용|사업장|공사장|병원|산업용|농업용|영농|축산)")


def load_prior(vocab):
    """이미 판정한 후보는 아는 말로 친다. 미판정은 남긴다."""
    n = 0
    for path in PRIOR:
        try:
            fh = io.open(path, encoding="utf-8-sig")
        except IOError:
            continue
        for r in csv.DictReader(fh):
            item = r.get("item") or r.get("head") or ""
            if item and r.get("decision"):
                vocab.setdefault(norm(item), "%s (판정 %s)" % (item, r["decision"]))
                n += 1
    return n


def main():
    vocab = known_vocabulary()
    base = len(vocab)
    prior = load_prior(vocab)

    rows, folded, heads = {}, [], {}
    seen_terms = 0
    for e in json.load(io.open(SRC, encoding="utf-8")):
        owner = re.sub(r"\s*[·∙]\s*", ", ", e["name"])
        for term in e["terms"]:
            seen_terms += 1
            name = re.sub(r"[\"'“”]", "", term).strip()
            if not name or is_noise(name) or BUSINESS.search(name):
                continue
            hit = folds_into(name, vocab)
            if hit:
                folded.append((name, hit))
                continue
            key = norm(name)
            if key in rows:
                r = rows[key]
                if owner not in r["under"]:
                    r["under"] = ", ".join([r["under"], owner])
                    r["cls"] = ", ".join(sorted(set(r["cls"].split(", "))
                                                | set(e["cls"].split(", "))))
                continue
            hit = folds_into(name, heads)
            if hit:
                folded.append((name, "%s (후보 대표)" % hit))
                continue
            heads[key] = name
            rows[key] = {
                "item": name,
                "under": owner,
                "cls": e["cls"],
                "id": e["id"],
                "decision": "",
                "note": "",
            }

    def rank(r):
        c = r["cls"]
        if "음식물" in c:
            return 3
        if c == "대형폐기물":
            return 2
        if "재활용" in c or "일반" in c or "유해" in c:
            return 0
        return 1

    out = sorted(rows.values(), key=lambda r: (rank(r), r["item"]))
    with io.open(OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=[
            "item", "under", "cls", "id", "decision", "note"])
        w.writeheader()
        for r in out:
            w.writerow(r)

    print("어휘 %d개(발행분) + 판정된 후보 %d개" % (base, prior))
    print("유사검색어(표제어 없는 말) %d건 -> 접힘 %d, 신규 %d"
          % (seen_terms, len(folded), len(out)))
    print("분류별:", Counter(rank(r) for r in out))
    print("접힌 예:", folded[:10])


if __name__ == "__main__":
    main()
