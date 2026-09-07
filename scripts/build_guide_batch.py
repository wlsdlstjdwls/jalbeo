# -*- coding: utf-8 -*-
"""실측 8차 묶음 — 절차 축 가이드 후보 8주제.

`triage_candidates_guides.py`가 묶은 주제마다 대표 키워드를 골라 5개씩 자른다.
품목 실측과 다른 점: 품목은 `{이름}버리는법` + `{이름}분리수거` 두 어미 고정인데,
절차는 어미가 주제마다 다르다 (봉투는 가격/파는곳, 과태료는 금액/이의신청).
그래서 어미를 만들지 않고 자동완성이 실제로 물어온 표현을 그대로 잰다.

출력: data/keywords/gate1-batches-8.md
그 다음: python scripts/build_batch_page.py data/keywords/gate1-batches-8.md
"""
import io
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "keywords", "gate1-batches-8.md")

# (주제 라벨, 자동완성 건수, [키워드...])
TOPICS = [
    ("종량제봉투 - 규격, 가격, 파는곳", 101, [
        "종량제봉투", "종량제봉투가격", "쓰레기봉투가격", "종량제봉투규격",
        "종량제봉투파는곳", "쓰레기봉투종류", "종량제봉투환불", "재활용봉투",
        "불연성마대", "50리터종량제봉투가격",
    ]),
    ("음식물 종량제봉투", 33, [
        "음식물쓰레기봉투", "음식물종량제봉투", "음식물쓰레기봉투가격",
        "음식물쓰레기봉투파는곳", "음식물쓰레기봉투규격",
    ]),
    ("헌옷, 헌책 방문수거", 32, [
        "헌옷수거", "헌옷방문수거", "의류수거함", "헌책수거", "헌책방문수거",
        "고물상", "폐지수거",
    ]),
    ("쓰레기 무단투기 과태료", 28, [
        "쓰레기무단투기", "무단투기과태료", "쓰레기과태료", "분리배출과태료",
        "무단투기신고", "무단투기신고포상금", "쓰레기과태료이의신청",
    ]),
    ("아파트 분리수거 요일과 시간", 19, [
        "아파트분리수거", "분리수거요일", "분리배출요일", "쓰레기버리는시간",
        "클린하우스", "분리수거요일제",
    ]),
    ("이사할 때 나오는 쓰레기", 16, [
        "이사쓰레기", "이사쓰레기버리는법", "이사쓰레기비용", "대청소쓰레기",
        "유품정리비용",
    ]),
    ("분리배출 기본 규칙", 13, [
        "분리배출", "분리배출방법", "분리배출표시", "재활용안되는것",
        "분리수거방법",
    ]),
    ("원룸, 자취방 쓰레기", 10, [
        "원룸쓰레기", "원룸쓰레기배출", "자취방쓰레기", "원룸분리수거",
        "오피스텔쓰레기",
    ]),
]

HEADER = """# 검색량 실측 8차 -- 절차 축 가이드 후보

> 8주제, 키워드 {n_kw}개, {n_batch}묶음 / 생성일 2026-09-07
> 씨앗이 품목이 아니라 절차 명사인 첫 크롤(`crawl_autocomplete_guides.py`) 결과다.

## 왜 재나

`/guides/`는 3개에서 멈춰 있다. 그 3개의 합이 198,805인데, 후보 목록이 없어서
4번째를 못 골랐다. 지금까지의 자동완성 크롤은 씨앗이 전부 품목명이라
"헌책 방문수거"가 들어와도 헌책이라는 품목만 남기고 방문수거를 버렸다.

절차 시드로 다시 캐서 394건을 얻었고, 기존 가이드가 이미 답하는 87건과
지역 20건, 범위밖 16건을 뺀 나머지를 8주제로 묶었다.

## 결과를 어떻게 읽나

| 상황 | 처리 |
|---|---|
| 주제 합계가 16,035(폐가구 가이드) 이상 | 가이드로 쓴다 |
| 그 아래지만 답이 기존 페이지와 갈림 | 보류. 다음 회차 후보 |
| 답이 기존 가이드와 같음 | 기존 가이드에 절 하나로 흡수 |

폐가구 가이드(16,035)가 하한선인 이유는 그게 지금 발행된 가이드 중 제일 작아서다.
그보다 작으면 페이지를 하나 더 만들 근거가 없다.

## 하는 법

1. searchad.naver.com 로그인 -> 도구 -> **키워드 도구**
2. 묶음을 붙여넣고 조회 (한 번에 5개까지)
3. 다운로드(엑셀) -> `data/keywords/gate1-8/`
4. 복붙이 번거로우면 `python scripts/build_batch_page.py data/keywords/gate1-batches-8.md`

## 주제별 자동완성 건수

| 주제 | 자동완성 후보 | 잴 키워드 |
|---|---:|---:|
{topic_table}

## 묶음

"""


def main():
    kws = []
    for label, n, words in TOPICS:
        for w in words:
            kws.append((w, label))

    batches = [kws[i:i + 5] for i in range(0, len(kws), 5)]
    topic_table = "\n".join(
        "| %s | %d | %d |" % (label, n, len(words)) for label, n, words in TOPICS)

    body = []
    for i, batch in enumerate(batches, 1):
        note = batch[0][1]
        if any(b[1] != note for b in batch):
            note = " + ".join(sorted({b[1] for b in batch}))
        body.append("**%d/%d** - %s\n\n```\n%s\n```\n"
                    % (i, len(batches), note, "\n".join(w for w, _ in batch)))

    text = HEADER.format(n_kw=len(kws), n_batch=len(batches),
                         topic_table=topic_table) + "\n".join(body)
    with io.open(OUT, "w", encoding="utf-8") as f:
        f.write(text)
    print("키워드 %d개, %d묶음 -> %s" % (len(kws), len(batches), OUT))


if __name__ == "__main__":
    main()
