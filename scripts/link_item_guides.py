# -*- coding: utf-8 -*-
"""품목 페이지에서 가이드로 가는 링크(`relatedGuides`)를 붙인다.

`docs/29` 감사에서 나온 것이다. 167개 품목 중 49개가 스티커, 신고, 무상수거
절차를 저마다 다시 설명하면서 그 절차를 가진 가이드로는 한 곳도 잇지 않고
있었다(전체 품목에서 가이드로 나가는 링크가 1개뿐이었다). 절차를 페이지마다
다시 쓰면 확정 판단 5번(같은 답을 하는 페이지를 늘리지 않는다)에 걸린다.

붙이는 기준은 **그 페이지가 실제로 그 절차를 말하고 있을 때**다. 품목 분류가
아니라 본문 어휘로 고른다. 최대 2개까지만 붙인다 - 다섯 개를 다 붙이면
그게 다시 템플릿이다.

    python scripts/link_item_guides.py --dry    # 무엇이 붙는지만 본다
    python scripts/link_item_guides.py          # md 프런트매터에 쓴다
"""
import io
import os
import re
import sys
from collections import Counter

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEM_DIR = os.path.join(ROOT, "site", "src", "content", "items")

# (가이드 slug, 신호 정규식, 최소 히트 수)
# 순서가 우선순위다. 같은 점수면 앞의 것이 먼저 붙는다.
#
# 최소 히트 수를 둔 이유: 한 번 스치는 말은 그 절차를 '말하고 있는' 게 아니다.
# 유모차 페이지의 "의류수거함 대상 아닙니다"는 표 한 칸이라 헌옷 가이드로
# 넘길 이유가 없다. 반대로 스티커는 한 번만 나와도 그 절차를 쓰고 있는 것이다.
RULES = [
    # 무상수거는 신호가 뚜렷하다. 전화번호나 제도명이 본문에 있어야 한다.
    ("pyegajeon-musang-sugeo",
     re.compile(r"(무상방문수거|무상 방문 ?수거|1599-?0903|E-순환거버넌스)"), 1),
    # 헌옷 축. 스쳐 지나가는 한 번은 빼려고 두 번 이상을 건다.
    ("heonot-bangmun-sugeo",
     re.compile(r"(의류수거함|헌옷|고물상)"), 2),
    # 대형폐기물 절차. 스티커, 필증, 신고 절차를 말할 때.
    ("daehyeong-pyegimul-singo",
     re.compile(r"(스티커|납부필증|신고필증|대형폐기물로 신고|대형폐기물 신고)"), 1),
    # 가구 축. 재활용센터나 가구 무료수거를 말할 때.
    ("pyegagu-mulyo-sugeo",
     re.compile(r"(재활용센터|무료수거 업체|가구 무료|폐가구)"), 1),
    # 봉투 축. '종량제봉투에 넣으세요'는 거의 모든 페이지에 있어서 신호가 못
    # 된다. 숫자도 그것만으로는 안 된다 - 식용유의 '18L'은 통 용량이지 봉투가
    # 아니다. 숫자와 '봉투'가 같은 자리에 있거나 마대를 말할 때만 붙인다.
    ("jongryangje-bongtu",
     re.compile(r"(\d+\s*(리터|L\b|ℓ)[^.\n]{0,12}봉투|봉투[^.\n]{0,12}\d+\s*(리터|L\b|ℓ)"
                r"|특수마대|마대|봉투 규격)"), 1),
]
MAX_LINKS = 2


def split_md(text):
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("프런트매터가 없다")
    return parts[1], parts[2]


def reciprocal():
    """가이드가 `related`로 지목한 품목 -> 그 가이드. 편집자가 이미 고른 짝이다."""
    out = {}
    gdir = os.path.join(ROOT, "site", "src", "content", "guides")
    for fn in sorted(os.listdir(gdir)):
        if not fn.endswith(".md"):
            continue
        text = io.open(os.path.join(gdir, fn), encoding="utf-8").read()
        m = re.search(r"^related:\s*\[([^\]]*)\]", text, re.M)
        if not m:
            continue
        for slug in re.findall(r'"([^"]+)"', m.group(1)):
            out.setdefault(slug, []).append(fn[:-3])
    return out


def pick(body, forced):
    scored = []
    for i, (slug, pat, floor) in enumerate(RULES):
        n = len(pat.findall(body))
        if n >= floor:
            scored.append((-n, i, slug))
    scored.sort()
    # 가이드가 먼저 지목한 짝을 앞에 세운다. 나머지는 본문 신호 순.
    out = list(forced)
    for _, _, s in scored:
        if s not in out:
            out.append(s)
    return out[:MAX_LINKS]


def main():
    dry = "--dry" in sys.argv
    back = reciprocal()
    stat = Counter()
    changed = 0
    for fn in sorted(os.listdir(ITEM_DIR)):
        if not fn.endswith(".md"):
            continue
        path = os.path.join(ITEM_DIR, fn)
        text = io.open(path, encoding="utf-8").read()
        fm, body = split_md(text)
        guides = pick(body, back.get(fn[:-3], []))
        if not guides:
            stat["없음"] += 1
            continue
        for g in guides:
            stat[g] += 1
        line = "relatedGuides: [%s]" % ", ".join('"%s"' % g for g in guides)
        if re.search(r"^relatedGuides:.*$", fm, re.M):
            new_fm = re.sub(r"^relatedGuides:.*$", line, fm, count=1, flags=re.M)
        else:
            # related 바로 다음 줄에 둔다. 둘 다 '이어보기'라 붙어 있는 게 읽힌다.
            new_fm = re.sub(r"^(related:.*)$", r"\1\n" + line, fm, count=1, flags=re.M)
        if new_fm == fm:
            print("SKIP %s - related 줄을 못 찾았다" % fn)
            continue
        if not dry:
            io.open(path, "w", encoding="utf-8", newline="").write(
                "---" + new_fm + "---" + body)
        changed += 1
        if dry:
            print("%-24s %s" % (fn[:-3], ", ".join(guides)))

    print()
    print("품목 %d개에 링크%s" % (changed, "" if not dry else " (dry)"))
    for k, n in stat.most_common():
        print("  %-26s %d" % (k, n))


if __name__ == "__main__":
    main()
