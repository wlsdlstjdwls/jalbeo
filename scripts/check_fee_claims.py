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

# 수수료표를 수집한 시군구 총수. "47개 시군구 가운데 8곳" 같은 문장의 앞 숫자다.
TOTAL_REGIONS = 47

# (라벨, 정규식, fees.json에서 비교할 필드)
CLAIMS = [
    ("지역수", re.compile(r"(\d+)\s*개?\s*시군구 품목표"), "regions"),
    ("등재수", re.compile(r"품목(?:표|)에 (?:이름 )?올(?:린|려둔) (?:곳은 )?\*{0,2}(\d+)"), "regions"),
    ("등재수", re.compile(r"\*{0,2}(\d+)\s*개 시군구가 [가-힣]{1,6}(?:을|를)\s*대형폐기물"), "regions"),
    ("중앙값", re.compile(r"(?:중앙값|가운데값)(?:은|)\s*\*{0,2}([\d,]+)\s*원?"), "median"),
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
