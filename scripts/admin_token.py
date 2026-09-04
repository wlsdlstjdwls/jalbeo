# -*- coding: utf-8 -*-
"""관리자 대시보드(/admin/) 토큰을 발급, 조회, 폐기한다.

이 사이트에는 로그인이 없다. 토큰이 곧 열쇠다 (`docs/17`).
토큰은 DB의 admin_tokens에만 있고 저장소에는 남기지 않는다.

    python scripts/admin_token.py issue                   무작위 32자로 발급
    python scripts/admin_token.py issue --key <내가 정한 키>  외우기 쉬운 키로 발급
    python scripts/admin_token.py issue --label phone        라벨 따로 두기
    python scripts/admin_token.py list                   발급 목록 (앞 6자만)
    python scripts/admin_token.py revoke <라벨>          해당 라벨 폐기

무작위 키는 이 출력에서만 볼 수 있다. 잃어버리면 다시 issue 한다.
직접 정한 키는 짧으면 찍힌다. 12자 이상만 받는다.

한 번 열면 브라우저가 키를 기억하므로(localStorage) 그 다음부터는 /admin 만
쳐도 열린다. 지우려면 화면 상단의 '키 지우기'를 누른다.
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


MIN_LEN = 12


def issue(label, key=None):
    if key is None:
        token = secrets.token_urlsafe(24)
    else:
        if len(key) < MIN_LEN:
            sys.exit("키가 짧다. %d자 이상으로 정한다 (지금 %d자)." % (MIN_LEN, len(key)))
        token = key
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
        label, key = "owner", None
        rest = args[1:]
        while rest:
            if rest[0] == "--key" and len(rest) > 1:
                key, rest = rest[1], rest[2:]
            elif rest[0] == "--label" and len(rest) > 1:
                label, rest = rest[1], rest[2:]
            else:  # 옛 사용법: issue <라벨>
                label, rest = rest[0], rest[1:]
        issue(label, key)
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
