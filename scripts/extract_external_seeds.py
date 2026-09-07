"""자동완성 고리 밖에서 품목 씨앗을 캔다.

판단 13(씨앗은 발행분에서 뽑는다)은 닫힌 고리다. 이미 가진 것의 이웃만
나오고, 처음부터 생각 못 한 물건은 영영 안 나온다. 여기서는 우리 페이지를
전혀 참조하지 않는 두 출처에서 품목명을 캔다.

  - data/processed/fees.csv        지자체 대형폐기물 수수료표 (47개 시군구)
  - data/raw/blisgo-items.json     경쟁 사이트 품목 목록 (재활용 축)

산출은 후보 목록일 뿐이다. 시군구 등재 수는 자동완성 빈도와 같은 성질의
대리지표라 판단 16에 걸린다 - 자르는 건 실측이 한다.
"""
import csv
import io
import json
import re
import sys
from collections import Counter, defaultdict

ROOT = "."
FEES = f"{ROOT}/data/processed/fees.csv"
BLISGO = f"{ROOT}/data/raw/blisgo-items.json"
ITEMS = f"{ROOT}/site/src/data/items.json"
OUT = f"{ROOT}/data/keywords/candidates-external.csv"

# 품목명이 아니라 표기 쓰레기인 것들
NOISE = re.compile(r"^(\d+|[a-zA-Z]{1,2}|.{1})$")
DROP_WORDS = ("기타", "그외", "그 외", "이외", "일체", "해당", "품목", "제품류")


def norm(s: str) -> str:
    return re.sub(r"\s+", "", (s or "")).lower()


def clean(raw: str) -> str:
    """'판유리)', '(김치)냉장고'처럼 짝 잃은 괄호를 떼어 낸다."""
    out = re.sub(r"[()\[\]]", " ", raw)
    return re.sub(r"\s+", " ", out).strip()


def split_variants(raw: str):
    """'수족관(어항)', 'CD, DVD'처럼 한 칸에 둘이 든 표기를 가른다."""
    out = []
    for part in re.split(r"[,/]", raw):
        part = part.strip()
        if not part:
            continue
        m = re.match(r"^(.*?)\s*[(\[]([^)\]]+)[)\]]\s*$", part)
        if m:
            head, inner = m.group(1).strip(), m.group(2).strip()
            # 괄호 안이 규격이면 버리고, 다른 이름이면 둘 다 쓴다
            if re.search(r"\d|이상|이하|미만|cm|m|kg|인용|형|용량", inner):
                out.append(head)
            else:
                out.extend([head, inner])
        else:
            out.append(part)
    return [c for c in (clean(o) for o in out) if c]


def is_noise(name: str) -> bool:
    if NOISE.match(name.strip()):
        return True
    if any(w in name for w in DROP_WORDS):
        return True
    if not re.search(r"[가-힣]", name):
        return True
    return False


CHO = list("ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ")
JUNG = list("ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ")
JONG = ["", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ", "ㄻ", "ㄼ", "ㄽ",
        "ㄾ", "ㄿ", "ㅀ", "ㅁ", "ㅂ", "ㅄ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅊ", "ㅋ",
        "ㅌ", "ㅍ", "ㅎ"]
HANGUL_BASE, HANGUL_LAST = 0xAC00, 0xD7A3
CHO_SPAN, JUNG_SPAN = 588, 28

# 수수료표가 붙여 두는 군더더기. 떼서 아는 말이 되면 새 품목이 아니다.
AFFIX_PREFIX = ("폐",)
AFFIX_SUFFIX = ("류", "기기", "세트", "제품")


def jamo(text: str) -> str:
    """site/src/lib/search.ts의 jamo와 같은 규칙이다. 한쪽을 고치면 같이 고친다."""
    out = []
    for ch in text:
        code = ord(ch)
        if HANGUL_BASE <= code <= HANGUL_LAST:
            at = code - HANGUL_BASE
            out.append(CHO[at // CHO_SPAN])
            out.append(JUNG[(at % CHO_SPAN) // JUNG_SPAN])
            out.append(JONG[at % JUNG_SPAN])
        elif ch != " ":
            out.append(ch)
    return "".join(out)


# 표기 이형태로 실제 갈리는 자모쌍. 편집거리 대신 이 집합만 접는다.
#
# 검색(site/src/lib/search.ts)은 자모 편집거리를 쓰지만 판단 33대로
# 부분일치가 0건일 때만 돈다. 씨앗 접기에는 그 관문이 없어서 무조건 돌고,
# 그러면 테이블이 케이블로, 키보드가 킥보드로, 헤어드라이어가
# 에어프라이어로 접힌다. 신규 품목이 오타 취급으로 사라지는 쪽이
# 목록에 이형태가 하나 더 남는 쪽보다 훨씬 비싸다.
CONFUSABLE = [
    "ㄱㅋㄲ", "ㄷㅌㄸ", "ㅂㅍㅃ", "ㅅㅆ", "ㅈㅊㅉ",   # 조음위치가 같은 자음
    "ㅐㅔ", "ㅒㅖ", "ㅕㅓ", "ㅗㅜ", "ㅘㅚ",           # 흔히 헷갈려 적는 모음
]
CONFUSE_SET = {
    (a, b) for group in CONFUSABLE for a in group for b in group if a != b
}


def is_spelling_variant(a: str, b: str) -> bool:
    """자모 길이가 같고 어긋난 자리가 하나뿐이며 그 쌍이 혼동쌍일 때만 참."""
    if len(a) != len(b) or a == b:
        return False
    diff = [(x, y) for x, y in zip(a, b) if x != y]
    return len(diff) == 1 and diff[0] in CONFUSE_SET


def strip_affix(name: str):
    """'폐소화기' -> '소화기', '목재류' -> '목재'."""
    out = []
    for pre in AFFIX_PREFIX:
        if name.startswith(pre) and len(name) > len(pre) + 1:
            out.append(name[len(pre):])
    for suf in AFFIX_SUFFIX:
        if name.endswith(suf) and len(name) > len(suf) + 1:
            out.append(name[: -len(suf)])
    return out


def folds_into(name: str, targets: dict):
    """아는 말의 표기 이형태면 그 말을 돌려준다. 씽크대 -> 싱크대.

    수수료표는 47개 시군구가 제각각 적은 것이라 같은 물건이 캐비닛,
    화일캐비닛, 파일캐비닛으로 흩어져 있다. 표기 차이를 신규 품목으로
    세면 실측 묶음이 오타로 찬다.
    """
    for cand in [name] + strip_affix(name):
        key = norm(cand)
        if key in targets:
            return targets[key]
    jm = jamo(norm(name))
    for tkey, tname in targets.items():
        if is_spelling_variant(jm, jamo(tkey)):
            return tname
    return None


def known_vocabulary():
    """발행명, 별칭, 이미 판정된 후보, 손으로 고른 시드까지 전부."""
    vocab = {}
    items = json.load(io.open(ITEMS, encoding="utf-8"))
    if isinstance(items, dict):
        items = items.get("items", [])
    for it in items:
        vocab[norm(it.get("name"))] = it.get("name")
        for a in it.get("aliases") or []:
            vocab.setdefault(norm(a), f"{a} (별칭 -> {it.get('name')})")
    for fname in ("candidates-r2-triage.csv", "candidates-r3-triage.csv"):
        for r in csv.DictReader(
            io.open(f"{ROOT}/data/keywords/{fname}", encoding="utf-8-sig")
        ):
            vocab.setdefault(norm(r["item"]), f"{r['item']} (판정 {r['decision']})")
    for r in csv.DictReader(io.open(f"{ROOT}/data/keywords/items.csv", encoding="utf-8-sig")):
        vocab.setdefault(norm(r["item"]), f"{r['item']} (시드)")
    return vocab


def collect_fees():
    """품목명 -> 등재 시군구 집합. 행 수가 아니라 시군구 수를 센다 (판단 19)."""
    hits = defaultdict(set)
    for r in csv.DictReader(io.open(FEES, encoding="utf-8-sig")):
        region = f"{r['sido']} {r['sigungu']}"
        for name in split_variants(r["item"] or ""):
            hits[name].add(region)
    return hits


def collect_blisgo():
    raw = json.load(io.open(BLISGO, encoding="utf-8"))
    names = Counter()
    for entry in raw:
        for name in split_variants(entry):
            names[name] += 1
    return names


def main():
    vocab = known_vocabulary()
    fees = collect_fees()
    blisgo = collect_blisgo()

    rows = {}
    folded = []

    def take(name, n_sigungu, from_blisgo):
        if is_noise(name):
            return
        hit = folds_into(name, vocab)
        if hit:
            folded.append((name, hit))
            return
        key = norm(name)
        if key in rows:
            rows[key]["n_sigungu"] = max(rows[key]["n_sigungu"], n_sigungu)
            if from_blisgo:
                rows[key]["in_blisgo"] = 1
                rows[key]["source"] = "fees+blisgo"
            return
        rows[key] = {
            "item": name,
            "source": "blisgo" if from_blisgo else "fees",
            "n_sigungu": n_sigungu,
            "in_blisgo": 1 if from_blisgo else 0,
            "variants": "",
        }

    # 등재 시군구가 많은 쪽을 먼저 넣어야 표기 이형태의 대표가 흔한 표기로 잡힌다
    for name, regions in sorted(fees.items(), key=lambda kv: -len(kv[1])):
        take(name, len(regions), False)
    for name in blisgo:
        take(name, 0, True)

    # 후보끼리도 접는다. 캐비넷과 캐비닛이 나란히 실측 묶음에 오르면 안 된다
    heads = {}
    for key, r in sorted(rows.items(), key=lambda kv: -kv[1]["n_sigungu"]):
        hit = folds_into(r["item"], heads)
        if hit:
            head = rows[norm(hit)]
            head["variants"] = ", ".join(
                x for x in [head["variants"], r["item"]] if x
            )
            head["n_sigungu"] = max(head["n_sigungu"], r["n_sigungu"])
            head["in_blisgo"] = max(head["in_blisgo"], r["in_blisgo"])
            folded.append((r["item"], f"{hit} (후보 대표)"))
            del rows[key]
        else:
            heads[key] = r["item"]

    out = sorted(
        rows.values(), key=lambda r: (-r["n_sigungu"], -r["in_blisgo"], r["item"])
    )
    with io.open(OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(
            fh,
            fieldnames=[
                "item", "source", "n_sigungu", "in_blisgo", "variants",
                "decision", "note",
            ],
        )
        w.writeheader()
        for r in out:
            r.setdefault("decision", "")
            r.setdefault("note", "")
            w.writerow(r)

    by_src = Counter(r["source"] for r in out)
    print(f"기존 어휘 {len(vocab)}개, 접힌 표기 {len(folded)}건")
    print(f"신규 후보 {len(out)}개 -> {OUT}")
    print("출처별:", dict(by_src))
    print("\n시군구 20곳 이상 등재:")
    for r in out:
        if r["n_sigungu"] >= 20:
            print(f"  {r['n_sigungu']:3d}곳  {r['item']}")


if __name__ == "__main__":
    sys.exit(main())
