# -*- coding: utf-8 -*-
"""관리자 대시보드(/admin/)에 들어갈 수 있는 이메일 명단을 관리한다.

로그인 자체는 Supabase Auth가 한다. 이 스크립트는 "누가 관리자인가"만 정한다.
계정(이메일 + 비밀번호)은 Supabase 대시보드에서 만든다 - 비밀번호는 여기를
지나가지 않는다.

    python scripts/admin_admins.py list                 명단 보기
    python scripts/admin_admins.py add <이메일> [라벨]   명단에 넣기
    python scripts/admin_admins.py remove <이메일>       명단에서 빼기

명단에 있는 이메일로 로그인해야 통계 RPC가 답한다 (`db/migrations/0005`).
명단에 넣는 것과 계정을 만드는 것은 별개다. 순서는 상관없다.
"""
import os
import sys

import psycopg2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db_apply import load_env  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def connect():
    env = load_env()
    return psycopg2.connect(
        host=env["SUPABASE_DB_HOST"], port=5432, dbname="postgres",
        user=env["SUPABASE_DB_USER"], password=env["SUPABASE_DB_PASSWORD"],
        connect_timeout=20, sslmode="require")


def listing():
    conn = connect()
    with conn, conn.cursor() as cur:
        cur.execute("select a.email, a.label, a.created_at, "
                    "       exists(select 1 from auth.users u where lower(u.email) = a.email) "
                    "from admins a order by a.created_at")
        rows = cur.fetchall()
    conn.close()
    if not rows:
        print("명단이 비었다. add 로 넣는다.")
        return
    print("%-34s %-10s %-12s %s" % ("이메일", "라벨", "등록일", "계정"))
    for email, label, created, has_user in rows:
        print("%-34s %-10s %-12s %s"
              % (email, label or "-", created.date(),
                 "있음" if has_user else "아직 없음 (대시보드에서 생성)"))


def add(email, label):
    email = email.strip().lower()
    conn = connect()
    with conn, conn.cursor() as cur:
        cur.execute("insert into admins (email, label) values (%s, %s) "
                    "on conflict (email) do update set label = excluded.label",
                    (email, label))
        cur.execute("select exists(select 1 from auth.users u where lower(u.email) = %s)",
                    (email,))
        has_user = cur.fetchone()[0]
    conn.close()
    print("명단에 넣었다: %s" % email)
    if not has_user:
        print("\n아직 이 이메일로 된 계정이 없다. Supabase 대시보드에서 만든다:")
        print("  Authentication > Users > Add user")
        print("  이메일 %s, 비밀번호는 직접 정하고 'Auto Confirm User'를 켠다." % email)


def remove(email):
    email = email.strip().lower()
    conn = connect()
    with conn, conn.cursor() as cur:
        cur.execute("delete from admins where email = %s", (email,))
        n = cur.rowcount
    conn.close()
    print("명단에서 뺐다: %d개 (%s)" % (n, email))
    if n:
        print("계정 자체는 남아 있다. 지우려면 Supabase 대시보드에서 지운다.")


def main():
    args = sys.argv[1:]
    cmd = args[0] if args else ""
    if cmd == "list":
        listing()
    elif cmd == "add":
        if len(args) < 2:
            sys.exit("이메일이 필요하다: python scripts/admin_admins.py add <이메일>")
        add(args[1], args[2] if len(args) > 2 else None)
    elif cmd == "remove":
        if len(args) < 2:
            sys.exit("이메일이 필요하다: python scripts/admin_admins.py remove <이메일>")
        remove(args[1])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
