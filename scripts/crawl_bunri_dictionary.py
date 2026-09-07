# -*- coding: utf-8 -*-
"""분리의정석(생활폐기물 분리배출 누리집, 환경부/한국폐기물협회) 품목사전 수집.

출력: data/raw/bunri-dictionary.json  (id, name, cls, base, page)

훈령 별표1에 이름이 없는 품목이 여기에는 있다(docs/35, 판단 41번). 770개가
재활용, 일반, 음식물, 대형으로 나뉘어 있어 "품목마다 답이 갈리는 영역"이다.
씨앗 출처로 쓴다. 상세 안내문은 fnViewArticle(id)로 따로 열어야 하므로 여기서는
목록(이름과 분류)만 받는다.
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
OUT = os.path.join(ROOT, "data", "raw", "bunri-dictionary.json")
BASE = "https://xn--oy2b29bd3a601b.kr"

ITEM_RE = re.compile(
    r"fnViewArticle\('(\d+)'\).*?<p>\s*(.*?)\s*</p>\s*<span class=\"tit\">(.*?)</span>",
    re.S,
)


def main():
    s = requests.Session()
    s.headers["User-Agent"] = "Mozilla/5.0 (jalbeo seed crawler)"
    r0 = s.get(BASE + "/front/dischargeMethod/dictionary.do", timeout=30)
    csrf = re.search(r'id="hdCsrfTk" value="([^"]+)"', r0.text).group(1)
    total = int(re.search(r"총 <strong>(\d+)개</strong>", r0.text).group(1))
    rows, seen, page = [], set(), 1
    while True:
        r = s.post(BASE + "/front/dischargeMethod/ajaxDictionaryHtml.do", timeout=30,
                   data={"searchCnd": "1", "searchWrd": "", "searchOp1": "",
                         "searchOp2": "", "pageIndex": str(page), "_csrf": csrf})
        found = 0
        for m in ITEM_RE.finditer(r.text):
            nid, name = m.group(1), m.group(3).strip()
            cls = re.sub(r"\s*,\s*", ", ", re.sub(r"\s+", " ", m.group(2))).strip(" ,")
            if nid in seen:
                continue
            seen.add(nid)
            found += 1
            base = re.sub(r"\s*\(.*?\)\s*$", "", name)  # '단소(플라스틱)' -> '단소'
            rows.append({"id": int(nid), "name": name, "base": base,
                         "cls": cls, "page": page})
        print("page %d: %d (누적 %d / %d)" % (page, found, len(rows), total))
        if found == 0 or len(rows) >= total:
            break
        page += 1
        time.sleep(0.3)
    rows.sort(key=lambda x: -x["id"])
    io.open(OUT, "w", encoding="utf-8").write(
        json.dumps(rows, ensure_ascii=False, indent=1) + "\n")
    print("저장", OUT, len(rows))


if __name__ == "__main__":
    main()
