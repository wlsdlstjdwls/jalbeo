# -*- coding: utf-8 -*-
"""사이트 내 검색어 로그에서 품목 확장 후보를 뽑는다 (docs/20 대기열 4번).

`search_queries`는 방문자가 검색창에 친 말을 그대로 받는다. 그중
**hit_count = 0**(화면에 한 건도 안 걸린 검색)이 "사이트에 없는 물건을
찾다가 못 찾았다"는 신호이고, 그게 다음 품목의 원천이다.

    python scripts/search_log_candidates.py                 못 찾은 검색 후보
    python scripts/search_log_candidates.py --all           걸린 검색까지 전부
    python scripts/search_log_candidates.py --days 14       최근 14일만
    python scripts/search_log_candidates.py --csv out.csv   표로 저장

## 이 스크립트가 하는 일이 '세기'만은 아니다

1. **디바운스 조각을 접는다.** 클라이언트는 입력이 멈춘 뒤에만 쏘지만
   천천히 치면 '캣', '캣타', '캣타워'가 다 남는다. 같은 방문자가 짧은
   간격으로 친 앞토막은 뒤에 온 긴 말에 흡수한다 (`--gap` 초, 기본 180).
2. **발행분과 겹치는지 본다.** 별칭과 초성까지 걸리는 검색(`lib/search.ts`)이
   0건을 냈다는 건 이미 강한 신호지만, 오타나 띄어쓰기로 빗나간 경우가 있어
   품목명/별칭과의 부분 일치를 같이 찍는다. 겹치면 새 품목이 아니라 **별칭**
   후보다 (판단 8번).
3. **표본을 먼저 말한다.** `docs/23`에서 방문자 1명짜리 흔적을 신호로 착각한
   적이 있다. 방문자 수와 기간을 맨 위에 찍고, 얇으면 얇다고 적는다.

빈도순 정식 추출은 트래픽이 쌓인 뒤의 일이다. 표본이 얇으면 이 스크립트는
후보를 내되 '표본 미달'이라고 먼저 말한다.
"""
import argparse
import csv
import io
import json
import os
import re
import sys

import psycopg2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db_apply import load_env  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEMS = os.path.join(ROOT, "site", "src", "data", "items.json")

# 표본 하한. 이 아래면 후보를 내되 '정식 신호 아님'을 먼저 찍는다 (docs/23).
MIN_VISITORS = 10
MIN_MISSES = 20


def norm(s):
    return re.sub(r"\s+", "", str(s or "")).lower()


def connect():
    env = load_env()
    return psycopg2.connect(
        host=env["SUPABASE_DB_HOST"], port=5432, dbname="postgres",
        user=env["SUPABASE_DB_USER"], password=env["SUPABASE_DB_PASSWORD"],
        connect_timeout=20, sslmode="require")


def load_items():
    """발행 품목의 이름과 별칭을 정규화해 모은다."""
    names, aliases = {}, {}
    for it in json.load(io.open(ITEMS, encoding="utf-8")):
        if not it.get("published", True):
            continue
        names[norm(it["name"])] = it["name"]
        for a in it.get("aliases") or []:
            aliases[norm(a)] = it["name"]
    return names, aliases


def fold_prefixes(rows, gap):
    """같은 방문자가 gap초 안에 친 앞토막을 뒤에 온 긴 말에 흡수한다.

    rows는 (term, hit_count, visitor_id, created_at) 오름차순.
    """
    drop = set()
    by_visitor = {}
    for i, (term, hit, vid, at) in enumerate(rows):
        by_visitor.setdefault(vid, []).append((i, term, at))
    for seq in by_visitor.values():
        for a in range(len(seq)):
            i, ta, at_a = seq[a]
            for b in range(a + 1, len(seq)):
                j, tb, at_b = seq[b]
                if (at_b - at_a).total_seconds() > gap:
                    break
                if tb != ta and tb.startswith(ta):
                    drop.add(i)
                    break
    return drop


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=0, help="최근 N일만 (0=전체)")
    ap.add_argument("--all", action="store_true", help="hit_count>0인 검색도 포함")
    ap.add_argument("--min-len", type=int, default=2, help="최소 글자수")
    ap.add_argument("--gap", type=int, default=180, help="디바운스 조각으로 볼 초 간격")
    ap.add_argument("--limit", type=int, default=60, help="화면에 찍을 후보 수")
    ap.add_argument("--csv", help="후보를 CSV로 저장할 경로")
    args = ap.parse_args()

    where = ["char_length(term) >= %s"]
    params = [args.min_len]
    if args.days:
        where.append("created_at >= now() - make_interval(days => %s)")
        params.append(args.days)

    conn = connect()
    with conn, conn.cursor() as cur:
        cur.execute("select count(*), count(distinct visitor_id), "
                    "       min(created_at), max(created_at) from search_queries")
        n_all, n_vis_all, first_at, last_at = cur.fetchone()
        cur.execute("select term, hit_count, visitor_id, created_at from search_queries "
                    "where " + " and ".join(where) + " order by created_at", params)
        rows = cur.fetchall()
    conn.close()

    print("검색 로그 %s건 / 방문자 %s명" % (format(n_all, ","), format(n_vis_all or 0, ",")))
    print("기간 %s ~ %s" % (first_at.date() if first_at else "-",
                            last_at.date() if last_at else "-"))
    if not rows:
        print("\n조건에 맞는 행이 없다. 트래픽이 쌓이기를 기다린다.")
        return

    drop = fold_prefixes(rows, args.gap)
    kept = [r for i, r in enumerate(rows) if i not in drop]
    misses = [r for r in kept if r[1] == 0]
    print("글자수 %d 이상 %d건 -> 디바운스 조각 %d건 접고 %d건, 그중 못 찾은 검색 %d건"
          % (args.min_len, len(rows), len(drop), len(kept), len(misses)))

    pool = kept if args.all else misses
    if not pool:
        print("\n못 찾은 검색이 없다.")
        return

    n_vis = len({r[2] for r in pool if r[2]})
    thin = n_vis < MIN_VISITORS or len(misses) < MIN_MISSES
    if thin:
        print("\n[표본 미달] 방문자 %d명(기준 %d), 못 찾은 검색 %d건(기준 %d)."
              % (n_vis, MIN_VISITORS, len(misses), MIN_MISSES))
        print("빈도 순위를 수요로 읽으면 안 된다. 겹치지 않는 것만 개별 판단한다"
              " (docs/23 선례).")

    names, aliases = load_items()
    agg = {}
    for term, hit, vid, at in pool:
        a = agg.setdefault(term, {"term": term, "n": 0, "vis": set(),
                                  "last": at, "hit": hit})
        a["n"] += 1
        a["vis"].add(vid)
        a["last"] = max(a["last"], at)
        a["hit"] = max(a["hit"], hit)

    out = []
    for a in agg.values():
        t = a["term"]
        if t in names:
            status, ref = "겹침(품목명)", names[t]
        elif t in aliases:
            status, ref = "겹침(별칭)", aliases[t]
        else:
            hit_name = next((v for k, v in list(names.items()) + list(aliases.items())
                             if t in k or k in t), None)
            status, ref = ("부분겹침", hit_name) if hit_name else ("신규", "")
        out.append({"term": t, "count": a["n"], "visitors": len(a["vis"]),
                    "hit_count": a["hit"], "status": status, "matched": ref or "",
                    "last_seen": a["last"].date().isoformat()})
    out.sort(key=lambda r: (-r["count"], -r["visitors"], r["term"]))

    print("\n%-20s %4s %4s %-12s %s" % ("검색어", "횟수", "방문", "판정", "겹친 품목"))
    for r in out[:args.limit]:
        print("%-20s %4d %4d %-12s %s"
              % (r["term"], r["count"], r["visitors"], r["status"], r["matched"]))

    fresh = [r for r in out if r["status"] == "신규"]
    print("\n신규 %d개 / 겹침 %d개." % (len(fresh), len(out) - len(fresh)))
    if fresh:
        print("신규만: %s" % ", ".join(r["term"] for r in fresh))
    print("겹치는 검색어가 0건을 냈으면 새 품목이 아니라 별칭이 빠진 것이다"
          " (판단 8번). aliases에 넣는 쪽을 먼저 본다.")

    if args.csv:
        path = args.csv if os.path.isabs(args.csv) else os.path.join(ROOT, args.csv)
        with io.open(path, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["term", "count", "visitors",
                                              "hit_count", "status", "matched",
                                              "last_seen"])
            w.writeheader()
            w.writerows(out)
        print("-> %s" % path)


if __name__ == "__main__":
    main()
