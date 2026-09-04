# -*- coding: utf-8 -*-
"""1차 실측 품목의 두 어미 재측정용 복붙 묶음을 만든다.

`docs/14`가 남긴 숙제다. 1차(`gate1-volumes.csv`)는 씨앗 실측이 아니라 연관어
덤프였다. 품목마다 우연히 걸린 어미가 달라서 합계의 기준이 제각각이다.

    이불   26,905 = 버리는방법 19,580 + 버리는법 3,140 + 버리기 2,380 + ...
    선풍기 12,120 = 버리는법 12,120 (어미 1개만 걸림)

이 값들을 2차/3차와 한 컬럼에 놓고 정렬하면 순위가 뒤집힌다. 그래서 1차 품목을
2차와 같은 자(`버리는법` + `분리수거` 두 씨앗)로 다시 잰다.

대상에서 빼는 것:
  - 2차에서 이미 두 어미로 잰 품목 (`gate1-volumes-2.csv`)
  - 3차에서 방금 잰 신규 품목 (`gate1-volumes-3.csv`)
  - 1차 덤프에 이미 두 어미가 다 걸린 품목 (3개)

출력: data/keywords/gate1-batches-4.md
"""
import csv
import io
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEMS = os.path.join(ROOT, "site", "src", "data", "items.json")
KW = os.path.join(ROOT, "data", "keywords")
V1 = os.path.join(KW, "gate1-volumes.csv")
V2 = os.path.join(KW, "gate1-volumes-2.csv")
V3 = os.path.join(KW, "gate1-volumes-3.csv")
OUT = os.path.join(KW, "gate1-batches-4.md")

PER_BATCH = 5   # 네이버 키워드도구가 한 번에 받는 씨앗 수
SUFFIXES = ("버리는법", "분리수거")

# 2차 8/12 묶음이 통째로 안 돌아가 `분리수거`만 남은 품목들. `버리는법`만 채우면 된다.
# 영양제는 3차에서 `약`으로 개명하며 두 어미를 다 쟀으므로 뺀다.
MISSING_A = ["염색약", "옥수수대", "유리병", "유모차"]

HEAD = """# 검색량 실측 4차 — 1차 품목 두 어미 재측정

> 대상: 1차 실측 품목 %d개 (키워드 %d개, %d묶음)
> 생성일 2026-09-04 / 목적은 **정렬 기준 통일**이다. 판정용이 아니다.

## 왜 다시 재나

1차(`gate1-volumes.csv`)는 씨앗 실측이 아니라 연관어 덤프였다. 품목마다
우연히 걸린 어미가 달라서 합계의 기준이 제각각이다.

```
이불   26,905 = 버리는방법 19,580 + 버리는법 3,140 + 버리기 2,380 + ...
선풍기 12,120 = 버리는법 12,120 (어미 1개만 걸림)
```

1차 92개를 2차 자로 다시 재면 232,525 -> 166,895(71%%)로 줄고, 감소폭이
품목마다 다르다(이불 11%%, 화분 8%%, 선풍기 100%%). 한 컬럼에 놓고 정렬하면
순위가 뒤집힌다. **이 표가 채워지기 전까지 monthly_volume은 절대 크기가
아니라 대략의 등급으로만 읽는다.**

## 어미는 두 개 다 잰다

어미는 품목마다 뒤집힌다(`docs/14`). 한쪽만 재면 품목을 잘못 버린다.

```
빨대       버리는법    45  /  분리수거 1,690    38배
조개껍질   버리는법    25  /  분리수거 1,570    63배
보조배터리 버리는법 9,660  /  분리수거 1,130    반대 방향
```

## 하는 법

1. searchad.naver.com 로그인 -> 도구 -> **키워드 도구**
2. 아래 묶음을 하나씩 입력창에 붙여넣고 조회 (한 번에 5개까지)
3. 결과 표 우측 상단 **다운로드**(엑셀) 클릭 -> `data/keywords/gate1-4/`에 모으기
4. 파일이 모이면 `scripts/gate1_batch2_aggregate.py`의 SRC를 `gate1-4`로 바꿔 돌린다

`월간검색수 PC` + `월간검색수 모바일`을 더한 값이 그 키워드의 검색량이다.

한 품목의 두 어미는 붙여서 넣었다. 묶음 경계에서만 갈라진다. 2차 때
8/12 묶음이 통째로 안 돌아가 5개 품목이 한 어미만 남은 적이 있으니,
**빠진 묶음 번호를 적어두고 다시 돌린다.**
그때 반쪽으로 남은 4개(염색약, 옥수수대, 유리병, 유모차)는 마지막 묶음에 몰아
넣었다. 이 품목들은 `버리는법`만 채우면 두 어미가 맞춰진다.

## 대상에서 뺀 것

| 구분 | 개수 | 이유 |
|---|---:|---|
| 2차 실측분 | %d | 이미 두 어미로 쟀다 (`gate1-volumes-2.csv`) |
| 3차 실측분 | %d | 신규 품목 후보로 방금 쟀다 (`gate1-volumes-3.csv`) |
| 두 어미 기측정 | %d | 1차 덤프에 두 어미가 다 걸렸다 — %s |
"""


def norm(s):
    return s.replace(" ", "")


def main():
    items = json.load(io.open(ITEMS, encoding="utf-8"))
    v2 = {r["slug"] for r in csv.DictReader(io.open(V2, encoding="utf-8-sig"))}
    v3 = {norm(r["item"]) for r in csv.DictReader(io.open(V3, encoding="utf-8-sig"))}

    # 1차 덤프에서 품목별로 어떤 어미가 걸렸는지 모은다
    seen = {}
    for r in csv.DictReader(io.open(V1, encoding="utf-8-sig")):
        if not r["item"]:
            continue
        got = seen.setdefault(norm(r["item"]), set())
        for suf in SUFFIXES:
            if norm(r["keyword"]).endswith(suf):
                got.add(suf)

    targets, both, skipped_v2, skipped_v3 = [], [], 0, 0
    for it in items:
        if it.get("monthly_volume") is None:
            continue            # 미측정분은 2차 대상이었다
        key = norm(it["name"])
        if it["slug"] in v2:
            skipped_v2 += 1
            continue
        if key in v3:
            skipped_v3 += 1
            continue
        if key not in seen:
            continue            # 1차 덤프에 없다 = 1차 품목이 아니다
        if seen[key] >= set(SUFFIXES):
            both.append(it["name"])
            continue
        targets.append(it["name"])

    targets.sort()
    keywords = []
    for name in targets:
        keywords += ["%s %s" % (name, suf) for suf in SUFFIXES]
    # 반쪽으로 남은 4개는 마지막 묶음에 몰아 넣는다. 품목 경계와 겹치지 않게 따로 끊는다.
    batches = [keywords[i:i + PER_BATCH] for i in range(0, len(keywords), PER_BATCH)]
    batches.append(["%s 버리는법" % n for n in MISSING_A])
    keywords += batches[-1]

    body = [HEAD % (len(targets), len(keywords), len(batches),
                    skipped_v2, skipped_v3, len(both), ", ".join(sorted(both)))]
    body.append("")
    body.append("## 복붙 묶음 (%d묶음, 키워드 %d개)" % (len(batches), len(keywords)))
    for i, b in enumerate(batches, 1):
        body.append("")
        body.append("**%d/%d**" % (i, len(batches)))
        body.append("")
        body.append("```")
        body.extend(b)
        body.append("```")
    body.append("")

    with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(body))

    print("대상 %d품목 / 키워드 %d개 / %d묶음" % (len(targets), len(keywords), len(batches)))
    print("뺀 것 — 2차 %d, 3차 %d, 두 어미 기측정 %d (%s)"
          % (skipped_v2, skipped_v3, len(both), ", ".join(sorted(both))))
    print("-> %s" % OUT)


if __name__ == "__main__":
    main()
