# -*- coding: utf-8 -*-
"""절차 축 후보 394건을 가이드 주제로 묶는다. 실측 대상만 다음 단계로 넘긴다.

`crawl_autocomplete_guides.py`가 캔 394건은 낱개 질의라 그대로는 페이지가 안 된다.
가이드는 품목처럼 1질의 1페이지가 아니라 **한 절차에 질의가 수십 개 붙는다**
(`docs/14`: 폐가전 무상수거 하나에 무료수거/무상수거/방문수거/수거신청이 다 붙어
145,940). 그래서 낱개를 세지 않고 주제로 묶은 뒤, 주제마다 대표 키워드만 잰다.

분류(위에서부터 먼저 걸리는 것을 적용):
  기존커버   발행된 가이드 3개나 품목 페이지가 이미 답한다
  지역       지자체명이 박혔다. 확정 판단 1번(B층 폐기)
  범위밖     택배 방문수거, 분리수거장 설치, 경고문 제작. 쓰레기 배출이 아니다
  <주제>     남은 것. 주제별로 묶어 실측 대상이 된다

출력:
  data/keywords/candidates-guides-triage.csv   394건 전부의 분류
  data/keywords/guide-topics.csv               주제별 집계
"""
import csv
import io
import os
import re
import sys
from collections import Counter, defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KW = os.path.join(ROOT, "data", "keywords")
SRC = os.path.join(KW, "candidates-guides.csv")
OUT = os.path.join(KW, "candidates-guides-triage.csv")
OUT_TOPICS = os.path.join(KW, "guide-topics.csv")

REGION = re.compile(
    r"(서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주"
    r"|김포|동탄|파주|부천|용인|창원|천안|수원|청주|평택|안양|일산|화성|성남|고양|남양주"
    r"|시흥|광명|의정부|구리|하남|김해|양산|전주|포항|구미|원주|춘천|목포|여수|순천)")

# 기존 페이지가 이미 답하는 축. 같은 답을 하는 페이지를 늘리지 않는다(확정 판단 5번).
COVERED = [
    (re.compile(r"스티커|납부필증|배출신고|폐기물\s?신고|생활폐기물\s?신고"),
     "daehyeong-pyegimul-singo"),
    (re.compile(r"(가전|전자제품|냉장고|세탁기|에어컨|티비|tv).*(무상|무료|방문)수거"),
     "pyegajeon-musang-sugeo"),
    (re.compile(r"(가구|소파|쇼파|장롱|침대).*(무상|무료)수거"), "pyegagu-mulyo-sugeo"),
    (re.compile(r"대형\s?폐기물\s?(수거|수수료|신청|가격)"), "daehyeong-pyegimul-singo"),
]

# 쓰레기 배출 절차가 아닌 것.
OUT_OF_SCOPE = re.compile(
    r"(택배|우체국|경동|로젠|퀵|중고|당근|판매|팔기|매입|거치대|설치|제작|경고문"
    r"|현수막|알바|일자리|자격증|면허|사업자|창업|주식|보험)")

# 주제. 순서대로 먼저 걸리는 것을 쓴다.
TOPICS = [
    ("eumsik-bongtu", "음식물 종량제봉투 (용량, 가격, 파는곳)",
     re.compile(r"음식물.*(봉투|종량제)|음식물종량제")),
    ("jongryangje-bongtu", "종량제봉투 (규격, 리터, 가격, 파는곳, 환불)",
     re.compile(r"종량제|쓰레기\s?봉투|쓰레기봉투|재활용\s?봉투|불연성|마대")),
    ("mudan-tugi", "쓰레기 무단투기 과태료 (금액, 고지서, 이의신청, 신고)",
     re.compile(r"무단투기|과태료|벌금|신고포상|쓰레기\s?신고")),
    ("isa-sseuregi", "이사할 때 나오는 쓰레기 (한꺼번에 버리는 법, 비용)",
     re.compile(r"이사|이삿짐|입주\s?청소|대청소|유품정리")),
    ("wonrum-sseuregi", "원룸, 자취방 쓰레기 배출 (수거함 없는 집)",
     re.compile(r"원룸|자취|오피스텔|빌라|고시원|1인가구|혼자")),
    ("apateu-bunri", "아파트 분리수거 요일과 시간",
     re.compile(r"아파트|공동주택|분리수거\s?(요일|날짜|시간)|클린하우스|배출\s?요일")),
    ("heonot-heonchaek", "헌옷, 헌책 방문수거 (의류수거함, 업체)",
     re.compile(r"헌옷|헌책|의류수거함|헌\s?옷|고물상|폐지")),
    ("bunri-baechul", "분리배출 기본 규칙 (표시, 재활용 안 되는 것)",
     re.compile(r"분리배출|분리수거|재활용\s?안|재활용\s?표시")),
    ("gongsa-pyegijae", "인테리어, 공사 폐자재 배출",
     re.compile(r"공사|인테리어|폐자재|건축|철거|시멘트|타일")),
]


def classify(q):
    for rx, guide in COVERED:
        if rx.search(q):
            return "기존커버", guide
    if REGION.search(q):
        return "지역", "B층 폐기 (확정 판단 1번)"
    if OUT_OF_SCOPE.search(q):
        return "범위밖", ""
    for key, label, rx in TOPICS:
        if rx.search(q):
            return key, label
    return "미분류", ""


def main():
    rows = list(csv.DictReader(io.open(SRC, encoding="utf-8-sig")))
    counts = Counter()
    by_topic = defaultdict(list)
    out = []
    for r in rows:
        verdict, note = classify(r["query"])
        counts[verdict] += 1
        out.append({
            "query": r["query"], "verdict": verdict, "note": note,
            "freq": r["freq"], "n_queries": r["n_queries"],
        })
        by_topic[verdict].append(r)

    with io.open(OUT, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["query", "verdict", "note", "freq", "n_queries"])
        w.writeheader()
        w.writerows(sorted(out, key=lambda r: (r["verdict"], -int(r["freq"]), r["query"])))

    topic_rows = []
    for key, label, _ in TOPICS:
        qs = by_topic.get(key) or []
        if not qs:
            continue
        qs.sort(key=lambda r: (-int(r["freq"]), r["query"]))
        topic_rows.append({
            "topic": key, "label": label, "n_queries": len(qs),
            "freq_sum": sum(int(r["freq"]) for r in qs),
            "samples": " / ".join(r["query"] for r in qs[:8]),
        })
    topic_rows.sort(key=lambda r: -r["n_queries"])
    with io.open(OUT_TOPICS, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["topic", "label", "n_queries", "freq_sum", "samples"])
        w.writeheader()
        w.writerows(topic_rows)

    print("총 %d건" % len(rows))
    for k, n in counts.most_common():
        label = next((l for key, l, _ in TOPICS if key == k), "")
        print("  %-20s %3d  %s" % (k, n, label))
    print("\n주제 %d개 -> %s" % (len(topic_rows), OUT_TOPICS))
    for t in topic_rows:
        print("  [%2d건] %s" % (t["n_queries"], t["label"]))
        print("         %s" % t["samples"])
    if counts.get("미분류"):
        print("\n미분류 %d건:" % counts["미분류"])
        for r in sorted(by_topic["미분류"], key=lambda r: -int(r["freq"]))[:40]:
            print("  %s (freq %s)" % (r["query"], r["freq"]))


if __name__ == "__main__":
    main()
