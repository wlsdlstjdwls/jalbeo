# -*- coding: utf-8 -*-
"""실측 10차 묶음 -- 사이트 검색어 로그에서 온 후보.

`docs/20`이 깐 `search_queries`가 처음으로 사람 검색을 물어왔다. 못 찾은
검색(hit_count = 0) 중 발행 품목, 별칭과 한 글자도 안 겹치는 것만 남겼다.
표본은 얇다(방문자 2명). 그래서 **빈도를 수요로 읽지 않고 실측한다** --
판단 16번. 빈도 1위가 검색량 1위가 아니었던 전례가 `docs/24`에 있다.

주제로 묶는 이유: 닌텐도, 플스, 플레이스테이션은 세 검색어지만 답이 하나다
(게임기). 별칭이 될지 페이지가 될지는 합계가 아니라 답이 갈리는지로 정하고,
검색량은 어느 표기를 페이지 이름으로 쓸지에만 쓴다 -- 판단 12번.

품목 축은 가이드 축과 달리 하한선이 없다. 발행된 167개 중 러닝머신 20,
보일러 20까지 있다. 그러니 이 실측은 발행 여부가 아니라 **이름과 우선순위**를
정한다. 발행 여부는 답이 기존 페이지와 갈리는지로 따로 본다.

출력: data/keywords/gate1-batches-10.md
그 다음: python scripts/build_batch_page.py data/keywords/gate1-batches-10.md
"""
import io
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "keywords", "gate1-batches-10.md")

PER_BATCH = 5
SUFFIXES = ("버리는법", "분리수거")

# (주제, 로그에 찍힌 검색어, [잴 표기...])
TOPICS = [
    ("게임기", ["닌텐도", "플스", "플레이스테이션"],
     ["게임기", "닌텐도", "플레이스테이션", "플스"]),
    ("피규어", ["피규어"], ["피규어"]),
    ("속옷", ["팬티"], ["속옷", "팬티"]),
    ("오징어", ["오징어"], ["오징어"]),
    ("썬크림", ["썬크"], ["썬크림"]),
]

HEADER = """# 검색량 실측 10차 -- 검색어 로그 후보

> {n_topic}주제, 키워드 {n_kw}개, {n_batch}묶음 / 생성일 2026-09-07
> 원천은 사이트 검색창이다 (`docs/20`, `scripts/search_log_candidates.py`)

## 어디서 왔나

도메인 연결(`docs/30`) 뒤 처음으로 사람이 친 검색이 로그에 남았다.
못 찾은 검색 중 발행 품목, 별칭과 안 겹치는 것만 남긴 결과가 아래다.

| 주제 | 로그에 찍힌 말 | 잴 표기 |
|---|---|---|
{table}

빠진 것 둘. `공기청덩`은 오타라 페이지가 아니라 검색이 받는다 --
`lib/search.ts`의 자모 폴백을 이번에 붙였다. `침대커버`는 침대(대형폐기물)로
잘못 걸리고 있는데, 이불(대형폐기물)과 헌옷(의류수거함) 중 어디로 가는지
답이 갈려 조사가 먼저다. 실측 대상이 아니다.

## 표본이 얇다

방문자 2명, 못 찾은 검색 10건이다. 추출기의 표본 기준(방문자 10명,
못 찾은 검색 20건)에 한참 못 미친다. **빈도 순위를 수요로 읽으면 안 된다**
(`docs/23` 선례). 그래서 빈도로 자르지 않고 다섯 주제를 전부 잰다.

## 결과를 어떻게 읽나

품목 축에는 하한선이 없다. 발행된 167개 중 러닝머신 20, 보일러 20이 있다.
그러니 검색량은 **발행 여부가 아니라 이름과 순서**를 정한다.

| 질문 | 무엇으로 답하나 |
|---|---|
| 페이지를 낼까 | 답이 기존 페이지와 갈리는가 (검색량 아님) |
| 어느 표기를 페이지 이름으로 | 두 어미 합계 1위 (판단 11번) |
| 나머지 표기는 | 별칭. 단, 본체의 2배를 넘으면 개명이나 분리 (판단 12번) |

## 묶는 법

키워드 도구는 씨앗을 한 번에 5개까지 받는다. 아래 묶음을 통째로 복사해
[네이버 검색광고 > 키워드도구]에 붙이고 조회한 뒤 다운로드한다.
받은 xlsx는 전부 `data/keywords/gate1-10/`에 넣는다.

그 다음: `python scripts/gate1_batch10_aggregate.py`
"""


def keywords():
    out = []
    for topic, _, words in TOPICS:
        for w in words:
            for suf in SUFFIXES:
                out.append((topic, "%s %s" % (w, suf)))
    return out


def main():
    pairs = keywords()
    batches = [pairs[i:i + PER_BATCH] for i in range(0, len(pairs), PER_BATCH)]
    table = "\n".join(
        "| %s | %s | %s |" % (t, ", ".join(logged), ", ".join(words))
        for t, logged, words in TOPICS)

    out = [HEADER.format(n_topic=len(TOPICS), n_kw=len(pairs),
                         n_batch=len(batches), table=table), ""]
    for i, batch in enumerate(batches, 1):
        labels = []
        for topic, _ in batch:
            if topic not in labels:
                labels.append(topic)
        out.append("**%d/%d** - %s" % (i, len(batches), " + ".join(labels)))
        out.append("")
        out.append("```")
        out.extend(kw for _, kw in batch)
        out.append("```")
        out.append("")

    io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(out))
    print("%s -- 주제 %d개, 키워드 %d개, %d묶음"
          % (OUT, len(TOPICS), len(pairs), len(batches)))


if __name__ == "__main__":
    main()
