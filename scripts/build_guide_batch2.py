# -*- coding: utf-8 -*-
"""실측 9차 묶음 -- PP마대.

`docs/29`가 남긴 하나뿐인 미측정 후보다. 절차 크롤 2차에서 신규 주제로 걸렸고
(자동완성 8건), 사이트가 한 글자도 안 답하고 있었다. 종량제봉투 가이드에 절로
흡수해 두었지만 검색량을 안 재서 별도 가이드 여부는 미정이다 (판단 16번 --
빈도로 자르지 말고 실측한다).

주제를 둘로 가른다. **같은 'PP마대'인데 검색 의도가 두 세계에 걸쳐 있다.**
버리는 쪽(규격, 가격, 파는곳, 버리는법)과 자재를 사는 쪽(중고, 구입방법, 톤마대)이
섞이면 합계가 부풀어 하한선 판정이 틀린다. 가이드 여부는 배출 맥락 합계로만 본다.

출력: data/keywords/gate1-batches-9.md
그 다음: python scripts/build_batch_page.py data/keywords/gate1-batches-9.md
"""
import io
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "keywords", "gate1-batches-9.md")

# (주제 라벨, 판정에 쓰나, [키워드...])
# 판정에 쓰나 = False면 참고용으로만 재고 하한선 합계에서 뺀다.
TOPICS = [
    ("PP마대 - 배출, 규격, 가격", True, [
        "pp마대", "pp마대가격", "pp마대파는곳", "pp마대사이즈",
        "pp마대20kg", "pp마대40kg", "pp마대버리는방법",
        "쓰레기마대", "마대자루", "폐기물마대",
    ]),
    ("PP마대 - 자재 구매 맥락 (참고)", False, [
        "pp마대구입방법", "pp마대중고", "pp마대뜻", "pp포대", "톤마대",
    ]),
]

HEADER = """# 검색량 실측 9차 -- PP마대

> 2주제, 키워드 {n_kw}개, {n_batch}묶음 / 생성일 2026-09-07
> `docs/29`가 남긴 유일한 미측정 후보다.

## 왜 재나

절차 크롤 2차(`crawl_autocomplete_guides2.py`)가 43건 중 딱 하나 새 주제를
물어왔다. PP마대다 -- 구입방법, 버리는방법, 20kg, 40kg, 뜻, 사이즈, 중고,
파는곳. 사이트가 한 글자도 안 답하고 있었다.

일단은 종량제봉투 가이드에 `## 마대는 규격이 지자체마다 다릅니다` 절로
흡수했다. 답의 성질이 봉투와 같아서다(같은 판매소, 같은 종량제 체계).
남은 질문은 **별도 가이드를 하나 더 낼 만큼 큰가**이고, 그건 빈도가 아니라
검색량으로 답한다 (판단 16번).

## 주제를 왜 둘로 갈랐나

'PP마대'는 검색 의도가 두 세계에 걸쳐 있다. 쓰레기를 담아 버리려는 쪽과
포장 자재를 사려는 쪽(중고, 톤마대, PP포대)이다. 뒤쪽은 이 사이트가 답할
질문이 아니다. 둘을 한 합계에 넣으면 하한선 판정이 부푼다. **가이드 여부는
배출 맥락 합계로만 정하고, 자재 쪽은 참고로만 적는다.**

## 결과를 어떻게 읽나

| 상황 | 처리 |
|---|---|
| 배출 맥락 합계가 16,035(폐가구 가이드) 이상 | 별도 가이드로 낸다 |
| 그 아래 | 지금처럼 종량제봉투 가이드의 절로 둔다. 종결 |

`불연성마대`는 8차에서 이미 쟀고 조회에 안 걸렸다(빈칸). 같은 결과가
나와도 이상한 게 아니다 -- 그때는 그게 답이다.

## 묶는 법

키워드 도구는 씨앗을 한 번에 5개까지 받는다. 아래 묶음을 통째로 복사해
[네이버 검색광고 > 키워드도구]에 붙이고 조회한 뒤 다운로드한다.
받은 xlsx는 전부 `data/keywords/gate1-9/`에 넣는다.

그 다음: `python scripts/gate1_batch9_aggregate.py`
"""


def main():
    pairs = [(label, kw) for label, _, kws in TOPICS for kw in kws]
    batches = [pairs[i:i + 5] for i in range(0, len(pairs), 5)]

    out = [HEADER.format(n_kw=len(pairs), n_batch=len(batches)), ""]
    for i, batch in enumerate(batches, 1):
        labels = []
        for label, _ in batch:
            if label not in labels:
                labels.append(label)
        out.append("**%d/%d** - %s" % (i, len(batches), " + ".join(labels)))
        out.append("")
        out.append("```")
        out.extend(kw for _, kw in batch)
        out.append("```")
        out.append("")

    io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(out))
    print("%s -- 키워드 %d개, %d묶음" % (OUT, len(pairs), len(batches)))


if __name__ == "__main__":
    main()
