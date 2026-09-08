# -*- coding: utf-8 -*-
"""실측 15차 묶음 -- 저본체 별칭. 본체 검색량 1,000 미만 페이지의 별칭 전량.

판단 12번(별칭 목록은 페이지를 나눌 후보 목록이기도 하다)의 계통 측정이다.
실측 6차(`docs/19`)가 본체 4,000 이하 별칭 40개를 재서 5개가 본체의 2배를
넘었고, 그중 셋이 개명 또는 분리로 갔다. 이번 대상은 그때보다 본체가 훨씬
작은 쪽이다 -- 본체가 1,000 미만이면 별칭이 뒤집혔을 때 사이트 우선순위가
그대로 바뀌므로 판단 14번의 생략 조건을 못 쓴다.

원천: data/keywords/candidates-low-owner-aliases.csv (`220921b`에서 리스트업)
      items.json의 aliases 중 본체 검색량 1,000 미만인 것 198개

여기서 다시 뺀 것 5개.
  1. 이미 두 어미 기준으로 잰 이름 4개 -- 한복(11차 115), 책꽂이(11차 50),
     식기세척기(11차 30), 잡지(12차 30). 전부 판정까지 끝나 별칭으로 갔다
  2. 중복 1개 -- 보행기(유모차와 휠체어 양쪽 별칭)
가스렌지는 1차 덤프에만 있고 두 어미 기준이 아니라 다시 잰다(판단 11).

묶음 순서는 **본체 검색량 내림차순**이다. 본체가 1,000에 가까울수록 2배
역전이 났을 때 절대값이 커서 페이지가 될 확률이 높다. 중간에 끊더라도
위쪽 묶음이 수확이 크다.

출력: data/keywords/gate1-batches-15.md
그 다음: python scripts/build_batch_page.py data/keywords/gate1-batches-15.md
받은 xlsx는 data/keywords/gate1-15/ 에 넣고 python scripts/gate1_batch15_aggregate.py
"""
import csv
import io
import os
import re
import sys
from collections import OrderedDict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KW = os.path.join(ROOT, "data", "keywords")
SRC = os.path.join(KW, "candidates-low-owner-aliases.csv")
OUT = os.path.join(KW, "gate1-batches-15.md")

PER_BATCH = 5
SUFFIXES = ("버리는법", "분리수거")

# 두 어미 기준으로 이미 잰 파일들(판단 11). 1차 덤프(gate1-volumes.csv)와
# 키워드 단위 파일(8, 9, 10차)은 어미 커버리지가 달라 비교 대상이 아니다.
TWO_SUFFIX_ROUNDS = ("2", "3", "4", "5", "6", "11", "12", "13", "14")


def norm(s):
    return re.sub(r"\s+", "", str(s))


def already_measured():
    """이름 -> (회차, 합계). 두 어미 기준 실측만 본다."""
    done = {}
    for n in TWO_SUFFIX_ROUNDS:
        path = os.path.join(KW, "gate1-volumes-%s.csv" % n)
        if not os.path.exists(path):
            continue
        for row in csv.DictReader(io.open(path, encoding="utf-8-sig")):
            name = norm(row.get("topic") or row.get("name")
                        or row.get("item") or row.get("alias") or "")
            if name and name not in done:
                done[name] = (n, row.get("total") or "")
    return done


def load():
    """(별칭, 본체, 본체슬러그, 본체검색량) 목록과 제외 목록."""
    done = already_measured()
    rows = list(csv.DictReader(io.open(SRC, encoding="utf-8-sig")))
    seen, keep, skipped = set(), [], []
    for r in rows:
        alias = r["alias"].strip()
        key = norm(alias)
        if key in seen:
            skipped.append((alias, r["owner"], "중복"))
            continue
        seen.add(key)
        if key in done:
            n, total = done[key]
            skipped.append((alias, r["owner"], "실측 %s차 %s" % (n, total or "미집계")))
            continue
        keep.append((alias, r["owner"], r["owner_slug"], int(r["owner_volume"])))
    return keep, skipped


def grouped(keep):
    """본체별로 묶고 본체 검색량 내림차순. 미측정 본체(0)는 맨 뒤."""
    g = OrderedDict()
    for alias, owner, slug, vol in keep:
        g.setdefault((owner, slug, vol), []).append(alias)
    return sorted(g.items(), key=lambda kv: (-kv[0][2], kv[0][0]))


HEADER = """# 검색량 실측 15차 -- 저본체 별칭

> 별칭 {n_alias}개, 본체 {n_owner}개, 키워드 {n_kw}개, {n_batch}묶음 / 생성일 2026-09-08
> 원천 `data/keywords/candidates-low-owner-aliases.csv`
> 생성 `python scripts/build_low_owner_alias_batch.py`

## 왜 재나

판단 12번이다. **별칭을 붙이면 그 단어의 수요가 안 보인다.** 별칭 목록은
페이지를 나눌 후보 목록이기도 하다.

실측 6차(`docs/19`)가 본체 4,000 이하 별칭 40개를 재서 5개가 본체의 2배를
넘었고, 그중 셋이 개명이나 분리로 갔다. 이번 대상은 그보다 아래다 --
**본체 검색량이 1,000 미만**인 페이지의 별칭 전량이다. 본체가 이만큼 작으면
별칭이 뒤집혔을 때 사이트 우선순위가 그대로 바뀌므로 판단 14번(실측 생략)의
조건을 못 쓴다.

이미 알고 있는 예시가 목록 안에 있다. 마우스(590)의 별칭에 키보드가 있고,
이어폰(270)의 별칭에 에어팟과 헤드폰이 있고, 헤어드라이어(55)의 별칭에
고데기가 있다. 뒤집혔는지는 재야 안다(판단 16: 빈도나 감으로 자르지 않는다).

## 이번 라운드가 정하는 것

별칭마다 셋 중 하나다.

| 결과 | 조건 | 처분 |
|---|---|---|
| 유지 | 별칭 < 본체 | 그대로 별칭 |
| 개명 | 별칭 >= 본체 2배 **이고 답이 같다** | 페이지 이름을 별칭으로 바꾼다 |
| 분리 | 별칭 >= 본체 2배 **이고 답이 갈린다** | 새 페이지 |

2배를 넘어도 자동으로 페이지가 아니다. 판단 40번대로 **그 페이지의 첫 문단이
이 사람의 질문인지**를 보고 가른다. 수수료 축이 붙는 별칭은 판단 39번(등재 수가
자릿수로 다르면 같은 물건이 아니다)과 판단 42번(`build_fee_stats`를 돌려 본체
중앙값이 움직이면 별칭이 아니다)도 같이 본다.

## 순서

묶음은 **본체 검색량 내림차순**이다. 본체가 1,000에 가까울수록 2배 역전의
절대값이 커서 페이지가 될 확률이 높다. 중간에 끊어도 위쪽이 수확이 크다.
본체 검색량 `-`는 미측정이다(0이 아니다). 그 셋은 맨 뒤에 둔다.

{owner_table}

## 뺀 것 {n_skip}개

{skip_table}

## 묶는 법

키워드 도구는 씨앗을 한 번에 5개까지 받는다. 아래 묶음을 통째로 복사해
[네이버 검색광고 > 키워드도구]에 붙이고 조회한 뒤 다운로드한다.
받은 xlsx는 전부 `data/keywords/gate1-15/`에 넣는다.
한 묶음이 두 주제 경계를 걸치기도 한다. 집계가 이름으로 다시 모으니 상관없다.
"""


def main():
    keep, skipped = load()
    groups = grouped(keep)

    pairs = []
    for (owner, slug, vol), aliases in groups:
        for alias in aliases:
            for suf in SUFFIXES:
                pairs.append((alias, "%s %s" % (alias, suf)))

    batches = [pairs[i:i + PER_BATCH] for i in range(0, len(pairs), PER_BATCH)]

    owner_table = "\n".join(
        ["| 본체 | 본체 검색량 | 별칭 |", "|---|---|---|"] +
        ["| %s | %s | %s |" % (owner, format(vol, ",") if vol else "-",
                               ", ".join(aliases))
         for (owner, slug, vol), aliases in groups])

    skip_table = "\n".join(
        ["| 뺀 별칭 | 본체 | 이유 |", "|---|---|---|"] +
        ["| %s | %s | %s |" % (a, o, why) for a, o, why in skipped])

    out = [HEADER.format(n_alias=len(keep), n_owner=len(groups),
                         n_kw=len(pairs), n_batch=len(batches),
                         n_skip=len(skipped),
                         owner_table=owner_table, skip_table=skip_table), ""]
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
    print("%s -- 별칭 %d개, 본체 %d개, 키워드 %d개, %d묶음"
          % (OUT, len(keep), len(groups), len(pairs), len(batches)))
    print("뺀 것 %d개: %s"
          % (len(skipped), ", ".join("%s(%s)" % (a, w) for a, o, w in skipped)))


if __name__ == "__main__":
    main()
