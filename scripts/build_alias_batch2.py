# -*- coding: utf-8 -*-
"""실측 7차 -- 별칭 재측정 2차. 본체 검색량 4,000 초과 페이지의 별칭.

`docs/19`(실측 6차)는 뒤집힐 여지가 큰 쪽(본체 <= 4,000)만 40개 쟀다.
이번엔 나머지 큰 본체 쪽을 같은 필터로 재려는다.

대상 필터는 build_alias_batch.py와 동일하다.
  1. 표기변형(별칭이 본체 이름을 품거나 한 글자 차이) 제외
  2. 영문/숫자만인 별칭 제외 (어미를 못 받는다)
  3. 과거 어느 실측 라운드(gate1-volumes-*.csv)에서든 이미 잰 이름 제외
     -- 별칭 상당수가 애초에 325 시드 후보로 한 번씩 재본 이름이라
        실제로 다시 재야 할 건 소수만 남는다

출력:
  data/keywords/gate1-batches-7.md
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
OUT = os.path.join(ROOT, "data", "keywords", "gate1-batches-7.md")

PER_BATCH = 5
SUFFIXES = ("버리는법", "분리수거")

# 실측 6차가 이미 본 경계. 이번엔 그 반대쪽(본체가 큰 페이지)을 본다.
MIN_OWNER_VOLUME = int(os.environ.get("MIN_OWNER_VOLUME", "4000"))

LATIN_ONLY = re.compile(r"^[A-Za-z0-9 ]+$")


def norm(s):
    return re.sub(r"\s+", "", s)


def one_char_apart(a, b):
    if len(a) != len(b):
        return False
    return sum(1 for x, y in zip(a, b) if x != y) == 1


def already_measured():
    done = set()
    for path in glob.glob(os.path.join(ROOT, "data", "keywords", "gate1-volumes-*.csv")):
        for row in csv.DictReader(io.open(path, encoding="utf-8-sig")):
            for col in ("item", "name", "alias"):
                if row.get(col):
                    done.add(norm(row[col]))
    return done


HEAD = """# 검색량 실측 7차 -- 별칭 재측정 2차

> 별칭 %d개, 키워드 %d개, %d묶음 / 생성일 2026-09-04
> 실측 6차(`docs/19`)가 안 본 쪽 -- 본체 검색량 %s 초과 페이지의 별칭.

## 왜 재나

`docs/19`는 뒤집힐 여지가 큰 쪽(본체 작은 페이지)만 40개 쟀다. 남은 별칭은
본체가 커서 뒤집혀도 순위는 안 바뀌지만, 확률이 낮은 것과 없는 것은 다르다.

## 대상을 어떻게 좁혔나

전체 별칭 중 아래를 뺐다.

1. **표기변형 제외.** 별칭이 본체 이름을 품거나 한 글자 차이면 정의상 같은 단어다
2. **영문/숫자만인 별칭 제외.** 어미를 붙여도 검색어가 안 된다
3. **과거 실측(1~6차)에서 이미 잰 이름 제외.** 별칭 상당수가 325 시드 후보로
   한 번씩 재본 이름이라, 실제로 새로 잴 건 소수만 남는다

남은 것 %d개.

## 결과를 어떻게 읽나

| 상황 | 처리 |
|---|---|
| 같은 물건, 별칭이 훨씬 큼 | **개명** |
| 다른 물건, 답도 갈림 | **페이지 분리** |
| 같은 물건, 차이가 2배 미만 | 그대로 둔다 |

## 하는 법

1. searchad.naver.com 로그인 -> 도구 -> **키워드 도구**
2. 묶음을 붙여넣고 조회 (한 번에 5개까지)
3. 다운로드(엑셀) -> `data/keywords/gate1-7/`
4. 복붙이 번거로우면 `python scripts/build_batch_page.py data/keywords/gate1-batches-7.md`

## 대상 목록

| # | 별칭 | 본체 | 본체 검색량 |
|---:|---|---|---:|
%s
"""


def main():
    items = json.load(io.open(ITEMS, encoding="utf-8"))
    done = already_measured()

    cands = []
    for it in items:
        vol = it.get("monthly_volume") or 0
        if vol <= MIN_OWNER_VOLUME:
            continue
        for a in (it.get("aliases") or []):
            if LATIN_ONLY.match(a):
                continue
            if norm(a) in done:
                continue
            if norm(it["name"]) in norm(a) or norm(a) in norm(it["name"]):
                continue
            if one_char_apart(norm(a), norm(it["name"])):
                continue
            cands.append({"alias": a, "owner": it["name"],
                          "slug": it["slug"], "vol": vol})

    cands.sort(key=lambda c: (c["vol"], c["owner"], c["alias"]))

    table = "\n".join(
        "| %d | %s | %s | %s |" % (i, c["alias"], c["owner"], format(c["vol"], ","))
        for i, c in enumerate(cands, 1))

    keywords = []
    for c in cands:
        keywords += ["%s %s" % (c["alias"], suf) for suf in SUFFIXES]
    batches = [keywords[i:i + PER_BATCH] for i in range(0, len(keywords), PER_BATCH)]

    body = [HEAD % (len(cands), len(keywords), len(batches),
                    format(MIN_OWNER_VOLUME, ","), len(cands), table)]
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

    print("후보 %d개 / 키워드 %d개 / %d묶음" % (len(cands), len(keywords), len(batches)))
    print("-> %s" % OUT)


if __name__ == "__main__":
    main()
