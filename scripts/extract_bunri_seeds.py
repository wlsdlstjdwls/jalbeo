# -*- coding: utf-8 -*-
"""분리의정석 품목사전(770개)에서 씨앗을 캔다.

입력: data/raw/bunri-dictionary.json  (scripts/crawl_bunri_dictionary.py)
출력: data/keywords/candidates-bunri.csv

수수료표는 씨앗으로 약했다(판단 37 - 대형폐기물은 품목이 뭐든 답이 같다).
품목사전은 재활용, 일반, 대형, 음식물, 유해로 나뉘어 있어 "품목마다 답이
갈리는 영역"을 담는다(판단 41). 그래서 분류를 같이 남기고, 대형폐기물로만
분류된 것과 음식물류는 실측 묶음에서 뒤로 민다.

접기는 extract_external_seeds와 같은 규칙이다 - 표기 혼동 집합만 접고
편집거리는 안 쓴다(판단 36). 리포 루트에서 돌린다.
"""
import csv
import io
import json
import re
import sys

sys.path.insert(0, "scripts")
from extract_external_seeds import (  # noqa: E402
    folds_into, is_noise, known_vocabulary, norm,
)

DICT = "data/raw/bunri-dictionary.json"
EXTERNAL = "data/keywords/candidates-external.csv"
OUT = "data/keywords/candidates-bunri.csv"

# 가정 배출이 아닌 것. 판단 1번이 지역 축을 접은 이유와 같다 - 우리 독자가 아니다
BUSINESS = re.compile(r"(업소용|사업장|공사장|병원|산업용|농업용|영농|축산)")


def main():
    vocab = known_vocabulary()
    # 이미 판정한 외부 후보(실측 11차 등)는 아는 말로 친다. 미판정은 남긴다
    external = {}
    for r in csv.DictReader(io.open(EXTERNAL, encoding="utf-8-sig")):
        external[norm(r["item"])] = r
        if r["decision"]:
            vocab.setdefault(norm(r["item"]), f"{r['item']} (외부 판정 {r['decision']})")

    rows, folded, heads = {}, [], {}
    for e in json.load(io.open(DICT, encoding="utf-8")):
        name = e["base"].strip()
        name = re.sub(r"[\"'“”]", "", name)
        full = re.sub(r"\s*[·∙]\s*", ", ", e["name"])  # 가운뎃점은 산출물에 안 쓴다
        if is_noise(name) or BUSINESS.search(full):
            continue
        hit = folds_into(name, vocab)
        if hit:
            folded.append((full, hit))
            continue
        key = norm(name)
        if key in rows:
            rows[key]["cls"] = ", ".join(sorted(set(rows[key]["cls"].split(", ")) | set(e["cls"].split(", "))))
            rows[key]["variants"] = ", ".join(x for x in [rows[key]["variants"], full] if x and x != name)
            continue
        hit = folds_into(name, heads)
        if hit:
            head = rows[norm(hit)]
            head["variants"] = ", ".join(x for x in [head["variants"], full] if x)
            folded.append((full, f"{hit} (후보 대표)"))
            continue
        heads[key] = name
        ext = external.get(key)
        rows[key] = {
            "item": name,
            "name_full": full if full != name else "",
            "cls": e["cls"],
            "id": e["id"],
            "in_external": 1 if ext else 0,
            "variants": "",
            "decision": "",
            "note": "",
        }

    def rank(r):
        c = r["cls"]
        # 답이 갈리는 영역(재활용, 일반, 유해)이 앞, 대형만 있는 것과 음식물은 뒤
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
            "item", "name_full", "cls", "id", "in_external", "variants", "decision", "note"])
        w.writeheader()
        for r in out:
            w.writerow(r)

    from collections import Counter
    print("품목사전 770 -> 접힘 %d, 신규 %d" % (len(folded), len(out)))
    print("분류별:", Counter(rank(r) for r in out))
    print("접힌 예:", folded[:12])
    print(OUT)


if __name__ == "__main__":
    main()
