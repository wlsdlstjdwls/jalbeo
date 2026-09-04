# -*- coding: utf-8 -*-
"""실측 2/3/4차를 한 자로 합쳐 items.monthly_volume 갱신 SQL을 만든다.

`docs/14`가 남긴 숙제의 마무리다. 1차는 연관어 덤프라 어미 커버리지가 품목마다
달랐다. 4차가 1차 품목을 2차와 같은 두 어미로 다시 쟀으므로, 이제 154개 전부를
`{품목}버리는법` + `{품목}분리수거` 한 자로 정렬할 수 있다.

우선순위: 4차 > 3차 > 2차 (같은 어미가 여러 회차에 있으면 최신 회차를 쓴다)
안 걸린 어미는 0이 아니라 빈칸이다. 두 어미가 다 빈칸이면 그 품목은 건너뛴다.

출력:
  data/keywords/volumes-merged.csv
  db/publish_volumes_4.sql
"""
import csv
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KW = os.path.join(ROOT, "data", "keywords")
ITEMS = os.path.join(ROOT, "site", "src", "data", "items.json")
OUT_CSV = os.path.join(KW, "volumes-merged.csv")
OUT_SQL = os.path.join(ROOT, "db", "publish_volumes_4.sql")

SUFFIXES = ["버리는법", "분리수거"]


def read_csv(path):
    with open(path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def main():
    items = json.load(open(ITEMS, encoding="utf-8"))
    by_slug = {it["slug"]: it for it in items}
    by_name = {it["name"]: it for it in items}

    # 회차별 {slug: {어미: 값}}. 나중 회차가 앞 회차를 덮는다
    rounds = []
    r2 = {}
    for r in read_csv(os.path.join(KW, "gate1-volumes-2.csv")):
        r2[r["slug"]] = {s: r[s] for s in SUFFIXES}
    rounds.append(("2차", r2))

    r3 = {}
    for r in read_csv(os.path.join(KW, "gate1-volumes-3.csv")):
        it = by_name.get(r["item"])
        if it:
            r3[it["slug"]] = {s: r[s] for s in SUFFIXES}
    rounds.append(("3차", r3))

    r4 = {}
    for r in read_csv(os.path.join(KW, "gate1-volumes-4.csv")):
        r4[r["slug"]] = {s: r[s] for s in SUFFIXES}
    rounds.append(("4차", r4))

    merged = []
    for it in items:
        rec = {"slug": it["slug"], "name": it["name"], "source": ""}
        srcs = []
        total = 0
        hit = False
        for suf in SUFFIXES:
            val, src = "", ""
            for label, table in rounds:
                v = table.get(it["slug"], {}).get(suf, "")
                if v != "":
                    val, src = int(v), label
            rec[suf] = val
            if val != "":
                total += val
                hit = True
                srcs.append("%s %s" % (suf, src))
        if not hit:
            continue
        rec["total"] = total
        rec["source"] = " / ".join(srcs)
        rec["half"] = 1 if "" in (rec[SUFFIXES[0]], rec[SUFFIXES[1]]) else 0
        merged.append(rec)

    merged.sort(key=lambda r: -r["total"])
    with open(OUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["slug", "name"] + SUFFIXES
                           + ["total", "half", "source"])
        w.writeheader()
        w.writerows(merged)

    fmt = lambda v: "-" if v == "" else str(v)
    lines = [
        "-- 실측 2/3/4차를 한 자로 합쳐 items.monthly_volume을 갱신한다 (2026-09-04).",
        "-- 근거: data/keywords/volumes-merged.csv (scripts/merge_volumes.py 산출)",
        "--",
        "-- monthly_volume은 '{품목}버리는법' + '{품목}분리수거' 두 어미의 합이다.",
        "-- 1차(gate1-volumes.csv)는 연관어 덤프라 어미 커버리지가 품목마다 달랐다.",
        "-- 4차가 1차 품목 94개를 2차와 같은 자로 다시 쟀으므로 그 값으로 덮는다.",
        "-- 두 어미 중 한쪽만 걸린 품목은 걸린 쪽만 더한 값이다 (없는 숫자는 안 만든다).",
        "",
        "update items set monthly_volume = v.n, updated_at = now()",
        "from (values",
    ]
    for i, r in enumerate(merged):
        tail = "," if i < len(merged) - 1 else ""
        lines.append("  ('%s',%d)%s  -- %s  버리는법 %s / 분리수거 %s"
                     % (r["slug"], r["total"], tail, r["name"],
                        fmt(r["버리는법"]), fmt(r["분리수거"])))
    lines += [
        ") as v(slug, n)",
        "where items.slug = v.slug;",
        "",
    ]
    open(OUT_SQL, "w", encoding="utf-8").write("\n".join(lines))

    half = [r["name"] for r in merged if r["half"]]
    covered = {r["slug"] for r in merged}
    missing = [it["name"] for it in items if it["slug"] not in covered]
    print("품목 %d / %d 측정, 합계 %s"
          % (len(merged), len(items), format(sum(r["total"] for r in merged), ",")))
    print("어미 한쪽만 걸린 품목 %d개: %s" % (len(half), ", ".join(half)))
    print("미측정 %d개: %s" % (len(missing), ", ".join(missing)))
    print("\n%-14s %9s %9s %9s" % ("품목", "버리는법", "분리수거", "합계"))
    for r in merged[:20]:
        print("%-14s %9s %9s %9s"
              % (r["name"][:14], fmt(r["버리는법"]), fmt(r["분리수거"]),
                 format(r["total"], ",")))
    print("\n-> %s\n-> %s" % (OUT_CSV, OUT_SQL))


if __name__ == "__main__":
    main()
