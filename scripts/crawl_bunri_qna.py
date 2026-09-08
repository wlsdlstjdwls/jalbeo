# -*- coding: utf-8 -*-
"""분리의정석 '분리배출 Q&A' 게시판 수집 -- 사람이 실제로 물은 것.

출력: data/raw/bunri-qna.json  (no, cls, title, date, views, answered)

품목사전(`crawl_bunri_dictionary.py`)은 **운영자가 답을 정해 둔 목록**이다.
여기는 **답이 없어서 물어본 목록**이다. 판단 38번이 말하는 자리가 정확히
이쪽이다 - 답이 하나로 굳어 있으면 검색이 없고, 둘로 갈려 있으면 검색이 몰린다.
게시판에 올라온 질문은 그 사람이 사이트를 뒤지고도 못 찾았다는 뜻이다.

판단 35번의 조건도 만족한다. 우리 페이지를 참조하지 않고, 발행분에서 뽑은
씨앗(판단 13)이 못 보는 자리를 본다. 실제로 첫 쪽에서만 쓰레받기, 썩은 쌀,
데오드란트가 나왔고 셋 다 우리 어휘에 없다.

조회수는 같이 받되 **자르는 데 쓰지 않는다** (판단 16 - 자동완성 빈도가
수요 순위가 아니었던 것과 같다). 자르는 건 실측이 한다.
"""
import io
import json
import os
import re
import sys
import time

import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "raw", "bunri-qna.json")
BASE = "https://xn--oy2b29bd3a601b.kr"
LIST = "/front/support/qna.do"

ROW_RE = re.compile(
    r"<tr[^>]*>\s*"
    r"<td[^>]*>\s*(\d+)\s*</td>\s*"          # 번호
    r"<td[^>]*>(.*?)</td>\s*"                # 폐기물 종류
    r"<td[^>]*>(.*?)</td>\s*"                # 제목
    r"<td[^>]*>(.*?)</td>\s*"                # 작성자
    r"<td[^>]*>\s*([\d.]+)\s*</td>\s*"       # 등록일
    r"<td[^>]*>\s*([\d,]+)\s*</td>\s*"       # 조회수
    r"<td[^>]*>(.*?)</td>",                  # 답변상태
    re.S,
)


def text(html):
    s = re.sub(r"<[^>]+>", " ", html or "")
    s = s.replace("&amp;", "&").replace("&nbsp;", " ").replace("&gt;", ">")
    s = s.replace("&lt;", "<").replace("&quot;", '"')
    return re.sub(r"\s+", " ", s).strip()


def main():
    s = requests.Session()
    s.headers["User-Agent"] = "Mozilla/5.0 (jalbeo seed crawler)"
    r0 = s.get(BASE + LIST, timeout=30)
    csrf = re.search(r'id="hdCsrfTk" value="([^"]+)"', r0.text).group(1)
    m = re.search(r"총\s*</?[^>]*>?\s*([\d,]+)\s*</?[^>]*>?\s*건", r0.text)
    total = int(m.group(1).replace(",", "")) if m else 0

    rows, seen, page = [], set(), 1
    while True:
        r = (r0 if page == 1 else
             s.post(BASE + LIST, timeout=30,
                    data={"pageIndex": str(page), "_csrf": csrf}))
        found = 0
        for mm in ROW_RE.finditer(r.text):
            no = int(mm.group(1))
            if no in seen:
                continue
            seen.add(no)
            found += 1
            rows.append({
                "no": no,
                "cls": text(mm.group(2)),
                "title": text(mm.group(3)),
                "date": mm.group(5).strip().rstrip("."),
                "views": int(mm.group(6).replace(",", "")),
                "answered": "답변완료" in text(mm.group(7)),
            })
        print("page %d: %d (누적 %d / %d)" % (page, found, len(rows), total))
        if found == 0 or (total and len(rows) >= total):
            break
        page += 1
        time.sleep(0.3)

    rows.sort(key=lambda x: -x["no"])
    io.open(OUT, "w", encoding="utf-8").write(
        json.dumps(rows, ensure_ascii=False, indent=1))
    print("\n질문 %d건 -> %s" % (len(rows), OUT))
    if total and len(rows) < total * 0.9:
        sys.exit("수집이 총 %d건의 90%%에 못 미친다. 파서를 본다 (판단 43)." % total)


if __name__ == "__main__":
    main()
