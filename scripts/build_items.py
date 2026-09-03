# -*- coding: utf-8 -*-
"""자동완성 원본(jsonl) -> 품목 시드 CSV.

크롤링과 분리돼 있어 정제 규칙만 바꿔 몇 번이든 다시 돌릴 수 있다.
입력: data/raw/autocomplete-crawl.jsonl (scripts/crawl_naver_autocomplete.py 산출)
출력: data/keywords/items.csv
"""
import csv
import json
import os
import re
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw", "autocomplete-crawl.jsonl")
OUT = os.path.join(ROOT, "data", "keywords", "items.csv")

SUFFIXES = [
    "버리는 방법", "버리는방법", "버리는 법", "버리는법", "버리는 비용", "버리는 가격",
    "버리는 곳", "버리는",
    "분리수거 방법", "분리수거", "분리배출", "재활용",
    "음식물쓰레기", "음식물 쓰레기", "음식물",
    "일반쓰레기", "일반 쓰레기", "종량제봉투", "종량제",
    "대형폐기물", "폐기물", "폐기 비용", "폐기",
    "어디에 버려", "어떻게 버려", "버려도 되나요", "버려도 되나",
]
SUFFIXES.sort(key=len, reverse=True)

# 광역 + 조사에 자주 붙는 기초자치단체. 품목 자리에 오면 잘라낸다.
REGION_WORDS = """
서울 부산 대구 인천 광주 대전 울산 세종 경기 강원 충북 충남 전북 전남 경북 경남 제주
수원 성남 고양 용인 부천 안양 안산 화성 광명 김포 하남 남양주 의정부 파주 오산 시흥 군포
포항 경주 창원 김해 진주 전주 익산 순천 목포 청주 천안 아산 원주 춘천 강릉 제주시
""".split()
REGION_RE = re.compile(
    r"^(?:%s)$|^(?:%s)\s+|\s+(?:%s)$|^[가-힣]{1,3}(?:구|군)$|^[가-힣]{1,4}시$"
    % ("|".join(REGION_WORDS), "|".join(REGION_WORDS), "|".join(REGION_WORDS))
)

BAD = {
    "쓰레기", "생활", "재활용", "분리", "음식물", "일반", "대형", "폐기물", "폐기",
    "종량제", "가정", "집", "아파트", "우리집", "방법", "비용", "가격", "스티커",
    "무료", "업체", "어플", "신고", "수거", "배출", "처리", "그", "이", "저", "다",
}
OK_CHARS = re.compile(r"^[가-힣A-Za-z0-9]+(?: [가-힣A-Za-z0-9]+)*$")
NOISE = re.compile(r"(꿈|삼킴|먹으면|강아지|고양이|안까짐|해몽|사주|증상|병원|미신|풍수)")


def split_item(s):
    for suf in SUFFIXES:
        idx = s.find(suf)
        if idx > 0:
            return s[:idx].strip(), s[idx + len(suf):].strip(), suf
    return None


def strip_region(item):
    """'수원 이불' -> '이불'. 순수 지역명이면 None."""
    parts = item.split()
    if len(parts) > 1 and (parts[0] in REGION_WORDS or re.match(r"^[가-힣]{1,3}(구|군)$|^[가-힣]{1,4}시$", parts[0])):
        return " ".join(parts[1:]).strip() or None
    if REGION_RE.match(item):
        return None
    return item


def acceptable(item):
    if item in BAD or NOISE.search(item):
        return False
    if not (1 < len(item) <= 14):
        return False
    if any(suf in item for suf in SUFFIXES):   # 파싱 누수 ('우산 버리는법')
        return False
    if re.fullmatch(r"[0-9]+", item):
        return False
    return bool(OK_CHARS.match(item))


def key_of(item):
    """표기 변종 병합용 키. 공백 제거 + 소문자."""
    return re.sub(r"\s+", "", item).lower()


def main():
    groups = defaultdict(lambda: {
        "surface": Counter(), "freq": 0, "patterns": Counter(),
        "modifiers": Counter(), "regions": Counter(), "queries": set(), "sample": "",
    })

    n_lines = n_sugg = 0
    for line in open(RAW, encoding="utf-8"):
        rec = json.loads(line)
        n_lines += 1
        for s in rec["suggestions"]:
            n_sugg += 1
            parsed = split_item(s)
            if not parsed:
                continue
            item, modifier, suf = parsed
            item = strip_region(item)
            if not item or not acceptable(item):
                continue
            g = groups[key_of(item)]
            g["surface"][item] += 1
            g["freq"] += 1
            g["patterns"][suf] += 1
            g["queries"].add(rec["query"])
            if modifier and not NOISE.search(modifier):
                if modifier in REGION_WORDS or re.match(r"^[가-힣]{1,3}(구|군)$|^[가-힣]{1,4}시$", modifier):
                    g["regions"][modifier] += 1
                else:
                    g["modifiers"][modifier] += 1
            if not g["sample"]:
                g["sample"] = s

    rows = []
    for g in groups.values():
        canonical = g["surface"].most_common(1)[0][0]
        variants = [s for s, _ in g["surface"].most_common()[1:]]
        rows.append({
            "item": canonical,
            "freq": g["freq"],
            "n_queries": len(g["queries"]),
            "has_region_modifier": 1 if g["regions"] else 0,
            "patterns": "|".join(p for p, _ in g["patterns"].most_common()),
            "top_modifiers": "|".join(m for m, _ in g["modifiers"].most_common(6)),
            "regions": "|".join(m for m, _ in g["regions"].most_common(6)),
            "variants": "|".join(variants),
            "sample_suggestion": g["sample"],
        })
    rows.sort(key=lambda r: (-r["freq"], r["item"]))

    with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print("원본 질의 %d건 / 자동완성 %d건 -> 품목 %d개" % (n_lines, n_sugg, len(rows)))
    print("freq>=5: %d, freq>=3: %d" % (
        sum(1 for r in rows if r["freq"] >= 5), sum(1 for r in rows if r["freq"] >= 3)))
    print("-> %s" % OUT)


if __name__ == "__main__":
    main()
