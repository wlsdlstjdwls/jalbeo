# -*- coding: utf-8 -*-
"""분리배출 Q&A 1,330건에서 품목 씨앗을 캔다.

입력: data/raw/bunri-qna.json  (crawl_bunri_qna.py)
출력: data/keywords/candidates-qna.csv

품목사전은 운영자가 답을 정해 둔 목록이고 이 게시판은 **답을 못 찾아서 물은
목록**이다. 그래서 거르는 방식이 다르다.

  1. 절차 질문은 품목 축이 아니다. "수거까지 며칠", "접수 취소"는 가이드 축이라
     여기서 뺀다 (판단 10). 남는 것만 품목 후보다.
  2. 제목에 현재 어휘(발행명, 별칭, 시드) 중 하나가 **부분문자열로** 걸리면
     '기존 커버'로 민다. '겔아이스팩'은 아이스팩 페이지가 받는다.
     너그럽게 걸러 두고 판단 40번(첫 문단이 이 질문인가)은 사람이 본다.
  3. 조회수는 같이 내되 자르는 데 쓰지 않는다 (판단 16).

    python scripts/extract_qna_seeds.py
"""
import csv
import io
import json
import os
import re
import sys
import importlib.util
from collections import defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data", "raw", "bunri-qna.json")
OUT = os.path.join(ROOT, "data", "keywords", "candidates-qna.csv")

# 품목이 아니라 절차를 묻는 제목. 가이드 축으로 넘긴다 (판단 10)
PROCEDURE = re.compile(
    r"수거(까지|일|날짜|시간|기사|업체|신청|문의|비용|안내)|접수|취소|환불|결제|"
    r"스티커\s*(구매|발급|재발급)|며칠|언제|예약|배출\s*장소|어디에?\s*(버|내)|"
    r"신고\s*(방법|취소)|앱|어플|홈페이지|사이트|아이디|비밀번호|회원|로그인|"
    r"과태료|벌금|민원|담당자|전화|연락")

# 제목 꼬리의 상투어. 이걸 떼면 품목이 남는다.
#
# 조사만 떼는 규칙은 쓰면 안 된다. '뽁뽁이', '파쇄종이', '꼬치'처럼 품목 이름이
# 조사와 같은 글자로 끝나서 '뽁뽁', '파쇄종'이 된다. 그래서 각 패턴은 **진짜
# 꼬리말 하나를 반드시 포함**하고, 조사는 그 앞에 붙어 있을 때만 같이 뗀다.
JOSA = r"(?:은|는|이|가|을|를|의|도|만|와|과|랑|이랑|에|에서|이나|나)?\s*"
ASK = r"(?:\s*(?:드립니다|드려요|드립니당|합니다|해요|해주세요|주세요|합니까|"
ASK += r"하나요|한가요|되나요|될까요|인가요|일까요|있나요|있을까요|하는지|"
ASK += r"해야하나요|해야되나요|좀요|좀|나요|가요|까요|여|요))?"

TAIL_PATTERNS = [
    JOSA + r"(?:어떻게|어디에|어디로|어디다|어느|무슨|뭐로|어떡)\s*.*",
    JOSA + r"(?:분리\s*)?(?:배출|수거)\s*(?:방법|법|방식|문의|질문|안내|요령|기준)?" + ASK,
    JOSA + r"(?:폐기|처리|처분)(?:하는|한|할|하)?\s*(?:방법|법|방식|문의|질문)?" + ASK,
    JOSA + r"버리(?:는|나|시|면|기)?\s*(?:법|방법)?" + ASK,
    JOSA + r"버려(?:야|서|요)?\s*(?:하는지|되는지)?" + ASK,
    JOSA + r"재활용\s*(?:여부|가능)?" + ASK,
    JOSA + r"(?:방법|방식|문의|질문|요령|기준|여부)" + ASK,
    JOSA + r"(?:궁금|여쭤|여쭙|알려)\s*\S*" + ASK,
    r"\s*(?:관련|에\s*대해|에\s*대하여|좀\s*알려주세요)$",
]
TAIL_RE = [re.compile(p + r"\s*[?!.~,]*$") for p in TAIL_PATTERNS]

DROP_WORDS = ("기타", "그외", "그 외", "일체", "해당", "품목", "문의", "질문",
              "생활폐기물", "재활용", "분리배출", "분리수거", "쓰레기")


def norm(s):
    return re.sub(r"\s+", "", (s or "")).lower()


def load_vocab():
    path = os.path.join(ROOT, "scripts", "extract_external_seeds.py")
    spec = importlib.util.spec_from_file_location("ex", path)
    mod = importlib.util.module_from_spec(spec)
    cwd = os.getcwd()
    os.chdir(ROOT)
    try:
        spec.loader.exec_module(mod)
        return mod.known_vocabulary()
    finally:
        os.chdir(cwd)


def head_noun(title):
    """제목에서 상투어를 떼고 품목 머리말을 남긴다."""
    t = re.sub(r"[\"'\[\]()（）]", " ", title)
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"^(?:저희|우리|제가|저는|혹시|그럼|그리고)\s+", "", t)
    for _ in range(4):                       # 꼬리가 겹쳐 붙는다
        before = t
        for rx in TAIL_RE:
            cut = rx.sub("", t).strip(" ,.-")
            if cut and cut != t:
                t = cut
        if t == before:
            break
    return t.strip(" ,.-")


def main():
    rows = json.load(io.open(SRC, encoding="utf-8"))
    vocab = load_vocab()
    # 부분문자열 대조용. 한 글자짜리는 아무 데나 걸려서 뺀다
    vocab_terms = sorted((k for k in vocab if len(k) >= 2), key=len, reverse=True)

    groups = defaultdict(lambda: {"n": 0, "views": 0, "cls": set(), "titles": []})
    n_proc = 0
    for r in rows:
        title = r["title"]
        if PROCEDURE.search(title):
            n_proc += 1
            continue
        name = head_noun(title)
        if not name or len(name) < 2 or not re.search(r"[가-힣]", name):
            continue
        if any(w == name for w in DROP_WORDS):
            continue
        key = norm(name)
        g = groups[key]
        g["n"] += 1
        g["views"] += r["views"]
        if r["cls"]:
            g["cls"].add(r["cls"])
        if len(g["titles"]) < 3:
            g["titles"].append(title)
        g.setdefault("name", name)

    out = []
    for key, g in groups.items():
        hit = next((t for t in vocab_terms if t in key), None)
        out.append({
            "item": g["name"],
            "n": g["n"],
            "views": g["views"],
            "cls": " / ".join(sorted(g["cls"]))[:60],
            "covered_by": vocab[hit] if hit else "",
            "decision": "기존 커버" if hit else "",
            "note": " | ".join(g["titles"])[:160],
        })
    out.sort(key=lambda r: (r["decision"] != "", -r["views"], r["item"]))

    with io.open(OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["item", "n", "views", "cls",
                                           "covered_by", "decision", "note"])
        w.writeheader()
        w.writerows(out)

    new = [r for r in out if not r["decision"]]
    print("질문 %d건 / 절차 질문 %d건 제외 / 머리말 %d개"
          % (len(rows), n_proc, len(out)))
    print("기존 어휘에 없는 것 %d개 -> %s" % (len(new), OUT))
    print("\n조회수 상위 40개 (자르는 데 쓰지 않는다, 판단 16):")
    for r in new[:40]:
        print("  %5d회 %2d건  %-22s %s" % (r["views"], r["n"], r["item"][:22],
                                          r["cls"][:34]))


if __name__ == "__main__":
    main()
