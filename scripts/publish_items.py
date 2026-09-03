# -*- coding: utf-8 -*-
"""본문이 준비된 품목을 items.json에 발행한다.

site/src/content/items/*.md 가 있는데 items.json에 없는 품목을 추가한다.
판정(verdict)은 아래 표로 명시한다 — 자동 추론하면 틀린 판정이 조용히 나간다.
"""
import csv
import io
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEMS = os.path.join(ROOT, "site", "src", "data", "items.json")
CONTENT = os.path.join(ROOT, "site", "src", "content", "items")
SEED = os.path.join(ROOT, "db", "seed", "items.csv")

# slug: (verdict, category, verdict_line, aliases)
VERDICTS = {
    "ibul": ("대형폐기물", "섬유류",
             "의류수거함에 넣으면 안 됩니다. 부피가 커서 대부분 대형폐기물입니다.", []),
    "huraipaen": ("조건부", "금속류",
                  "코팅 팬은 고철이 아닙니다. 통주물·스테인리스만 고철로 갑니다.", ["프라이팬"]),
    "yuri": ("일반쓰레기", "유리류",
             "판유리·거울·내열유리는 재활용이 안 됩니다. 불연성 마대로 갑니다.", []),
    "baeteori": ("전용수거함", "유해폐기물",
                 "일반쓰레기에 넣으면 안 됩니다. 폐건전지 전용수거함으로 갑니다.", []),
    "usan": ("조건부", "복합재질",
             "살대는 고철, 천은 일반쓰레기입니다. 분해해야 재활용됩니다.", []),
    "kaerieo": ("대형폐기물", "생활용품",
                "크기와 상관없이 대부분 대형폐기물 신고 대상입니다.", ["여행가방"]),
    "hwabun": ("조건부", "도자기류",
               "재질에 따라 갈립니다. 흙은 화분과 따로 버려야 합니다.", []),
    "geureut": ("일반쓰레기", "도자기류",
                "도자기·유리 식기는 재활용이 안 됩니다. 불연성 마대로 갑니다.", ["식기"]),
    "sinbal": ("조건부", "섬유류",
               "상태가 좋으면 의류수거함, 낡았으면 일반쓰레기입니다.", ["운동화"]),
    "chimdae": ("대형폐기물", "가구류",
                "프레임과 매트리스를 따로 신고해야 하는 지자체가 많습니다.", []),
    "begae": ("일반쓰레기", "섬유류",
              "의류수거함에 넣으면 안 됩니다. 종량제 봉투로 갑니다.", []),
    "naembi": ("재활용", "금속류",
               "스테인리스·양은은 고철입니다. 뚜껑 유리는 분리하세요.", []),
    "maeteuriseu": ("대형폐기물", "가구류",
                    "스프링이 있으면 처리비가 올라갑니다. 지자체별 금액 차가 큽니다.", []),
    "uija": ("대형폐기물", "가구류",
             "개수만큼 수수료가 붙습니다. 금속 프레임은 고철로 뺄 수 있습니다.", []),
    "subakkkeopjil": ("음식물", "음식물",
                      "음식물쓰레기가 맞습니다. 잘게 잘라 물기를 빼세요.", []),
    "geonjeonji": ("전용수거함", "유해폐기물",
                   "일반쓰레기에 넣으면 안 됩니다. 전용수거함이 따로 있습니다.", ["건전지"]),
    "sugeon": ("조건부", "섬유류",
               "깨끗하면 의류수거함, 오염됐으면 일반쓰레기입니다.", []),
    "sikyongyu": ("전용수거함", "유해폐기물",
                  "하수구에 버리면 안 됩니다. 폐식용유 수거함으로 갑니다.", ["폐식용유"]),
    # E-순환거버넌스가 안마의자만 '집밖 배출' 단서를 단다. 무상수거는 되지만
    # 다른 가전처럼 집 안까지 들어오지 않는다.
    "anmauija": ("무상수거", "폐전기·전자제품",
                 "폐가전 무상수거 대상이지만 집밖으로 내놓아야 가져갑니다.", []),
    "syopa": ("대형폐기물", "가구류",
              "인승 수만큼 수수료가 매겨집니다. 소파와 같은 품목입니다.", ["소파"]),
    "doma": ("일반쓰레기", "생활용품",
             "재질과 상관없이 대부분 종량제 봉투로 갑니다.", []),
    "somibul": ("대형폐기물", "섬유류",
                "솜 충전재라 의류수거함에 못 넣습니다. 부피가 큽니다.", []),
    # 중소형이라 1대 단독으로는 무상수거 신청이 안 된다. 5개 이상이어야 한다.
    "noteubuk": ("조건부", "폐전기·전자제품",
                 "중소형이라 1대만으로는 무상수거가 안 됩니다. 5개 이상부터입니다.", []),
    "bananakkeopjil": ("음식물", "음식물",
                       "음식물쓰레기가 맞습니다. 스티커는 떼세요.", []),
}


def main():
    items = json.load(io.open(ITEMS, encoding="utf-8"))
    have = {i["slug"] for i in items}
    seed = {r["slug"]: r for r in csv.DictReader(io.open(SEED, encoding="utf-8"))}
    written = {os.path.splitext(f)[0]
               for f in os.listdir(CONTENT) if f.endswith(".md")}

    added, skipped = [], []
    for slug in sorted(written - have):
        if slug not in VERDICTS:
            skipped.append((slug, "판정 미정"))
            continue
        s = seed.get(slug)
        if not s:
            skipped.append((slug, "시드에 없음"))
            continue
        verdict, category, line, aliases = VERDICTS[slug]
        try:
            vol = int(s["monthly_volume"] or 0) or None
        except ValueError:
            vol = None
        items.append({
            "slug": slug,
            "name": s["name"],
            "aliases": aliases,
            "verdict": verdict,
            "verdict_line": line,
            "category": category,
            "housing_split": s["housing_split"] == "true",
            "region_varies": s["region_varies"] == "true",
            "monthly_volume": vol,
            "competitor_has": s["competitor_has"] == "true",
            "published": True,
            "updated_at": "2026-09-03T00:00:00+00:00",
        })
        added.append(slug)

    items.sort(key=lambda i: -(i.get("monthly_volume") or 0))
    io.open(ITEMS, "w", encoding="utf-8").write(
        json.dumps(items, ensure_ascii=False, indent=2) + "\n")

    print("발행 %d개 추가 → 총 %d개" % (len(added), len(items)))
    for s in added:
        print("  + %s" % s)
    for s, why in skipped:
        print("  ! %s — %s" % (s, why))


if __name__ == "__main__":
    main()
