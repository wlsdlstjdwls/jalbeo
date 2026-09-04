# -*- coding: utf-8 -*-
"""실측 5차 복붙 묶음 — 재크롤 2차 실측 대상 + 보류 2개 재측정.

입력:
  data/keywords/candidates-r2-triage.csv   `triage_candidates_r2.py` 산출물
                                           (`신규후보`, `별칭확인`만 잰다)
출력:
  data/keywords/gate1-batches-5.md

두 어미(`버리는법`, `분리수거`)를 한 품목당 붙여서 넣는다. 어미는 품목마다
뒤집히므로(`docs/14`, `docs/16`) 한쪽만 재면 품목을 잘못 버린다.

보류 2개(에어컨, 오븐)는 어미가 다르다. `docs/14`가 남긴 숙제로,
품목 어미가 아니라 서비스 어미(`무상수거`, `철거비용`)로 다시 잰다.
선풍기가 12,120인데 에어컨이 50이었던 건 수요가 없어서가 아니라
어미가 품목이 아니라 서비스에 붙어 있어서였다.
"""
import csv
import io
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KW = os.path.join(ROOT, "data", "keywords")
SRC = os.path.join(KW, "candidates-r2-triage.csv")
OUT = os.path.join(KW, "gate1-batches-5.md")

PER_BATCH = 5           # 네이버 키워드도구가 한 번에 받는 씨앗 수
SUFFIXES = ("버리는법", "분리수거")

# 실측하는 분류. 나머지는 별칭, 가이드축, 총칭, 조합어, B층, 범위밖으로 이미 갈렸다.
MEASURE = ("신규후보", "별칭확인")

# 보류 2개. 품목 어미로는 각각 65, 50이었다 (`docs/14` 2번).
HOLD = [
    ("에어컨", ("무상수거", "철거비용")),
    ("오븐", ("무상수거", "철거비용")),
]

HEAD = """# 검색량 실측 5차 — 재크롤 2차 실측 대상 %d개 + 보류 2개

> 키워드 %d개, %d묶음 / 생성일 2026-09-04
> 목적은 **발행 후보 선별**이다. 정렬 기준 통일(4차)과는 다른 작업이다.

## 후보가 어디서 나왔나

시드 325개는 소진됐다. 발행 154, 별칭 329, 나머지는 표기변형과 조합어다.
그래서 씨앗을 사람이 떠올린 명사가 아니라 **발행분에서** 뽑았다
(`scripts/crawl_autocomplete_r2.py`). 발행 품목명 154개와 별칭 329개를
자동완성에 넣고, 돌아온 문자열에서 어미를 떼어 앞의 명사를 모았다.
어미에는 1차에 없던 거래/절차 축(`무상수거`, `무료수거`, `철거비용`)을 더했다.

질의 2,128건에서 627개가 걸렸고, 이미 아는 것(발행명, 별칭, 시드 325 =
고유 511개)을 빼 100개가 남았다. 그 100개를 `scripts/triage_candidates_r2.py`가
8종으로 갈랐고, 여기 오는 건 그중 두 종뿐이다.

```
신규후보  10   기존 어느 페이지와도 답이 다르다
별칭확인   4   답은 같지만 수요를 확인한다 (아래)
별칭      25   기존 페이지에 붙인다. 재지 않는다
가이드축  21   품목이 아니라 절차다
총칭       9   분류 이름이라 페이지가 답할 게 없다
조합어     9   발행 품목에 어미가 두 겹
B층폐기    8   품목 x 지자체 (확정 판단 1번)
범위밖    14   건축 철거, 배송, 행정 절차
```

### 별칭확인을 왜 재나

답이 같으면 별칭이다(확정 판단 8번). 그런데 `docs/14`에서 `영양제`가 `약`의
1/92짜리 단어인 채로 페이지 이름을 달고 있었다. 답이 같아도 수요가 크면
**페이지 이름을 바꿔야 한다.** 요가매트, 퍼즐매트, 놀이매트, 주방 발매트가
러그와 범퍼침대에 대해 그 자리인지 확인한다.

## 어미는 두 개 다 잰다

```
빨대       버리는법    45  /  분리수거 1,690    38배
조개껍질   버리는법    25  /  분리수거 1,570    63배
보조배터리 버리는법 9,660  /  분리수거 1,130    반대 방향
```

한쪽만 재면 품목을 잘못 버린다. 기준선은 3차와 같은 **두 어미 합계 300**이다
(2차 하위권이 화병 35, 나뭇가지 40).

## 보류 2개는 어미가 다르다

에어컨 50, 오븐 65였다(`docs/14`). 선풍기가 12,120인데 에어컨이 50일 리가 없다.
어미가 품목이 아니라 서비스에 붙어 있었다. `무상수거`, `철거비용`으로 다시 잰다.
이 둘은 판정 기준선도 다르다 — 품목 페이지가 받을 수 있는 검색어인지부터 본다.

## 하는 법

1. searchad.naver.com 로그인 -> 도구 -> **키워드 도구**
2. 아래 묶음을 하나씩 입력창에 붙여넣고 조회 (한 번에 5개까지)
3. 결과 표 우측 상단 **다운로드**(엑셀) 클릭 -> `data/keywords/gate1-5/`에 모으기
4. 파일이 모이면 `python scripts/gate1_batch5_aggregate.py`

`월간검색수 PC` + `월간검색수 모바일`을 더한 값이 그 키워드의 검색량이다.
**안 돌아간 묶음 번호를 적어둔다.** 2차 때 8/12 묶음이 통째로 빠져
5개 품목이 한 어미만 남았고, 그걸 4차까지 끌고 왔다.

## 실측 대상

| # | 품목 | 분류 | 등장 | 질의 | 왜 재나 | 예시 자동완성 |
|---:|---|---|---:|---:|---|---|
%s
"""


def main():
    if not os.path.exists(SRC):
        sys.exit("%s 가 없다. 먼저 scripts/triage_candidates_r2.py 를 돌린다." % SRC)

    rows = [r for r in csv.DictReader(io.open(SRC, encoding="utf-8-sig"))
            if r["decision"] in MEASURE]

    table = "\n".join(
        "| %d | %s | %s | %s | %s | %s | %s |" % (
            i, r["item"], r["decision"], r["freq"], r["n_queries"],
            r["note"], r["sample_suggestion"])
        for i, r in enumerate(rows, 1))

    keywords = []
    for r in rows:
        keywords += ["%s %s" % (r["item"], suf) for suf in SUFFIXES]
    batches = [keywords[i:i + PER_BATCH] for i in range(0, len(keywords), PER_BATCH)]

    # 보류 2개는 어미가 달라 마지막 묶음에 따로 끊는다.
    hold_kw = ["%s %s" % (n, s) for n, sufs in HOLD for s in sufs]
    batches.append(hold_kw)
    keywords += hold_kw

    body = [HEAD % (len(rows), len(keywords), len(batches), table)]
    body.append("## 복붙 묶음 (%d묶음, 키워드 %d개)" % (len(batches), len(keywords)))
    for i, b in enumerate(batches, 1):
        body.append("")
        body.append("**%d/%d**%s" % (i, len(batches),
                                     " — 보류 2개 재측정" if i == len(batches) else ""))
        body.append("")
        body.append("```")
        body.extend(b)
        body.append("```")
    body.append("")

    with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(body))

    print("실측 대상 %d품목 / 키워드 %d개 / %d묶음 -> %s"
          % (len(rows), len(keywords), len(batches), OUT))


if __name__ == "__main__":
    main()
