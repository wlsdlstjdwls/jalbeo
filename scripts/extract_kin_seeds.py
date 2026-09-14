# -*- coding: utf-8 -*-
"""지식iN 검색 제목에서 품목 씨앗을 캔다.

입력: data/raw/kin-search.json  (crawl_naver_kin.py)
출력: data/keywords/candidates-kin.csv

`extract_qna_seeds.py`와 하는 일은 같은데 들어오는 말이 다르다. 분리배출
Q&A는 게시판 양식에 맞춰 "품목 + 배출방법 문의"로 오지만 지식iN은 사람이
말하듯 온다. "가발은 일반쓰레기인가요?", "귤 껍데기는 일반쓰레기인가요?
음식물 쓰레기인가요?" 처럼 **재질 판정 자체가 제목**이라 꼬리말을 더 떼야
머리말이 남는다.

여기서 새로 하는 것 둘.

  1. 상태 수식어를 머리말에서 갈라 `modifiers` 칸에 따로 담는다. "고장난
     우레탄 폼 캔", "곰팡이 핀 고양이 사료"에서 물건은 우레탄폼캔, 고양이
     사료다. 수식어를 붙인 채로 묶으면 같은 물건이 흩어진다. 그런데 수식어
     자체가 판단 38이 말하는 '답이 갈리는 자리'라서 버리지는 않는다.
  2. 조사 '이'에 먹힌 이름은 코퍼스가 되돌린다. 판단 51이 말한 자리인데
     여기서는 꼬리말을 반드시 포함해도 안 막힌다 - "떡볶이 음식물쓰레기
     인가요?"의 '이'는 진짜 조사 자리와 글자가 같다. 실제로 '이 + 재질어'
     52건 중 50건이 진짜 조사(껍질이, 된장이, 생크림이)라 조사에서 뺄 수도
     없다. 대신 **머리말 + '이'가 코퍼스에 낱말로 있고 머리말 자체는 없으면**
     긴 쪽을 쓴다. 떡볶이, 손톱깎이, 뽁뽁이, 강냉이가 이 규칙으로 돌아온다.
  3. 검색 결과에는 품목이 아예 없는 질문이 섞인다. 지식iN은 열린 게시판이라
     "고3 세특 버려도 되나요", "욕심 버리는법"이 같은 어미로 걸린다.
     기계로 확실한 것만 민다. 애매하면 미판정으로 두고 사람이 본다. 미는 갈래는
     셋이다.
       - '노이즈'  사람의 사정을 묻는 질문
       - '지역'    "강서구 대형폐기물", "대구 북구 음식물쓰레기". 품목 축이
                   아니라 B층이고 B층은 폐기했다 (확정 판단 1)
       - '절차'    "원룸 분리수거", "아파트 음식물쓰레기". 물건이 아니라 사는
                   곳을 묻는다. 가이드 축이다 (판단 10)
     머리말이 통째로 꼬리말이면(제목이 "일반 쓰레기인가요?" 뿐이면) 물건이
     없는 것이므로 버린다. 꼬리를 떼다 남은 토막("분리", "대형")도 마찬가지다.

조회수는 여기 없다. 판단 60번대로 어차피 자르는 데 못 쓴다.

    python scripts/extract_kin_seeds.py
"""
import csv
import io
import json
import os
import re
import sys
import importlib.util
from collections import Counter, defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data", "raw", "kin-search.json")
OUT = os.path.join(ROOT, "data", "keywords", "candidates-kin.csv")

# 품목이 아니라 사람의 사정을 묻는 제목. 지식iN이 열린 게시판이라 섞인다.
NOISE = re.compile(
    r"모고|모의고사|세특|출결|생기부|학기|학원|수능|내신|기출|문제집은|"
    r"욕심|미련|집착|감정|스트레스|우울|사람|남친|여친|남자친구|여자친구|"
    r"연애|이별|친구|인간관계|버릇|습관|살은|다이어트|"
    r"게임|롤|쿠키런|메이플|피파|캐릭터|계정|아이템|보상|"
    r"압류|대출|보험|주식|코인|월급|알바|퇴사|면접|"
    r"고양이를|강아지를|반려동물을|아기를|사람을|시체|사체를")

# 재질 판정형 꼬리. Q&A 쪽 패턴이 못 떼는 말투다.
JOSA = r"(?:은|는|이|가|을|를|의|도|만|와|과|랑|이랑|에|에서|이나|나)?\s*"
KIND = (r"(?:일반\s*쓰레기|음식물\s*쓰레기|음식물|재활용\s*쓰레기|재활용품|재활용|"
        r"종량제\s*봉투|종량제|대형\s*폐기물|플라스틱|비닐|종이류|종이|스티로폼|"
        r"고철|캔|유리|의류\s*수거함|수거함)")
END = (r"(?:\s*(?:인가요|인가|이에요|예요|에요|맞나요|맞죠|맞나|인지|일까요|"
       r"되나요|될까요|돼요|되요|하나요|할까요|있나요|요))?")

KIN_TAIL_PATTERNS = [
    JOSA + KIND + r"\s*(?:로|으로|에|에다|에다가)?\s*(?:버려도|버리면|넣어도|"
    r"내놔도|배출해도)?\s*(?:되|괜찮|맞)?\S*" + END,
    JOSA + KIND + END,
    JOSA + r"버려도\s*\S*" + END,
    JOSA + r"(?:씻어서|헹궈서|말려서)\s*\S*" + END,
    JOSA + r"어디에?\s*(?:다가?)?\s*(?:버|내놓|배출)\S*" + END,
    JOSA + r"(?:처리|폐기|배출)\s*\S*" + END,
    r"\s*(?:질문|문의|궁금해요|궁금합니다|알려주세요|도와주세요|급해요|급함)\s*$",
]
KIN_TAIL_RE = [re.compile(p + r"\s*[?!.~,ㅜㅠ]*$") for p in KIN_TAIL_PATTERNS]

# 물건의 상태. 물건 이름이 아니므로 갈라 둔다.
MODIFIER = re.compile(
    r"^(?:고장\s*난?|망가진|깨진|부러진|찢어진|오래된|낡은|헌|중고|새|"
    r"안\s*쓰는|안\s*쓴|다\s*쓴|사용한|쓰던|쓴|먹다\s*남은|남은|"
    r"유통기한\s*지난|기한\s*지난|썩은|상한|곰팡이\s*핀|녹슨|녹은|"
    r"코팅이?\s*벗겨진|구멍\s*난|작아진|못\s*쓰는|버려진|더러운|"
    r"큰|작은|대형|소형|플라스틱|유리|철제|나무)\s+")

LEAD = re.compile(r"^(?:저희|우리|제가|저는|혹시|그럼|그리고|이거|이것|그거|"
                  r"요것|얘|이|그|저)\s+")

DROP_WORDS = ("기타", "그외", "그 외", "일체", "해당", "품목", "문의", "질문",
              "생활폐기물", "재활용", "분리배출", "분리수거", "쓰레기", "폐기물",
              "일반쓰레기", "음식물", "음식물쓰레기", "종량제봉투", "대형폐기물",
              "재활용쓰레기", "그냥", "급해요", "급해유",
              # 꼬리를 떼다 남은 토막
              "분리", "대형", "생활", "버리", "버려", "이건", "이거", "그거",
              "이것", "저것", "요것", "재활용품", "재활용쓰레기통", "쓰레기통들",
              "일반", "음쓰", "종량제", "배출", "처리", "폐기", "수거")

# 사는 곳을 묻는 질문. 물건이 아니라 절차라 가이드 축이다 (판단 10)
HOUSING = ("아파트", "원룸", "빌라", "오피스텔", "주택", "단독주택", "가정용",
           "자취방", "기숙사", "고시원", "학교", "회사", "사무실", "가게",
           "식당", "군대", "타지역", "이사후", "이사 후", "주택가")

# 지역을 묻는 질문. B층은 폐기했다 (확정 판단 1)
SIDO = ("서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종",
        "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주",
        "서울시", "경기도", "강원도", "충청북도", "충청남도", "전라북도",
        "전라남도", "경상북도", "경상남도", "제주도")
# '시'를 안 붙이고 도시 이름만 적는다. "안산 폐기물처리", "청주 대형폐기물"
CITY = ("수원", "성남", "안양", "안산", "용인", "부천", "광명", "평택", "과천",
        "오산", "시흥", "군포", "의왕", "하남", "파주", "이천", "안성", "김포",
        "화성", "여주", "양평", "고양", "일산", "의정부", "남양주", "구리",
        "포천", "양주", "동두천", "가평", "연천", "춘천", "원주", "강릉",
        "동해", "태백", "속초", "삼척", "홍천", "청주", "충주", "제천",
        "천안", "공주", "보령", "아산", "서산", "논산", "계룡", "당진",
        "전주", "군산", "익산", "정읍", "남원", "김제", "목포", "여수",
        "순천", "나주", "광양", "포항", "경주", "김천", "안동", "구미",
        "영주", "영천", "상주", "문경", "경산", "창원", "진주", "통영",
        "사천", "김해", "밀양", "거제", "양산", "서귀포", "분당", "판교")
GU = ("강남", "강동", "강북", "강서", "관악", "광진", "구로", "금천", "노원",
      "도봉", "동대문", "동작", "마포", "서대문", "서초", "성동", "성북",
      "송파", "양천", "영등포", "용산", "은평", "종로", "중랑", "수성", "달서",
      "달성", "남동", "부평", "연수", "계양", "미추홀", "해운대", "사하",
      "금정", "북", "남", "동", "서", "중", "유성", "대덕")
REGION_TAIL = re.compile(r"(?:특별시|광역시|특별자치시|특별자치도|"
                         r"[가-힣]{2,4}(?:시|군|구)(?:청)?)$")

# 생활폐기물이 아니다. 우리가 답하는 축 밖이다
BIZ = re.compile(r"^(?:사업장|산업|건설|공사장?|의료|방사성|화학|지정|"
                 r"유해화학|감염성|폐기물처리기사|폐기물처리산업기사|"
                 r"폐기물\s*처리\s*(?:기사|산업기사|시설|업체|장))")

# 학교 과목과 시험지. 지식iN에서 '버려도 되나요'가 제일 많이 쓰이는 자리다
STUDY = re.compile(r"^(?:고[1-3]|중[1-3]|초[1-6]|[1-9]학년|수학|영어|국어|한문|"
                   r"과학|사회|한국사|물리|화학1|생명|지구과학|기하|미적|확통|"
                   r"기말|중간|모고|모의고사|시험지|교과서|문제집|자습서|수능|"
                   r"ncs|기가)(?:\s|$)")


def load_qna():
    path = os.path.join(ROOT, "scripts", "extract_qna_seeds.py")
    spec = importlib.util.spec_from_file_location("q", path)
    mod = importlib.util.module_from_spec(spec)
    cwd = os.getcwd()
    os.chdir(ROOT)
    try:
        spec.loader.exec_module(mod)
    finally:
        os.chdir(cwd)
    return mod


def strip_tails(qna, title):
    t = re.sub(r"[\"'\[\]()（）]", " ", title)
    t = re.sub(r"\s+", " ", t).strip()
    t = LEAD.sub("", t)
    for _ in range(5):                       # 꼬리가 겹쳐 붙는다
        before = t
        for rx in qna.TAIL_RE + KIN_TAIL_RE:
            cut = rx.sub("", t).strip(" ,.-")
            if not cut:
                return ""                    # 제목이 통째로 꼬리말 = 물건이 없다
            if cut != t:
                t = cut
        if t == before:
            break
    return t.strip(" ,.-?!~")


def region_or_housing(name, title):
    """품목 축이 아닌 갈래면 이름을 돌려준다."""
    first = name.split()[0] if name.split() else ""
    if name in HOUSING or first in HOUSING:
        return "절차"
    if first in SIDO or first in ("%s구" % g for g in GU):
        return "지역"
    if REGION_TAIL.search(first) and len(first) >= 3:
        return "지역"
    if first in CITY:
        return "지역"
    if BIZ.match(name):
        return "사업장"
    if STUDY.match(name.lower()):
        return "노이즈"
    return ""


def corpus_tokens(rows):
    toks = set()
    for r in rows:
        for t in re.split(r"[^가-힣A-Za-z0-9]+", r["title"]):
            if t:
                toks.add(t)
    return toks


def restore_i(name, toks):
    """조사 '이'에 먹힌 이름을 되돌린다. 코퍼스가 판정한다."""
    if name.endswith("이") or " " in name:
        return name
    return name + "이" if (name + "이") in toks and name not in toks else name


def split_modifier(name):
    mods = []
    for _ in range(3):
        m = MODIFIER.match(name)
        if not m:
            break
        mods.append(m.group(0).strip())
        name = name[m.end():]
    return name.strip(), " ".join(mods)


def main():
    rows = json.load(io.open(SRC, encoding="utf-8"))
    toks = corpus_tokens(rows)
    qna = load_qna()
    vocab = qna.load_vocab()
    vocab_terms = sorted((k for k in vocab if len(k) >= 2), key=len, reverse=True)

    groups = defaultdict(lambda: {"n": 0, "mods": set(), "titles": [], "noise": 0})
    n_proc = 0
    for r in rows:
        title = r["title"]
        if qna.PROCEDURE.search(title):
            n_proc += 1
            continue
        name = strip_tails(qna, title)
        name = restore_i(name, toks)
        name, mods = split_modifier(name)
        if not name or len(name) < 2 or not re.search(r"[가-힣]", name):
            continue
        if any(w == name for w in DROP_WORDS):
            continue
        if len(name) > 20:                   # 문장이 통째로 남은 것
            continue
        g = groups[qna.norm(name)]
        g["n"] += 1
        if mods:
            g["mods"].add(mods)
        if NOISE.search(title):
            g["noise"] += 1
        if len(g["titles"]) < 3:
            g["titles"].append(title)
        g.setdefault("name", name)

    out = []
    for key, g in groups.items():
        hit = next((t for t in vocab_terms if t in key), None)
        axis = region_or_housing(g["name"], g["titles"][0])
        if hit:
            decision, note = "기존 커버", vocab[hit]
        elif axis:
            decision, note = axis, ""
        elif g["noise"] >= g["n"]:           # 걸린 제목이 전부 사람 사정
            decision, note = "노이즈", ""
        else:
            decision, note = "", ""
        out.append({
            "item": g["name"],
            "n": g["n"],
            "modifiers": ", ".join(sorted(g["mods"]))[:60],
            "covered_by": vocab[hit] if hit else "",
            "decision": decision,
            "note": note or " | ".join(g["titles"])[:160],
        })
    out.sort(key=lambda r: (-r["n"], r["item"]))

    with io.open(OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=[
            "item", "n", "modifiers", "covered_by", "decision", "note"])
        w.writeheader()
        w.writerows(out)

    new = [r for r in out if not r["decision"]]
    print("제목 %d, 절차 %d, 머리말 %d" % (len(rows), n_proc, len(out)))
    tally = Counter(r["decision"] or "미판정" for r in out)
    print("  " + ", ".join("%s %d" % (k, tally[k]) for k in
          ("기존 커버", "지역", "절차", "사업장", "노이즈", "미판정") if tally[k]))
    print("-> %s" % OUT)
    for r in new[:30]:
        print("   %3d  %-16s %s" % (r["n"], r["item"][:16], r["note"][:60]))


if __name__ == "__main__":
    main()
