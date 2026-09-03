# -*- coding: utf-8 -*-
"""db/apply.sql 을 Supabase에 적용한다.

직접 접속(db.<ref>.supabase.co)은 IPv6 전용이라 이 환경에서 안 되고,
세션 풀러(aws-0-ap-northeast-2.pooler.supabase.com:5432)로 붙는다.
자격증명은 site/.env 에서 읽는다 (git 제외).
"""
import os
import sys

import psycopg2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQL = os.path.join(ROOT, "db", "apply.sql")
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
    env = load_env()
    missing = [k for k in ("SUPABASE_DB_HOST", "SUPABASE_DB_USER", "SUPABASE_DB_PASSWORD")
               if not env.get(k)]
    if missing:
        sys.exit("site/.env 에 없음: %s" % ", ".join(missing))

    sql = open(SQL, encoding="utf-8").read()
    conn = psycopg2.connect(
        host=env["SUPABASE_DB_HOST"], port=5432, dbname="postgres",
        user=env["SUPABASE_DB_USER"], password=env["SUPABASE_DB_PASSWORD"],
        connect_timeout=20, sslmode="require")
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
        with conn.cursor() as cur:
            for table in ("items", "regions", "item_region_rules",
                          "bulky_fees", "guideline_verdicts"):
                cur.execute("select count(*) from %s" % table)
                print("  %-22s %s행" % (table, cur.fetchone()[0]))
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    print("\napply.sql 적용 완료")


if __name__ == "__main__":
    main()
