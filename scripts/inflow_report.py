# -*- coding: utf-8 -*-
"""검색엔진발 착지와 사이트 내 검색어 로그를 찍는다 (판단 99, docs/61).

세션 시작 때 돌린다. 문서에 적힌 마지막 숫자를 옮기지 말고 여기서 다시 잰다.
  python scripts/inflow_report.py [since=2026-09-08]
"""
import sys

import psycopg2

from db_apply import load_env

ENGINES = ("google", "naver", "bing", "daum", "yandex")


def main():
    since = sys.argv[1] if len(sys.argv) > 1 else "2026-09-08"
    sys.stdout.reconfigure(encoding="utf-8")
    env = load_env()
    conn = psycopg2.connect(
        host=env["SUPABASE_DB_HOST"], port=5432, dbname="postgres",
        user=env["SUPABASE_DB_USER"], password=env["SUPABASE_DB_PASSWORD"],
        connect_timeout=20, sslmode="require")
    engine = " or ".join("referrer_host like '%%%%%s%%%%'" % e for e in ENGINES)
    with conn.cursor() as cur:
        cur.execute(
            "select (created_at at time zone 'Asia/Seoul')::date, count(*) from page_views"
            " where created_at >= %s and path <> '/' and (" + engine + ")"
            " group by 1 order by 1", (since,))
        rows = cur.fetchall()
        print("품목/가이드 검색 착지 %d건" % sum(n for _, n in rows))
        for d, n in rows:
            print("  %s  %d" % (d, n))

        cur.execute(
            "select path, count(*) from page_views"
            " where created_at >= %s and path <> '/' and (" + engine + ")"
            " group by 1 order by 2 desc", (since,))
        print("\n페이지별")
        for p, n in cur.fetchall():
            print("  %3d  %s" % (n, p))

        cur.execute(
            "select (created_at at time zone 'Asia/Seoul')::date, term, hit_count"
            " from search_queries where created_at >= %s order by created_at", (since,))
        rows = cur.fetchall()
        print("\n사이트 내 검색 %d건 (hit_count = 0은 찍힌 시점 값, 판단 71)" % len(rows))
        for d, t, h in rows:
            print("  %s  %-20s %d" % (d, t, h))
    conn.close()


if __name__ == "__main__":
    main()
