# -*- coding: utf-8 -*-
"""보관 기간이 지난 로그를 지운다 (db/migrations/0009).

페이지뷰 12개월, 검색어 24개월. 숫자는 SQL 함수 안에 있고 여기서는 부르기만
한다 - 두 군데에 적으면 갈린다. 개인정보처리방침(/privacy)이 이 기간을 약속한다.

pg_cron 이 붙어 있으면 매달 자동으로 도는 것과 같은 함수다. 이 스크립트는
pg_cron 을 못 쓰는 경우와, 지금 당장 확인하고 싶을 때 쓴다.

    python scripts/purge_logs.py         # 지운다
    python scripts/purge_logs.py --dry   # 지울 행 수만 센다
"""
import os
import sys

import psycopg2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV = os.path.join(ROOT, "site", ".env")


def load_env():
    out = {}
    with open(ENV, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                out[k.strip()] = v.strip()
    return out


def main():
    dry = "--dry" in sys.argv
    env = load_env()
    missing = [k for k in ("SUPABASE_DB_HOST", "SUPABASE_DB_USER", "SUPABASE_DB_PASSWORD")
               if not env.get(k)]
    if missing:
        sys.exit("site/.env 에 없음: %s" % ", ".join(missing))

    conn = psycopg2.connect(
        host=env["SUPABASE_DB_HOST"], port=5432, dbname="postgres",
        user=env["SUPABASE_DB_USER"], password=env["SUPABASE_DB_PASSWORD"],
        connect_timeout=20, sslmode="require")
    try:
        with conn.cursor() as cur:
            if dry:
                cur.execute("""
                    select (select count(*) from page_views
                              where created_at < now() - interval '12 months'),
                           (select count(*) from search_queries
                              where created_at < now() - interval '24 months')
                """)
                pv, sq = cur.fetchone()
                print("지울 대상  page_views %s행, search_queries %s행 (--dry)" % (pv, sq))
                return
            cur.execute("select * from public.purge_old_logs()")
            pv, sq = cur.fetchone()
            conn.commit()
            print("지움  page_views %s행, search_queries %s행" % (pv, sq))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
