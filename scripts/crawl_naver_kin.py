# -*- coding: utf-8 -*-
"""네이버 지식iN 검색 수집 -- 답을 못 찾아 물은 목록의 두 번째 판.

출력: data/raw/kin-search.json  (q, title, date)

씨앗 출처를 재점검한 결과다. 지금까지 쓴 다섯(자동완성 재크롤, 지자체
수수료표, blisgo, 품목사전, 분리배출 Q&A)에서 Q&A만 판단 49가 말하는
'물은 목록'이었는데 회차 두 번에 말랐다(판단 62). 같은 성질이면서 자릿수가
다른 자리가 지식iN이다. 분리배출 Q&A가 1,330건, 여기는 어미 하나로만
수백 쪽이 나온다.

품목사전, 수수료표와 갈리는 점은 **물건 이름이 아니라 상태로 묻는다**는
것이다. "고장난 우레탄 폼 캔", "곰팡이 핀 고양이 사료", "코팅이 벗겨진
프라이팬"처럼 우리가 가진 어느 목록에도 없는 형태로 온다. 판단 38이 말하는
'답이 둘로 갈린 자리'를 목록이 아니라 사람 말로 준다.

수집 규칙 두 가지.
  1. 검색이 '법' 한 글자로도 걸려서 "남자끼리 손절치는 법"이 섞인다.
     **제목 자체가 배출을 말해야** 담는다.
  2. 쪽이 깊어질수록 관련도가 떨어진다. 40쪽을 상한으로 둔다.

    python scripts/crawl_naver_kin.py
    python scripts/crawl_naver_kin.py --pages 10       (탐침)
"""
import html
import io
import json
import os
import re
import sys
import time
import urllib.parse

import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "raw", "kin-search.json")
LIST = "https://kin.naver.com/search/list.naver"
DELAY = 0.35

# 질의. 어미만 넣는다 - 품목명을 넣으면 판단 13의 고리가 다시 닫힌다.
# 뒤쪽 넷(재질 판정)은 답이 갈리는 자리를 직접 겨눈다.
QUERIES = [
    "버리는법", "버리는 방법", "버리는 곳",
    "분리수거", "분리배출", "분리수거 방법",
    "음식물쓰레기", "음식물 쓰레기 인가요", "음식물 아닌가요",
    "일반쓰레기", "일반쓰레기 인가요",
    "종량제봉투", "재활용", "재활용 되나요", "재활용 쓰레기",
    "대형폐기물", "폐기물 처리",
    "어디에 버려", "버려도 되나요", "버리면 되나요", "어떻게 버려요",
    "플라스틱인가요", "종이류인가요", "스티로폼인가요", "고철인가요",
    "수거함에 넣어도", "씻어서 버려야", "유통기한 지난",
]

TITLE_RE = re.compile(r'_searchListTitleAnchor[^>]*>(.*?)</a>', re.S)
DATE_RE = re.compile(r'<dd class="txt_inline">([\d.]+)\.?</dd>')
DISPOSAL = re.compile(
    r"버리|버려|분리\s*수거|분리\s*배출|음식물|종량제|폐기|재활용|쓰레기|"
    r"배출|수거함|버린")


def text(raw):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", raw))).strip()


def main():
    pages = 40
    if "--pages" in sys.argv:
        pages = int(sys.argv[sys.argv.index("--pages") + 1])

    s = requests.Session()
    s.headers["User-Agent"] = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

    rows, seen, dropped = [], set(), 0
    for q in QUERIES:
        kept = 0
        for page in range(1, pages + 1):
            url = "%s?query=%s&page=%d" % (LIST, urllib.parse.quote(q), page)
            try:
                body = s.get(url, timeout=20).text
            except Exception as e:
                print("  %s p%d 실패: %s" % (q, page, e))
                break
            titles = [text(m) for m in TITLE_RE.findall(body)]
            if not titles:
                break
            for t in titles:
                if not t or t in seen:
                    continue
                seen.add(t)
                if not DISPOSAL.search(t):
                    dropped += 1
                    continue
                rows.append({"q": q, "title": t})
                kept += 1
            time.sleep(DELAY)
        print("%-18s 배출 제목 %4d (누적 %d)" % (q, kept, len(rows)))

    if not rows:
        sys.exit("수집 0건. 산출물을 안 쓴다 (판단 43).")

    io.open(OUT, "w", encoding="utf-8").write(
        json.dumps(rows, ensure_ascii=False, indent=1))
    print("\n제목 %d건(무관 %d건 버림) -> %s" % (len(rows), dropped, OUT))


if __name__ == "__main__":
    main()
