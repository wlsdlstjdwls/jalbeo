# -*- coding: utf-8 -*-
"""5차 확장분(미측정 신규 품목)의 검색량 실측용 복붙 묶음을 만든다.

docs/09가 남긴 숙제다. items.csv 325개 중 실제로 숫자가 나온 것은 104개뿐이고
나머지는 0이 아니라 '모름'이었다. 5차 확장으로 페이지를 만든 59개가 바로
그 '모름' 구간에서 나왔으므로, 여기에 숫자를 채워야 우선순위를 매길 수 있다.

출력: data/keywords/gate1-batches-2.md
"""
import io
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEMS = os.path.join(ROOT, "site", "src", "data", "items.json")
OUT = os.path.join(ROOT, "data", "keywords", "gate1-batches-2.md")

PER_BATCH = 5   # 네이버 키워드도구가 한 번에 받는 씨앗 수

HEAD = """# 검색량 실측 2차 — 네이버 키워드도구 복붙용

> 대상: 5차 확장으로 발행한 신규 품목 %d개 (monthly_volume이 null인 것)
> 생성일 2026-09-04 / 판정용이 아니라 **우선순위용**이다. 게이트 1은 이미 통과했다.

## 하는 법

1. searchad.naver.com 로그인 -> 도구 -> **키워드 도구**
2. 아래 묶음을 하나씩 입력창에 붙여넣고 조회 (한 번에 5개까지)
3. 결과 표 우측 상단 **다운로드**(엑셀) 클릭 -> `data/keywords/gate1/`에 모으기
4. 파일이 모이면 `scripts/gate1_aggregate.py`로 합산한다

`월간검색수 PC` + `월간검색수 모바일`을 더한 값이 그 키워드의 검색량이다.

## 숫자가 나오면 무엇이 달라지나

- 홈 목록 정렬이 바로잡힌다. 지금은 미측정분이 이름순으로 꼬리에 붙어 있다
- 수요가 큰 품목을 골라 본문을 더 깊게 만들 수 있다 (docs/09 결론)
- 수요가 0에 가까운 품목은 별칭으로 접어 페이지 수를 줄일 근거가 된다

---

"""


def main():
    items = json.load(io.open(ITEMS, encoding="utf-8"))
    targets = [i["name"] for i in items if i.get("monthly_volume") is None]
    targets.sort()

    batches = [targets[i:i + PER_BATCH] for i in range(0, len(targets), PER_BATCH)]
    out = [HEAD % len(targets)]
    out.append("## A안 — `{품목} 버리는법` (%d묶음)\n" % len(batches))
    for n, group in enumerate(batches, 1):
        out.append("**%d/%d**\n" % (n, len(batches)))
        out.append("```")
        out += ["%s 버리는법" % name for name in group]
        out.append("```\n")

    out.append("---\n")
    out.append("## B안 — `{품목} 분리수거` (교차 확인용, %d묶음)\n" % len(batches))
    for n, group in enumerate(batches, 1):
        out.append("**%d/%d**\n" % (n, len(batches)))
        out.append("```")
        out += ["%s 분리수거" % name for name in group]
        out.append("```\n")

    io.open(OUT, "w", encoding="utf-8").write("\n".join(out))
    print("미측정 %d개 -> %d묶음 (A안 B안 각각) -> %s"
          % (len(targets), len(batches), OUT))


if __name__ == "__main__":
    main()
