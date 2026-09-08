# -*- coding: utf-8 -*-
"""품목별 수수료 통계 생성. 페이지의 '비용' 섹션에 주입할 데이터.

입력: data/processed/fees.csv, site/src/data/items.json
출력: site/src/data/fees.json

지자체마다 금액이 몇 배씩 다르므로 단일 값을 못 박지 않는다. 중앙값과
사분위 범위, 표본 지역 수를 함께 낸다. 근거로 쓸 지역별 샘플도 남긴다.
"""
import csv
import io
import json
import os
import re
import statistics
import sys
from collections import defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEES = os.path.join(ROOT, "data", "processed", "fees.csv")
ITEMS = os.path.join(ROOT, "site", "src", "data", "items.json")
OUT = os.path.join(ROOT, "site", "src", "data", "fees.json")

# 원본 표기가 우리 품목명과 다른 경우. 왼쪽이 원본 토큰, 오른쪽이 우리 slug.
EXTRA_ALIAS = {
    "카펫": "reogeu", "카페트": "reogeu", "카펫트": "reogeu",
    "전기밥솥": "bapsot", "압력밥솥": "bapsot",
    "전기레인지": "gaseureinji", "가스렌지": "gaseureinji",
    "디지털피아노": "jeonjapiano", "전자올겐": "jeonjapiano",
    "장농": "jangrong",
    "헬맷": "helmet",
    # 별칭이지만 수수료 축이 다른 것. 식기세척기는 4,000~14,000, 건조기는 0~2,000이라
    # 한 중앙값에 섞으면 건조기 페이지가 세척기 요금표를 보여 준다 (판단 39).
    "식기세척기": None, "팩스": None, "팩시밀리": None, "팩스기": None, "팩스기기": None,   # 하남시 표기. 오타는 별칭이 아니라 여기서 접는다 (판단 33, 36)
    "진공청소기": "cheongsogi",
    "봉제인형": "inhyeong",
    "화장다이": "hwajangdae", "경대": "hwajangdae",
    "서랍": "seorapjang", "수납장": "seorapjang",
    "건조대": "ppalraegeonjodae", "빨래걸이": "ppalraegeonjodae",
    "자토바이": None,   # 자전거 오탐 방지용 자리표시
    # 스피커 페이지 별칭. 오디오(전축)는 세트라 값이 스피커 낱개의 두 배 가까이 된다.
    # 섞으면 스피커 중앙값이 2,000에서 3,500으로 뛴다 (docs/39, 판단 39).
    "오디오": None, "전축": None, "오디오세트": None, "앰프": None,
    # 박스 페이지(골판지)는 수수료 축이 없다. 접미 일치가 아이스박스, 콘솔박스,
    # 공간박스를 끌어온다 (docs/39).
    "박스": None, "상자": None, "택배박스": None, "택배상자": None, "종이박스": None,
    "종이상자": None, "골판지": None, "골판지상자": None, "라면박스": None,
    "피자박스": None, "치킨박스": None,
    # 대형폐기물 품목표의 '조명', '형광등'은 램프가 아니라 등기구다. 램프는
    # 형광등 수거함으로 가는 물건이라 애초에 대형폐기물 신고 대상이 아니다.
    # 그래서 형광등 페이지가 아니라 LED등(등기구) 페이지로 보낸다.
    "조명기구": "leddeung", "조명": "leddeung", "전등": "leddeung",
    "형광등": "leddeung", "led등": "leddeung", "전등틀": "leddeung",
    # 토스트기는 에어프라이어 별칭인데 수수료표에 따로 오른 곳(1,000~2,000)이
    # 에어프라이어 중앙값을 3,000에서 2,750으로 끌어내린다 (docs/40, 판단 42).
    "토스트기": None, "토스터": None, "토스터기": None, "토스트 기계": None,
    # 신발 페이지 별칭 '인라인스케이트'. 신발은 6곳(중앙값 3,000)인데 인라인이
    # 6곳(중앙값 2,000)을 더 얹는다. 훈령이 같은 줄에 적은 물건이라 별칭이지만
    # 과금은 신발이 아니라 스포츠용품 쪽에 붙는다 (docs/45, 판단 42).
    "인라인스케이트": None, "인라인": None, "롤러스케이트": None, "스케이트": None,
    # 바이올린 페이지 별칭 '악기'는 양천구 '악기류'(피아노 15,000 포함)를 통째로
    # 끌어와 지역값이 4,500이 된다. 악기 통계는 안 모으고 본문이 지역별로 적는다.
    "악기": None, "현악기": None, "기타 악기": None, "바이올린 케이스": None,
    "첼로": None, "통기타": None, "우쿨렐레": None, "비올라": None,
    # 크리스마스트리 페이지 별칭 '트리'. 강북구 '인조나무/트리/화환'은 조화가
    # '화환'으로 이미 받는 행이고, 높이 50cm'마다' 1,000원이라 통짜 값도 아니다.
    # 크리스마스트리 자체 행 4곳만 남긴다 (docs/46, 판단 24, 47).
    "트리": None, "인조나무": None,
}

# 과금 단위. 통짜 한 개에 얼마가 아니라 '단위 얼마'로 매기는 품목이 있다.
# 장롱은 1쪽당, 카펫은 3.3㎡당, 장판은 5m당, 깨진 유리는 kg당이다.
# 단위가 다른 값을 같은 중앙값에 섞으면 배수만큼 틀린다 (docs/12).
#
# '이상', '미만'이 붙은 규격 구간과 구별해야 한다. 냉장고 '300ℓ 이상'은
# 크기 구간이지 과금 단위가 아니다. 그래서 '당'이 붙은 표기만 단위로 본다.
UNIT_RE = re.compile(r"(1?\s*쪽\s*당|\(?1\s*쪽\)?|쪽당|1\s*짝|짝문|당\s*1쪽"
                     r"|짝당|폭당|칸당|한\s*짝당"
                     # 강북구는 '당' 대신 '마다'로 적는다 ('서랍장 1단마다',
                     # '인덕션 류 1구 마다'). 같은 뜻이다 (docs/46, 판단 24)
                     r"|단\s*마다|칸\s*마다|쪽\s*마다|구\s*마다)")

# 마대, 자루, 포대, 묶음처럼 담는 그릇을 세는 표기. 그릇 자체는 규격이 없지만
# 지자체가 그릇 크기를 ℓ이나 kg으로 적어 둔다 ('100ℓ 자루당', '20㎏마대기준').
# 적어 둔 그 규격이 곧 환산 기준이다 (docs/29).
SACK = r"(?:마대|자루|포대|봉투|묶음|박스)"
# '당', '기준', '1개당'처럼 단위임을 알리는 꼬리. 이게 없으면 규격 구간이다.
TAIL = r"(?:\s*(?:자루|마대|포대|봉투|묶음)?\s*(?:1\s*개)?\s*(?:당|기준|마다))"

# (단위 이름, 기준 단위, 수량+단위 정규식, 기준 단위 환산 계수)
# 수량이 안 적힌 'kg당', '㎡당'은 1로 본다.
# '당', '기준' 말고 '마다'로 적는 지자체가 있다. 강북구 품목표 55행이 전부
# 그렇고("가장 긴 면이 50cm마다 1,000원"), '마다'를 못 읽으면 그 값이 통짜
# 요금으로 들어가 강북구가 어느 품목에서나 최저가가 된다 (docs/46, 판단 24).
UNIT_TAIL = r"(?:당|기준|마다)"

MEASURED = [
    # 무게. 'kg당' 말고 '20㎏마대기준', 'PP포대 당(25킬로그램)'도 같은 뜻이다.
    ("weight", "kg", re.compile(
        r"(\d+(?:\.\d+)?)?\s*(kg|㎏|킬로그램|킬로|톤|t)\s*(?:%s)?\s*%s"
        % (SACK, UNIT_TAIL), re.I), {"톤": 1000, "t": 1000}),
    # '1㎡초과 시 마다'(대덕구), '1제곱미터초과시마다'(서구)도 같은 뜻이다.
    ("area", "㎡", re.compile(r"(\d+(?:\.\d+)?)?\s*(㎡|m2|제곱미터|평)"
                             r"\s*(?:초과\s*시)?\s*(?:\([^)]*\))?\s*%s"
                             % UNIT_TAIL, re.I), {"평": 3.3}),
    ("length", "m", re.compile(r"(\d+(?:\.\d+)?)?\s*(m|미터|cm|㎝)\s*%s"
                              % UNIT_TAIL, re.I), {"cm": 0.01, "㎝": 0.01}),
    # 부피. '100ℓ 자루당', '100리터 봉투기준', '20ℓ당'. 기준 단위는 1ℓ다.
    # 냉장고 '500ℓ 이상'은 꼬리가 없어서 여기 안 걸린다 (확정 판단 24번).
    ("volume", "ℓ", re.compile(r"(\d+(?:\.\d+)?)\s*(ℓ|l|리터|L)%s" % TAIL), {}),
    # 세제곱미터는 리터로 환산하지 않는다. 수족관 '1㎥당 6,000원'을 ℓ로 펴면
    # '1ℓ당 6원'이 되어 화면이 못 읽을 숫자가 된다. 단위를 따로 둔다 (docs/46).
    ("volume_m3", "㎥", re.compile(r"(\d+(?:\.\d+)?)?\s*(㎥|m3|세제곱미터)"
                                  r"\s*(?:이상)?\s*(?:\([^)]*\))?\s*%s"
                                  % UNIT_TAIL, re.I), {}),
]


def unit_of(item, spec):
    """과금 단위와 기준 단위 환산 계수를 돌려준다.

    ('area', 3.3) 이면 그 행의 금액은 3.3㎡ 값이라는 뜻이다. 금액을
    3.3으로 나눠야 다른 지자체의 1㎡당 값과 같은 자리에 놓인다.
    """
    s = item + " " + spec
    if UNIT_RE.search(s):
        return "panel", 1.0
    for name, _base, pat, scale in MEASURED:
        m = pat.search(s)
        if not m:
            continue
        qty = float(m.group(1)) if m.group(1) else 1.0
        qty *= scale.get(m.group(2).lower(), scale.get(m.group(2), 1))
        if qty <= 0:
            continue
        return name, qty
    return "whole", 1.0


# 화면과 본문에서 쓰는 단위 이름.
UNIT_LABEL = {"whole": "전후", "panel": "1쪽당", "area": "1㎡당",
              "length": "1m당", "weight": "1kg당", "volume": "1ℓ당",
              "volume_m3": "1㎥당"}


SPLIT = re.compile(r"[,/·]|및|그리고")
PAREN = re.compile(r"[()（）\[\]]")


def tokens(item):
    """'장롱(옷장)', '비디오, 청소기, 선풍기' 같은 표기를 낱개로 쪼갠다."""
    s = PAREN.sub(",", item)
    out = []
    for t in SPLIT.split(s):
        t = re.sub(r"\s+", "", t).strip(".·-")
        if not t:
            continue
        out.append(t)
        # '피아노류'·'카펫트류'처럼 묶음 접미가 붙은 표기도 같은 품목으로 본다.
        if len(t) > 2 and t.endswith("류"):
            out.append(t[:-1])
    return out


def build_matcher(items):
    """토큰 → slug. 긴 이름을 먼저 보게 해서 전자피아노가 피아노로 새지 않게 한다."""
    table = {}
    for it in items:
        names = [it["name"]] + (it.get("aliases") or [])
        for n in names:
            table[re.sub(r"\s+", "", n)] = it["slug"]
    for k, v in EXTRA_ALIAS.items():
        if v:
            table[k] = v
        else:
            # None은 '이 표기는 수수료를 안 모은다'는 뜻이다. items의 별칭에서 들어온
            # 같은 표기를 지워야 막힌다 (docs/36 판단 42, docs/39 스피커/박스)
            table.pop(k, None)
    return table, sorted(table, key=len, reverse=True)


def match(token, table, order):
    if token in table:
        return table[token]
    # '전기밥솥'처럼 수식어가 붙은 표기는 접미 일치로 받는다. 긴 후보가 우선이다.
    for name in order:
        if len(token) > len(name) and token.endswith(name):
            return table[name]
    return None


def summarize(per_region):
    """지역별 대표값 목록에서 통계를 낸다. 표본이 3곳 미만이면 버린다."""
    vals = sorted(per_region.values())
    if len(vals) < 3:
        return None
    cheapest = min(per_region.items(), key=lambda kv: kv[1])
    dearest = max(per_region.items(), key=lambda kv: kv[1])
    return {
        "median": int(statistics.median(vals)),
        "min": vals[0],
        "max": vals[-1],
        "q1": vals[len(vals) // 4],
        "q3": vals[(len(vals) * 3) // 4],
        "regions": len(vals),
        "cheapest": {"region": cheapest[0], "fee": cheapest[1]},
        "dearest": {"region": dearest[0], "fee": dearest[1]},
        "by_region": dict(sorted(per_region.items(), key=lambda kv: kv[1])),
    }


def main():
    items = json.load(io.open(ITEMS, encoding="utf-8"))
    rows = list(csv.DictReader(io.open(FEES, encoding="utf-8")))
    table, order = build_matcher(items)

    # slug → 과금단위 → 지역 → 금액들
    buckets = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    base_dates = defaultdict(list)
    for r in rows:
        fee = int(r["fee"])
        if fee <= 0:
            continue
        unit, qty = unit_of(r["item"], r["spec"])
        if qty != 1.0:
            fee = int(round(fee / qty))
            if fee <= 0:
                continue
        region = (r["sido"] + " " + r["sigungu"]).strip()
        seen = set()
        for tok in tokens(r["item"]):
            slug = match(tok, table, order)
            if slug and slug not in seen:
                seen.add(slug)
                buckets[slug][unit][region].append(fee)
                if r["base_date"]:
                    base_dates[slug].append(r["base_date"])

    out = {}
    for slug, by_unit in buckets.items():
        stats = {}
        for unit, regions in by_unit.items():
            per_region = {k: int(statistics.median(sorted(v))) for k, v in regions.items()}
            st = summarize(per_region)
            if st:
                stats[unit] = st
        if not stats:
            continue
        # 어느 단위가 다수인지. 쪽당이 다수면 화면에서 그걸 먼저 말해야 한다.
        # 같은 지역 수면 통짜를 앞에 둔다. 읽는 사람이 기대하는 쪽이다.
        order = ["whole", "panel", "area", "length", "weight", "volume",
                 "volume_m3"]
        primary = max(order, key=lambda u: (stats.get(u, {}).get("regions", 0),
                                            -order.index(u)))
        entry = {
            "primary": primary,
            "base_date": max(base_dates[slug]) if base_dates[slug] else "",
        }
        for unit in order:
            if unit in stats:
                entry[unit] = stats[unit]
        out[slug] = entry

    # 키 순서는 CSV를 훑은 순서라 품목이 하나만 늘어도 전체가 밀린다.
    # 값이 그대로인데 파일 전체가 diff로 잡히면 뭐가 바뀌었는지 안 보인다.
    io.open(OUT, "w", encoding="utf-8").write(
        json.dumps(dict(sorted(out.items())), ensure_ascii=False, indent=2) + "\n"
    )

    print("품목 %d개 집계" % len(out))
    for it in items:
        e = out.get(it["slug"])
        if not e:
            print("  %-8s  —" % it["name"])
            continue
        parts = []
        for unit in ("whole", "panel", "area", "length", "weight", "volume"):
            if unit in e:
                st = e[unit]
                parts.append("%s %s원(%d지역)"
                             % (UNIT_LABEL[unit], f"{st['median']:,}",
                                st["regions"]))
        star = ""
        if e["primary"] != "whole":
            star = " <-%s 우세" % UNIT_LABEL[e["primary"]]
        print("  %-8s %s%s" % (it["name"], " / ".join(parts), star))


if __name__ == "__main__":
    main()
