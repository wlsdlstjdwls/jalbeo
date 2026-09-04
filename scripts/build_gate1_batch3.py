# -*- coding: utf-8 -*-
"""신규 품목 후보의 검색량 실측용 복붙 묶음을 만든다.

2차(`build_gate1_batch2.py`)는 이미 발행한 148개 중 미측정 59개를 재는 거였다.
3차는 목적이 다르다. **페이지가 아직 없는 품목을 추가할지 정하는** 측정이다.

대상: 시드 325개(`data/keywords/items.csv`) 중 발행 품목명에도 별칭에도 없는 것.
그중 표기변형과 수거처 검색어를 빼면 실질 후보가 남는다.

어미는 2차 실측 결과를 따른다. `분리수거`가 `버리는법`을 앞서는 품목이 실재하므로
(뽁뽁이 1,770 대 280, 빨대 1,690 대 45) 소형/재질 품목은 두 어미를 다 잰다.
대형폐기물로 나갈 품목은 분리수거 대상이 아니라 A안만 잰다.

출력: data/keywords/gate1-batches-3.md
"""
import csv
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEEDS = os.path.join(ROOT, "data", "keywords", "items.csv")
ITEMS = os.path.join(ROOT, "site", "src", "data", "items.json")
OUT = os.path.join(ROOT, "data", "keywords", "gate1-batches-3.md")

PER_BATCH = 5   # 네이버 키워드도구가 한 번에 받는 씨앗 수

# 후보와 어미. both=True면 분리수거까지 잰다
CANDIDATES = [
    ("에어컨", False),
    ("정수기", False),
    ("공기청정기", False),
    ("오븐", False),
    ("킥보드", False),
    ("전선", True),
    ("나무젓가락", True),
    ("가위", True),
    ("약", True),
]

# 남은 시드 중 후보로 안 올린 것과 그 이유
DROPPED = [
    ("cd, tv, led 전구, 된장, 고추장 된장, 뽁뽁이 비닐, 코팅된 종이, 다 쓴 치약, "
     "아이돌앨범, 은박 보냉백, pcm 아이스팩, 부푼 보조배터리, 일회용 보조배터리, "
     "안쓰는 그릇, 플라스틱 캔, 삶은옥수수, 찐옥수수, 옥수수, 고추씨, 꽃게 톱밥, pe폼",
     "이미 발행된 품목의 표기변형이다. 별칭이지 페이지가 아니다 (docs/13)"),
    ("아파트 냄비, 아파트 선풍기, 아파트 책, 냄비 후라이팬, 이불 베개, 베개 이불, 가위 칼",
     "두 품목을 붙여 친 조합어다. 페이지는 각각 이미 있다"),
    ("다이소, 편의점",
     "품목이 아니라 수거처 검색어다. 페이지 성격이 달라 따로 판단한다"),
    ("케이블", "전선의 별칭으로 붙인다"),
    ("폐약", "약의 별칭으로 붙인다"),
]

HEAD = """# 검색량 실측 3차 — 신규 품목 후보

> 대상: 아직 페이지도 별칭도 없는 신규 품목 후보 %d개
> 생성일 2026-09-04 / 목적은 **품목 추가 여부 판단**이다. 게이트 1은 이미 통과했다.

## 하는 법

1. searchad.naver.com 로그인 -> 도구 -> **키워드 도구**
2. 아래 묶음을 하나씩 입력창에 붙여넣고 조회 (한 번에 5개까지)
3. 결과 표 우측 상단 **다운로드**(엑셀) 클릭 -> `data/keywords/gate1-3/`에 모으기
4. 파일이 모이면 `scripts/gate1_batch2_aggregate.py`의 SRC를 `gate1-3`으로 바꿔 돌린다

`월간검색수 PC` + `월간검색수 모바일`을 더한 값이 그 키워드의 검색량이다.

## 어미를 두 개 쓰는 이유

2차 실측에서 어미가 품목마다 뒤집혔다.

```
뽁뽁이   버리는법   280  /  분리수거 1,770
빨대     버리는법    45  /  분리수거 1,690
보조배터리 버리는법 9,660 /  분리수거 1,130
```

한 어미만 재면 품목을 잘못 버릴 수 있다. 다만 대형폐기물로 나갈 품목
(에어컨, 정수기, 공기청정기, 오븐, 킥보드)은 분리수거 대상이 아니므로 A안만 잰다.

## 추가 기준

이 숫자로 페이지를 만들지 정한다. 2차 실측 하위권이 화병 35, 나뭇가지 40이었다.
**합계 300 미만이면 별칭으로 넘기고 페이지를 만들지 않는다.**
"""

# 2차 복붙 묶음 8/12가 통째로 안 돌아갔다. 이 5개는 분리수거만 숫자가 있다
MISSING2 = ["염색약", "영양제", "옥수수대", "유리병", "유모차"]

TAIL = """
## 덤 — 2차에서 빠진 5개

`gate1-batches-2.md`의 8/12 묶음이 안 돌아가서 이 품목들은 `분리수거`만 숫자가 있다.
이미 발행된 페이지라 추가 판단용은 아니고, 우선순위 정렬용으로 채운다.

```
%s
```

## 후보에서 뺀 시드와 이유

| 시드 | 뺀 이유 |
|---|---|
%s
"""


def norm(s):
    return re.sub(r"\s+", "", s)


def leftover():
    items = json.load(open(ITEMS, encoding="utf-8"))
    have = set()
    for it in items:
        have.add(norm(it["name"]))
        for a in it.get("aliases", []):
            have.add(norm(a))
    with open(SEEDS, encoding="utf-8-sig") as f:
        return [r["item"] for r in csv.DictReader(f) if norm(r["item"]) not in have]


def main():
    left = leftover()
    named = {norm(n) for n, _ in CANDIDATES}
    unseen = [s for s in left if norm(s) in named]

    keywords = [n + " 버리는법" for n, _ in CANDIDATES]
    keywords += [n + " 분리수거" for n, both in CANDIDATES if both]

    batches = [keywords[i:i + PER_BATCH] for i in range(0, len(keywords), PER_BATCH)]

    body = [HEAD % len(CANDIDATES)]
    body.append("")
    body.append("## 복붙 묶음 (%d묶음, 키워드 %d개)" % (len(batches), len(keywords)))
    for i, b in enumerate(batches, 1):
        body.append("")
        body.append("**%d/%d**" % (i, len(batches)))
        body.append("")
        body.append("```")
        body.extend(b)
        body.append("```")
    rows = chr(10).join("| %s | %s |" % (s, why) for s, why in DROPPED)
    miss = chr(10).join(n + " 버리는법" for n in MISSING2)
    body.append(TAIL % (miss, rows))

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(body))

    print("남은 시드 %d개 -> 후보 %d개 (시드에 있던 것 %d개)"
          % (len(left), len(CANDIDATES), len(unseen)))
    print("키워드 %d개 / %d묶음" % (len(keywords), len(batches)))
    print("-> %s" % OUT)


if __name__ == "__main__":
    main()
