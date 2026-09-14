# -*- coding: utf-8 -*-
"""분리의정석 품목사전 **상세**를 받는다. 목록에 없는 두 필드가 목적이다.

입력: data/raw/bunri-dictionary.json (crawl_bunri_dictionary.py)
출력: data/raw/bunri-dictionary-detail.json
      (id, name, cls, terms, term_entries, similar_items, method, note, caution)

`docs/36`이 목록만 받고 <q>상세 안내문은 dictionaryView.do로 따로 열어야
한다</q>고 적은 뒤로, 상세는 판정할 때 손으로 한 건씩 열어 봤을 뿐이다.
그 화면에 **유사검색어** 칸이 있다. 텀블러(niIdx=77)에는 빨대, 카페
일회용컵, 보온도시락통, 보온보냉팩, 컵 워머가 걸려 있다.

이 칸이 지금까지 쓴 씨앗 출처와 다른 점은 **목록이 아니라 검색어**라는
것이다. 품목사전 표제어는 '텀블러'인데 사람은 '보온도시락통'으로 찾는다 -
그 대응을 환경부 사이트가 직접 적어 뒀다. 판단 67이 지식iN에서 본 것과
같은 갈림인데, 이쪽은 답이 이미 붙어 있다.

유사검색어 칸은 두 종류가 섞여 있다. `dictionaryView.do?niIdx=`로 걸린 말은
**품목사전에 표제어가 있는** 말이고, `javascript:void(0)`인 말은 표제어가
없다. 텀블러에서는 빨대와 카페 일회용컵이 앞쪽, 보온도시락통, 보온보냉팩,
컵 워머가 뒤쪽이다. 뒤쪽이 우리가 못 본 자리다 - 사전이 "이 말로 찾는
사람이 있다"고 인정하면서 페이지는 안 준 말이다. 갈라서 담는다.

`유사품목`(배출방법이 동일한 품목)은 판단 45가 개명과 분리를 가르는 데
쓴다. 같이 받아 둔다.

    python scripts/crawl_bunri_detail.py
    python scripts/crawl_bunri_detail.py --limit 20   (탐침)
"""
import html
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
SRC = os.path.join(ROOT, "data", "raw", "bunri-dictionary.json")
OUT = os.path.join(ROOT, "data", "raw", "bunri-dictionary-detail.json")
BASE = "https://xn--oy2b29bd3a601b.kr"
VIEW = BASE + "/front/dischargeMethod/dictionaryView.do"
DELAY = 0.3


def strip(raw):
    raw = re.sub(r"(?s)<script.*?</script>|<style.*?</style>", " ", raw)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(raw))).strip()


def block(text, start, ends):
    """'유사검색어'처럼 제목만 있고 태그가 없는 칸을 다음 제목 앞까지 자른다."""
    i = text.find(start)
    if i < 0:
        return ""
    seg = text[i + len(start):]
    cut = len(seg)
    for e in ends:
        j = seg.find(e)
        if 0 <= j < cut:
            cut = j
    return seg[:cut].strip(" ·-,")


# 상세 화면의 칸 순서. 뒤 칸이 앞 칸의 끝이다.
FIELDS = ["유사검색어", "배출방법", "특징", "유의사항", "유사품목",
          "※ 배출방법은", "가까운 분리배출 장소"]

# 유사검색어 칸. 낱말 경계가 태그에만 있어서 글자로는 못 가른다
# ('카페 일회용컵', '화분 이름표'에 공백이 들어 있다).
TERM_BLOCK = re.compile(r'<dt class="btit">유사검색어</dt>(.*?)</dl>', re.S)
TERM_A = re.compile(r'<a href="([^"]*)"[^>]*>(.*?)</a>', re.S)


def parse(raw):
    t = strip(raw)
    out = {}
    for n, f in enumerate(FIELDS[:-2]):
        out[f] = block(t, f, FIELDS[n + 1:])
    out["유사품목"] = block(t, "배출방법이 동일한 유사품목", FIELDS[-2:])
    return out


def parse_terms(raw):
    """(표제어 없는 말, 표제어 있는 말). 앞쪽이 씨앗이다."""
    m = TERM_BLOCK.search(raw)
    if not m:
        return [], []
    bare, linked = [], []
    for href, label in TERM_A.findall(m.group(1)):
        name = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", label))).strip()
        if not name:
            continue
        (linked if "niIdx=" in href else bare).append(name)
    return bare, linked


def terms(s):
    return re.sub(r"\s+", " ", s).strip()


def main():
    limit = None
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])

    items = json.load(io.open(SRC, encoding="utf-8"))
    if limit:
        items = items[:limit]

    s = requests.Session()
    s.headers["User-Agent"] = "Mozilla/5.0 (jalbeo seed crawler)"

    rows, fail = [], 0
    for n, it in enumerate(items, 1):
        try:
            r = s.get(VIEW, params={"niIdx": it["id"]}, timeout=25)
        except Exception as e:
            print("  %s 실패: %s" % (it["name"], e))
            fail += 1
            continue
        if r.status_code != 200 or len(r.text) < 3000:
            fail += 1
            continue
        f = parse(r.text)
        bare, linked = parse_terms(r.text)
        rows.append({
            "id": it["id"],
            "name": it["name"],
            "cls": it.get("cls", ""),
            "terms": bare,
            "term_entries": linked,
            "similar_items": terms(f.get("유사품목", "")),
            "method": f.get("배출방법", "")[:600],
            "note": f.get("특징", "")[:600],
            "caution": f.get("유의사항", "")[:600],
        })
        if n % 50 == 0:
            print("  %d/%d" % (n, len(items)))
        time.sleep(DELAY)

    if not rows:
        sys.exit("수집 0건. 산출물을 안 쓴다 (판단 43).")
    if fail > len(items) * 0.1:
        sys.exit("실패 %d건(%d개 중). 산출물을 안 쓴다" % (fail, len(items)))

    io.open(OUT, "w", encoding="utf-8").write(
        json.dumps(rows, ensure_ascii=False, indent=1) + "\n")
    bare = sorted({t for r in rows for t in r["terms"]})
    linked = sorted({t for r in rows for t in r["term_entries"]})
    print("상세 %d개 (실패 %d)" % (len(rows), fail))
    print("유사검색어  표제어 없는 말 %d개 / 표제어 있는 말 %d개"
          % (len(bare), len(linked)))
    for r in rows[:5]:
        print("   %-14s %s" % (r["name"][:14], ", ".join(r["terms"])[:60]))


if __name__ == "__main__":
    main()
