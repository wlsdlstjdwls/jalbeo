# -*- coding: utf-8 -*-
"""items 테이블을 읽어 site/src/data/items.json 스냅샷을 갱신한다.

site/scripts/pull-data.mjs는 PostgREST(SUPABASE_URL/ANON_KEY)를 쓰는데 이 환경엔
그 키가 없다. 대신 db_apply.py와 같은 세션 풀러로 붙어 같은 질의를 낸다.
정렬도 들여쓰기도 pull-data.mjs와 맞춘다
(monthly_volume desc nulls last, name asc / JSON.stringify indent 1).
"""
import json
import os
import sys

import psycopg2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db_apply import load_env  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "site", "src", "data", "items.json")

COLS = ["slug", "name", "aliases", "verdict", "verdict_line", "category",
        "housing_split", "region_varies", "monthly_volume", "competitor_has",
        "published", "updated_at"]

Q = """select %s from items where published = true
order by monthly_volume desc nulls last, name asc""" % ", ".join(COLS)


def main():
    env = load_env()
    conn = psycopg2.connect(
        host=env["SUPABASE_DB_HOST"], port=5432, dbname="postgres",
        user=env["SUPABASE_DB_USER"], password=env["SUPABASE_DB_PASSWORD"],
        connect_timeout=20, sslmode="require")
    with conn, conn.cursor() as cur:
        cur.execute(Q)
        rows = cur.fetchall()
    conn.close()

    out = []
    for r in rows:
        rec = dict(zip(COLS, r))
        rec["updated_at"] = rec["updated_at"].isoformat() if rec["updated_at"] else None
        out.append(rec)

    open(OUT, "w", encoding="utf-8").write(
        json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    nulls = sum(1 for r in out if r["monthly_volume"] is None)
    print("품목 %d개 (monthly_volume null %d개) -> %s" % (len(out), nulls, OUT))


if __name__ == "__main__":
    main()
