# -*- coding: utf-8 -*-
"""관리자 대시보드(/admin/) 토큰을 발급, 조회, 폐기한다.

이 사이트에는 로그인이 없다. 토큰이 곧 열쇠다 (`docs/17`).
토큰은 DB의 admin_tokens에만 있고 저장소에는 남기지 않는다.

    python scripts/admin_token.py issue [라벨]   새 토큰 발급 후 접속 주소 출력
    python scripts/admin_token.py list           발급된 토큰 목록 (앞 6자만)
    python scripts/admin_token.py revoke <라벨>  해당 라벨의 토큰 폐기

발급된 값은 이 출력에서만 볼 수 있다. 어디에도 안 적어 두므로 잃어버리면
revoke 하고 다시 issue 한다.
"""
import os
import secrets
import sys

import psycopg2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db_apply import load_env  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SITE = os.environ.get("SITE_URL", "https://jalbeo.com")


def connect():
    env = load_env()
    return psycopg2.connect(
        host=env["SUPABASE_DB_HOST"], port=5432, dbname="postgres",
        user=env["SUPABASE_DB_USER"], password=env["SUPABASE_DB_PASSWORD"],
        connect_timeout=20, sslmode="require")


def issue(label):
    token = secrets.token_urlsafe(24)
    conn = connect()
    with conn, conn.cursor() as cur:
        cur.execute("delete from admin_tokens where label = %s", (label,))
        replaced = cur.rowcount
        cur.execute("insert into admin_tokens (token, label) values (%s, %s)",
                    (token, label))
    conn.close()
    if replaced:
        print("라벨 '%s'의 기존 토큰 %d개를 지웠다." % (label, replaced))
    print("발급 완료. 이 주소가 곧 열쇠다:\n")
    print("  %s/admin/?k=%s\n" % (SITE.rstrip("/"), token))
    print("이 출력 말고는 어디에도 없다. 잃어버리면 다시 발급한다.")


def listing():
    conn = connect()
    with conn, conn.cursor() as cur:
        cur.execute("select label, left(token, 6), created_at from admin_tokens "
                    "order by created_at")
        rows = cur.fetchall()
    conn.close()
    if not rows:
        print("발급된 토큰이 없다.")
        return
    print("%-16s %-10s %s" % ("라벨", "앞 6자", "발급일"))
    for label, head, created in rows:
        print("%-16s %-10s %s" % (label or "-", head + "...", created.date()))


def revoke(label):
    conn = connect()
    with conn, conn.cursor() as cur:
        cur.execute("delete from admin_tokens where label = %s", (label,))
        n = cur.rowcount
    conn.close()
    print("폐기 %d개 (라벨 '%s')" % (n, label))


def main():
    args = sys.argv[1:]
    cmd = args[0] if args else ""
    if cmd == "issue":
        issue(args[1] if len(args) > 1 else "owner")
    elif cmd == "list":
        listing()
    elif cmd == "revoke":
        if len(args) < 2:
            sys.exit("라벨이 필요하다: python scripts/admin_token.py revoke <라벨>")
        revoke(args[1])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
