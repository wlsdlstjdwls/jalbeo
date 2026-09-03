# -*- coding: utf-8 -*-
"""마이그레이션 + 시드를 SQL Editor 붙여넣기용 파일 하나로 합친다.

DB 비밀번호 없이 Supabase 대시보드 SQL Editor만으로 초기화할 수 있게 한다.
출력: db/apply.sql
"""
import csv
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIG = os.path.join(ROOT, "db", "migrations", "0001_init.sql")
SEED = os.path.join(ROOT, "db", "seed")
OUT = os.path.join(ROOT, "db", "apply.sql")


def q(v):
    """SQL 리터럴. None/빈값은 null."""
    if v is None or v == "":
        return "null"
    return "'" + str(v).replace("'", "''") + "'"


def boolean(v):
    return "true" if str(v).lower() == "true" else "false"


def main():
    parts = ["-- 잘버려 초기화 — Supabase SQL Editor에 통째로 붙여넣고 실행\n",
             "-- 생성: scripts/build_db_sql.py (재실행 안전 — upsert)\n\n",
             open(MIG, encoding="utf-8").read(), "\n\n"]

    with open(os.path.join(SEED, "items.csv"), encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    parts.append("-- 품목 %d개 (게이트 1 실측 검색량 있는 것만, 집필 전이라 published=false)\n"
                 % len(rows))
    parts.append("insert into items "
                 "(slug, name, monthly_volume, region_varies, competitor_has, "
                 "housing_split, published) values\n")
    parts.append(",\n".join(
        "  (%s, %s, %s, %s, %s, %s, %s)" % (
            q(r["slug"]), q(r["name"]), r["monthly_volume"] or "null",
            boolean(r["region_varies"]), boolean(r["competitor_has"]),
            boolean(r["housing_split"]), boolean(r["published"]))
        for r in rows))
    parts.append("\non conflict (slug) do update set\n"
                 "  name = excluded.name,\n"
                 "  monthly_volume = excluded.monthly_volume,\n"
                 "  region_varies = excluded.region_varies,\n"
                 "  competitor_has = excluded.competitor_has,\n"
                 "  updated_at = now();\n\n")

    with open(os.path.join(SEED, "guideline_verdicts.csv"), encoding="utf-8") as f:
        gv = list(csv.DictReader(f))
    parts.append("-- 환경부 훈령 별표1 판정 %d건 (docs/08)\n" % len(gv))
    parts.append("insert into guideline_verdicts "
                 "(item_name, verdict, category, subitem, basis, source_url, as_of) values\n")
    parts.append(",\n".join(
        "  (%s, %s, %s, %s, %s, %s, %s::date)" % (
            q(r["item_name"]), q(r["verdict"]), q(r["category"]), q(r["subitem"]),
            q(r["basis"]), q(r["source_url"]), q(r["as_of"]))
        for r in gv))
    parts.append("\non conflict do nothing;\n")

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("".join(parts))

    print("-> db/apply.sql  (품목 %d, 별표1 판정 %d, %d줄)"
          % (len(rows), len(gv), open(OUT, encoding="utf-8").read().count("\n")))


if __name__ == "__main__":
    main()
