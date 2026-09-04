# -*- coding: utf-8 -*-
"""실측 6차 — 별칭이 본체보다 큰 자리를 찾는다.

확정 판단 12번(`docs/18`)의 실행이다. 별칭을 붙이는 순간 그 단어의 수요가
안 보이게 된다. 두 번 걸렸다.

    영양제 -> 약        92배   (docs/14)
    러그 <- 요가매트     2.2배  (docs/18)
    범퍼침대 <- 퍼즐매트  8.0배  (docs/18)

셋 다 우연히 발견했다. 이번엔 뒤집힐 만한 자리를 먼저 좁혀서 잰다.

## 대상을 어떻게 좁히나

별칭 360여 개를 다 재면 700키워드가 넘는다. 손으로 못 한다. 세 가지로 자른다.

1. **본체 이름을 품은 별칭은 뺀다.** `쇼파`는 소파의 표기변형이고 `헌 옷`은
   띄어쓰기 차이다. 표기변형은 정의상 같은 단어라 수요가 안 갈린다.
   실제로 뒤집힌 셋은 전부 본체와 **다른 단어**였다
2. **본체 검색량이 작은 페이지부터 본다.** 뒤집히려면 본체가 작아야 한다.
   러그 1,555, 범퍼침대 105, 영양제 45. 큰 페이지의 별칭은 뒤집혀도
   순위가 안 바뀐다

출력:
  data/keywords/gate1-batches-6.md
  (이어서 scripts/build_batch_page.py 로 복붙 페이지를 굽는다)
"""
import csv
import glob
import io
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEMS = os.path.join(ROOT, "site", "src", "data", "items.json")
OUT = os.path.join(ROOT, "data", "keywords", "gate1-batches-6.md")

PER_BATCH = 5
SUFFIXES = ("버리는법", "분리수거")
TOP = int(os.environ.get("TOP", "40"))      # 잴 별칭 수

# 본체가 이만큼 크면 별칭이 뒤집혀도 순위가 안 바뀐다. 재지 않는다.
MAX_OWNER_VOLUME = int(os.environ.get("MAX_OWNER_VOLUME", "4000"))

# 영문, 숫자만인 별칭은 어미를 붙여도 검색어가 안 된다 (led, dvd, kf94).
LATIN_ONLY = re.compile(r"^[A-Za-z0-9 ]+$")


def norm(s):
    return re.sub(r"\s+", "", s)


def one_char_apart(a, b):
    """장농 / 장롱처럼 한 글자만 다른 표기변형. 포함 관계로는 안 걸린다."""
    if len(a) != len(b):
        return False
    return sum(1 for x, y in zip(a, b) if x != y) == 1


def already_measured():
    """지난 실측에서 두 어미로 이미 잰 이름. 같은 걸 또 재지 않는다."""
    done = set()
    for path in glob.glob(os.path.join(ROOT, "data", "keywords", "gate1-volumes-*.csv")):
        for row in csv.DictReader(io.open(path, encoding="utf-8-sig")):
            for col in ("item", "name"):
                if row.get(col):
                    done.add(norm(row[col]))
    return done


HEAD = """# 검색량 실측 6차 — 별칭 재측정

> 별칭 %d개, 키워드 %d개, %d묶음 / 생성일 2026-09-04
> 목적은 **페이지 이름이 수요의 그늘에 있는 자리를 찾는 것**이다.

## 왜 재나

별칭을 붙이면 그 단어의 수요가 안 보인다. 지금까지 세 번 걸렸고 셋 다 우연이었다.

```
영양제 -> 약        92배   docs/14   페이지를 개명했다
러그 <- 요가매트     2.2배  docs/18   페이지를 나눴다
범퍼침대 <- 퍼즐매트  8.0배  docs/18   페이지를 나눴다
```

## 대상을 어떻게 좁혔나

별칭 %d개 전부를 재면 %d묶음이다. 둘로 잘랐다.

1. **본체 이름을 품은 별칭은 뺐다.** `쇼파`(소파), `헌 옷`(헌옷) 같은 표기변형은
   정의상 같은 단어라 수요가 안 갈린다. 뒤집힌 셋은 전부 본체와 **다른 단어**였다
2. **본체 검색량 %s 이하만 봤다.** 뒤집히려면 본체가 작아야 한다
   (러그 1,555, 범퍼침대 105, 영양제 45)

남은 것 중 본체가 작은 순으로 %d개다.

## 결과를 어떻게 읽나

별칭 합계가 본체 검색량보다 크면 셋 중 하나다.

| 상황 | 처리 |
|---|---|
| 같은 물건, 별칭이 훨씬 큼 | **개명.** 영양제 -> 약 |
| 다른 물건, 답도 갈림 | **페이지 분리.** 러그 -> 요가매트 |
| 같은 물건, 차이가 2배 미만 | 그대로 둔다 |

## 하는 법

1. searchad.naver.com 로그인 -> 도구 -> **키워드 도구**
2. 묶음을 붙여넣고 조회 (한 번에 5개까지)
3. 다운로드(엑셀) -> `data/keywords/gate1-6/`
4. 복붙이 번거로우면 `python scripts/build_batch_page.py data/keywords/gate1-batches-6.md`

`월간검색수 PC` + `월간검색수 모바일`의 합이 그 키워드의 검색량이다.

## 대상 목록

| # | 별칭 | 본체 | 본체 검색량 |
|---:|---|---|---:|
%s
"""


def main():
    items = json.load(io.open(ITEMS, encoding="utf-8"))
    done = already_measured()

    cands = []
    total_aliases = 0
    for it in items:
        vol = it.get("monthly_volume") or 0
        for a in (it.get("aliases") or []):
            total_aliases += 1
            if vol > MAX_OWNER_VOLUME:
                continue
            if LATIN_ONLY.match(a):
                continue
            if norm(a) in done:
                continue
            # 표기변형 제외 — 별칭이 본체 이름을 품거나 그 반대
            if norm(it["name"]) in norm(a) or norm(a) in norm(it["name"]):
                continue
            if one_char_apart(norm(a), norm(it["name"])):
                continue
            cands.append({"alias": a, "owner": it["name"],
                          "slug": it["slug"], "vol": vol})

    # 본체가 작은 순. 뒤집힐 여지가 큰 자리부터 본다.
    cands.sort(key=lambda c: (c["vol"], c["owner"], c["alias"]))
    picked = cands[:TOP]

    table = "\n".join(
        "| %d | %s | %s | %s |" % (i, c["alias"], c["owner"], format(c["vol"], ","))
        for i, c in enumerate(picked, 1))

    keywords = []
    for c in picked:
        keywords += ["%s %s" % (c["alias"], suf) for suf in SUFFIXES]
    batches = [keywords[i:i + PER_BATCH] for i in range(0, len(keywords), PER_BATCH)]

    body = [HEAD % (len(picked), len(keywords), len(batches),
                    total_aliases, -(-total_aliases * 2 // PER_BATCH),
                    format(MAX_OWNER_VOLUME, ","), len(picked), table)]
    body.append("## 복붙 묶음 (%d묶음, 키워드 %d개)" % (len(batches), len(keywords)))
    for i, b in enumerate(batches, 1):
        body.append("")
        body.append("**%d/%d**" % (i, len(batches)))
        body.append("")
        body.append("```")
        body.extend(b)
        body.append("```")
    body.append("")

    io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(body))

    print("별칭 %d개 중 후보 %d개 -> 상위 %d개 / 키워드 %d개 / %d묶음"
          % (total_aliases, len(cands), len(picked), len(keywords), len(batches)))
    print("-> %s" % OUT)


if __name__ == "__main__":
    main()
