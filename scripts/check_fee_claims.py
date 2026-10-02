# -*- coding: utf-8 -*-
"""본문의 수수료 수치를 fees.json과 대조한다.

FeeTable이 같은 화면에 '{regions}개 지자체 공개 요금의 중앙값'을 띄우므로
본문이 다른 숫자를 말하면 한 페이지 안에서 답이 둘이 된다. 그걸 막는 검사다.

    python scripts/check_fee_claims.py        # 어긋난 것만 출력, 있으면 exit 1

수수료 데이터를 다시 수집하거나(`normalize_fees.py`) 통계를 다시 낸 뒤
(`build_fee_stats.py`) 돌린다. 숫자가 바뀌면 본문도 따라가야 한다.
"""
import glob
import io
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEES = os.path.join(ROOT, "site", "src", "data", "fees.json")
ITEMS = os.path.join(ROOT, "site", "src", "data", "items.json")
CONTENT = os.path.join(ROOT, "site", "src", "content", "items", "*.md")

# 수수료표를 수집한 시군구 총수. "48개 시군구 가운데 8곳" 같은 문장의 앞 숫자다.
# 손으로 적어 두면 지역이 늘 때 본문의 낡은 총수가 통과한다. 데이터에서 센다.
def _count_regions():
    import csv as _csv, os as _os
    path = _os.path.join(_os.path.dirname(__file__), "..", "data", "processed", "fees.csv")
    with open(path, encoding="utf-8") as f:
        return len({(r["sido"], r["sigungu"]) for r in _csv.DictReader(f)})
TOTAL_REGIONS = _count_regions()

# (라벨, 정규식, fees.json에서 비교할 필드)
CLAIMS = [
    ("지역수", re.compile(r"(\d+)\s*개?\s*시군구 품목표"), "regions"),
    # '요금을 공개한'과 '수수료를 공개한'이 섞여 쓰인다. 밥상이 후자로 적혀
    # 있어 32곳 -> 31곳 변경을 검사기가 놓쳤다 (docs/55)
    ("지역수", re.compile(r"(?:요금|수수료)(?:을|를) 공개한 \*{0,2}(\d+)\s*곳"), "regions"),
    ("지역수", re.compile(r"\*{0,2}(\d+)\s*곳의 (?:중앙값|가운데값)"), "regions"),
    ("지역수", re.compile(r"(?:수수료를 )?확인한 \*{0,2}(\d+)\s*개 시군구"), "regions"),
    ("단위지역수", re.compile(r"\|\s*\*{0,2}(\d+)곳\s*\*{0,2}\s*\|"), "regions"),
    # '올려둔'과 '올려 둔'이 둘 다 쓰인다. 띄어쓰기 때문에 검사가 새면 안 된다.
    # 품목명이 '품목표에'와 '올린' 사이에 끼는 어법이 있다 ("품목표에 스탠드를
    # 올려 둔 곳은 12개 시군구"). 끼어 있으면 검사기가 통째로 못 봤다 (docs/55)
    ("등재수", re.compile(r"품목(?:표|)에 (?:[가-힣A-Za-z]{1,12}(?:을|를)\s*)?(?:이름 )?"
                        r"올(?:린|려\s?둔) (?:곳은 )?\*{0,2}(\d+)"), "regions"),
    ("등재수", re.compile(r"\*{0,2}(\d+)\s*개 시군구가 [가-힣]{1,6}(?:을|를)\s*대형폐기물"), "regions"),
    # 조사가 '은'만 있는 게 아니다 - '중앙값이 4,000원'도 같은 주장이다.
    ("중앙값", re.compile(r"(?:중앙값|가운데값)(?:은|이|)\s*\*{0,2}([\d,]+)\s*원?"), "median"),
    # 중앙값만 맞고 범위가 틀린 문장이 있었다(프린터 "0원부터 최대 10,000원").
    ("최저", re.compile(r"낮은 곳은\s*\*{0,2}([\d,]+)\s*원"), "min"),
    ("최고", re.compile(r"높은 곳은\s*\*{0,2}([\d,]+)\s*원"), "max"),
    ("최고", re.compile(r"최대\s*\*{0,2}([\d,]+)\s*원"), "max"),
    ("범위최저", re.compile(r"범위는\s*\*{0,2}([\d,]+)\?~"), "min"),
    ("범위최고", re.compile(r"범위는\s*\*{0,2}[\d,]+\?~\s*([\d,]+)\s*원"), "max"),
    # 과금 방식 표의 중앙값. 2026-09-07 양주시 품목표 축소 때 '곳' 수는 잡히고
    # 같은 줄의 중앙값(돗자리 2,500 -> 2,750, 러그 5,000 -> 5,250)은 새어 나갔다.
    ("표중앙값", re.compile(r"\|\s*통짜 한 건\s*\|\s*\*{0,2}\d+곳\*{0,2}\s*\|\s*\*{0,2}([\d,]+)\s*원"), "median"),
    ("표중앙값", re.compile(r"\|\s*(?:면적|길이|무게) 단위\s*\|\s*\*{0,2}\d+곳\*{0,2}\s*\|\s*\*{0,2}1(?:㎡|m|kg)당 ([\d,]+)\s*원"), "median"),
]


def main():
    fees = json.load(io.open(FEES, encoding="utf-8"))
    names = {i["slug"]: i["name"]
             for i in json.load(io.open(ITEMS, encoding="utf-8"))}

    checked = 0
    bad = []
    for path in sorted(glob.glob(CONTENT)):
        slug = os.path.basename(path)[:-3]
        body = re.sub(r"[ \t]*\n[ \t]*", " ", io.open(path, encoding="utf-8").read())
        blocks = [v for v in (fees.get(slug) or {}).values() if isinstance(v, dict)]
        for label, pat, field in CLAIMS:
            allowed = {b[field] for b in blocks}
            if field == "regions":
                allowed.add(TOTAL_REGIONS)
            for m in pat.finditer(body):
                checked += 1
                val = int(m.group(1).replace(",", ""))
                if val not in allowed:
                    bad.append((slug, names.get(slug, ""), label, val, sorted(allowed)))

    for slug, name, label, val, allowed in bad:
        print("%-14s %-6s %s %s -> fees.json %s"
              % (slug, name, label, format(val, ","), allowed))
    print("\n수수료 수치 %d건 검사, 어긋남 %d건" % (checked, len(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
