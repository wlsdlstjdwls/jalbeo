# -*- coding: utf-8 -*-
"""색인 요청을 손으로 넣을 URL 묶음을 뽑고, 넣은 것을 기록한다.

구글 서치콘솔 URL 검사와 네이버 서치어드바이저 웹페이지 수집요청은 하루
할당량이 있다(구글 10, 네이버 50). 175개를 여러 날에 걸쳐 나눠 넣어야 하고,
어제 넣은 것을 오늘 또 넣으면 할당량만 버린다. 그 진행 상태를 남긴다.

    python scripts/indexing_queue.py --engine naver            # 다음 50개, 기록함
    python scripts/indexing_queue.py --engine google           # 다음 10개, 기록함
    python scripts/indexing_queue.py --engine google --dry     # 보기만, 기록 안 함
    python scripts/indexing_queue.py --status                  # 진행률만
    python scripts/indexing_queue.py --engine naver --undo     # 마지막 묶음 취소

기록은 data/indexing/submitted.json. 커밋해서 세션이 바뀌어도 이어간다.

순서는 검색 수요 순이다. 홈, 가이드 5개, 그 다음 품목을 monthly_volume
내림차순으로 낸다. 할당량이 적은 구글일수록 앞쪽이 중요하다.
"""
import argparse
import datetime
import io
import json
import os
import re
import sys
import urllib.parse
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEMS = os.path.join(ROOT, "site", "src", "data", "items.json")
STATE_DIR = os.path.join(ROOT, "data", "indexing")
STATE = os.path.join(STATE_DIR, "submitted.json")
SITEMAP = "https://jalbeo.com/sitemap-0.xml"
LOCAL_SITEMAP = os.path.join(ROOT, "site", "dist", "sitemap-0.xml")

# 하루 할당량. 구글은 URL 검사 색인 요청, 네이버는 웹페이지 수집요청 기준.
QUOTA = {"google": 10, "naver": 50}


def load_urls():
    """사이트맵이 발행 목록의 원본이다. 라이브를 먼저 보고, 안 되면 로컬 빌드."""
    xml = None
    try:
        with urllib.request.urlopen(SITEMAP, timeout=15) as r:
            xml = r.read().decode("utf-8")
    except Exception:
        if os.path.exists(LOCAL_SITEMAP):
            xml = io.open(LOCAL_SITEMAP, encoding="utf-8").read()
    if not xml:
        sys.exit("사이트맵을 못 읽었다. 네트워크를 보거나 site에서 npm run build 를 먼저 돌려라.")
    return re.findall(r"<loc>([^<]+)</loc>", xml)


def rank(urls):
    """검색 수요 순으로 세운다. 홈 -> 가이드 -> 품목(검색량 내림차순) -> 나머지."""
    vol = {}
    for it in json.load(io.open(ITEMS, encoding="utf-8")):
        # 미측정(null)은 0이 아니다. 여기서 0을 주는 것은 값을 지어내는 게
        # 아니라 "순서를 뒤로 민다"는 뜻뿐이다 (현재 3개).
        vol[it["slug"]] = it.get("monthly_volume") or 0

    def key(u):
        path = urllib.parse.urlparse(u).path.strip("/")
        if path == "":
            return (0, 0, u)
        if path.startswith("guides"):
            return (1, 0, u)
        slug = path.split("/")[-1]
        if slug in vol:
            return (2, -vol[slug], u)
        return (3, 0, u)

    return sorted(urls, key=key)


def load_state():
    if os.path.exists(STATE):
        return json.load(io.open(STATE, encoding="utf-8"))
    return {"google": {}, "naver": {}}


def save_state(state):
    if not os.path.isdir(STATE_DIR):
        os.makedirs(STATE_DIR)
    with io.open(STATE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def progress(state, urls):
    lines = []
    for eng in ("google", "naver"):
        done = len([u for u in urls if u in state.get(eng, {})])
        left = len(urls) - done
        days = (left + QUOTA[eng] - 1) // QUOTA[eng]
        lines.append(
            "%-7s %3d / %3d  남은 %3d개, 하루 %d개면 %d일"
            % (eng, done, len(urls), left, QUOTA[eng], days)
        )
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", choices=["google", "naver"])
    ap.add_argument("--count", type=int, help="기본은 엔진별 하루 할당량")
    ap.add_argument("--dry", action="store_true", help="기록하지 않고 보기만")
    ap.add_argument("--undo", action="store_true", help="그 엔진의 마지막 묶음을 취소")
    ap.add_argument("--status", action="store_true", help="진행률만 출력")
    args = ap.parse_args()

    urls = rank(load_urls())
    state = load_state()

    if args.status or not args.engine:
        print(progress(state, urls))
        return

    eng = args.engine
    done = state.setdefault(eng, {})

    if args.undo:
        if not done:
            sys.exit("%s 기록이 비어 있다. 취소할 게 없다." % eng)
        last = max(done.values())
        removed = [u for u, d in done.items() if d == last]
        for u in removed:
            del done[u]
        save_state(state)
        print("%s 마지막 묶음(%s) %d개를 취소했다." % (eng, last, len(removed)))
        print(progress(state, urls))
        return

    n = args.count or QUOTA[eng]
    batch = [u for u in urls if u not in done][:n]

    if not batch:
        print("%s 는 %d개 전부 넣었다. 더 넣을 게 없다." % (eng, len(urls)))
        return

    today = datetime.date.today().isoformat()
    print("# %s 색인 요청 %d개 (%s)" % (eng, len(batch), today))
    print()
    for i, u in enumerate(batch, 1):
        print("%2d. %s" % (i, u))
    print()

    if args.dry:
        print("(--dry 라 기록 안 했다. 실제로 넣었으면 --dry 빼고 다시 돌려라)")
    else:
        for u in batch:
            done[u] = today
        save_state(state)
        print("기록함 -> %s" % os.path.relpath(STATE, ROOT))
    print()
    print(progress(state, urls))


if __name__ == "__main__":
    main()
