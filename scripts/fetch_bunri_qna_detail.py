# -*- coding: utf-8 -*-
"""분리배출 Q&A 한 건의 질문과 답변 본문을 받는다.

`crawl_bunri_qna.py`는 목록만 긁는다 - 씨앗을 뽑는 데는 제목이면 됐다.
그런데 판단 74번대로 **Q&A는 씨앗 출처이자 조사 출처**다. 품목사전은
표제어가 있는 것만 답하고 Q&A는 표제어가 없는 것을 답한다. 조사할 때는
본문이 있어야 인용할 수 있다.

목록의 `no`(화면 번호)와 상세의 `nqIdx`(내부 번호)는 다르다. 새 글이
쌓이면 화면 번호가 밀리므로 **제목으로 찾아 nqIdx를 얻는다.**

    python scripts/fetch_bunri_qna_detail.py 볼링공 콘돔 시멘트

받은 것은 data/raw/bunri-qna-detail.json에 쌓는다 (같은 nqIdx는 덮어쓴다).
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
OUT = os.path.join(ROOT, "data", "raw", "bunri-qna-detail.json")
BASE = "https://xn--oy2b29bd3a601b.kr"
LIST = "/front/support/qna.do"
VIEW = "/front/support/qnaView.do"

LINK_RE = re.compile(r"fnViewArticle\('(\d+)'\)[^>]*>\s*([^<]{1,120})")


def text(html):
    s = re.sub(r"<script.*?</script>", " ", html or "", flags=re.S)
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"</(p|div|li|tr)>", "\n", s)
    s = re.sub(r"<[^>]+>", " ", s)
    for a, b in (("&amp;", "&"), ("&nbsp;", " "), ("&gt;", ">"),
                 ("&lt;", "<"), ("&quot;", '"'), ("&#39;", "'")):
        s = s.replace(a, b)
    s = re.sub(r"[ \t]+", " ", s)
    return re.sub(r"\n\s*\n+", "\n", s).strip()


def index(s, csrf, pages=160):
    """제목 -> nqIdx. 목록을 돌며 모은다."""
    out = []
    for page in range(1, pages + 1):
        r = s.post(BASE + LIST, timeout=30,
                   data={"pageIndex": str(page), "_csrf": csrf})
        found = LINK_RE.findall(r.text)
        if not found:
            break
        for idx, title in found:
            out.append((int(idx), text(title)))
        time.sleep(0.2)
    return out


def detail(s, csrf, idx):
    r = s.post(BASE + VIEW, timeout=30,
               data={"nqIdx": str(idx), "_csrf": csrf})
    body = text(r.text)
    # 상세 화면은 머리말, 질문, 답변 순서다. 답변 표시줄로 가른다
    m = re.search(r"(답\s*변|답변내용)", body)
    return {
        "nqIdx": idx,
        "raw": body,
        "answer": body[m.start():] if m else "",
    }


def main():
    words = [w for w in sys.argv[1:] if not w.startswith("-")]
    if not words:
        sys.exit("찾을 말을 적는다: python scripts/fetch_bunri_qna_detail.py 볼링공")

    s = requests.Session()
    s.headers["User-Agent"] = "Mozilla/5.0 (jalbeo research)"
    r0 = s.get(BASE + LIST, timeout=30)
    csrf = re.search(r'id="hdCsrfTk" value="([^"]+)"', r0.text).group(1)

    pairs = index(s, csrf)
    print("목록 %d건" % len(pairs))

    store = {}
    if os.path.exists(OUT):
        store = {str(r["nqIdx"]): r for r in
                 json.load(io.open(OUT, encoding="utf-8"))}

    want = [(i, t) for i, t in pairs if any(w in t for w in words)]
    print("걸린 것 %d건" % len(want))
    for idx, title in want:
        d = detail(s, csrf, idx)
        d["title"] = title
        store[str(idx)] = d
        print("\n===== [%d] %s" % (idx, title))
        print(d["answer"][:900] or d["raw"][:900])
        time.sleep(0.3)

    rows = sorted(store.values(), key=lambda r: -r["nqIdx"])
    io.open(OUT, "w", encoding="utf-8").write(
        json.dumps(rows, ensure_ascii=False, indent=1))
    print("\n-> %s (%d건)" % (OUT, len(rows)))


if __name__ == "__main__":
    main()
