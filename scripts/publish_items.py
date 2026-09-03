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
    # ── batch5~8 (2차 확장) ───────────────────────────────────────
    "gabang": ("조건부", "섬유류",
               "바퀴가 달렸는지, 크기가 얼마나 되는지로 경로가 갈립니다.", ["백팩"]),
    "keompyuteo": ("무상수거", "폐전기·전자제품",
                   "폐가전 무상수거 대상입니다. 저장장치부터 처리하세요.", ["데스크톱"]),
    "gireum": ("전용수거함", "유해폐기물",
               "튀김 기름과 엔진오일은 경로가 완전히 다릅니다.", ["폐유"]),
    "seutiropom": ("조건부", "발포수지류",
                   "흰색이고 깨끗한 것만 재활용됩니다. 하나라도 어긋나면 종량제입니다.", []),
    "sopa": ("대형폐기물", "가구류",
             "인승 수만큼 수수료가 붙습니다. 버리기 전에 값이 붙는지 보세요.", ["쇼파"]),
    "jangnangam": ("조건부", "플라스틱류",
                   "플라스틱 완구는 2026년부터 재활용 대상입니다. 봉제·복합재질은 종량제입니다.", ["완구"]),
    "naengjanggo": ("무상수거", "폐전기·전자제품",
                    "대형가전이라 한 대만으로도 무상방문수거가 됩니다.", []),
    "heonot": ("재활용", "섬유류",
               "의류수거함으로 갑니다. 다만 아무 섬유나 받지는 않습니다.", ["헌 옷"]),
    "geoul": ("일반쓰레기", "유리류",
              "뒷면에 금속을 입힌 판유리라 유리병 수거함에 넣으면 안 됩니다.", []),
    "chaeksang": ("대형폐기물", "가구류",
                  "지자체마다 나누는 축이 달라 항목 고르기가 더 어렵습니다.", []),
    "hwajangpum": ("조건부", "복합재질",
                   "한 용기가 서너 재질입니다. 뜯어야 재활용됩니다.", ["화장품 용기"]),
    "hyangsu": ("조건부", "복합재질",
                "두꺼운 유리·금속 펌프·남은 알코올이 각각 다른 곳으로 갑니다.", ["향수병"]),
    "gimchi": ("음식물", "음식물",
               "음식물쓰레기가 맞습니다. 헹구라는 안내는 지자체마다 갈립니다.", []),
    # 뼈는 사료화가 안 돼 음식물 기준에서 빠진다. 가장 흔한 오해 지점이다.
    "chikinppyeo": ("일반쓰레기", "음식물",
                    "음식물쓰레기가 아닙니다. 뼈는 기준에서 빠져 종량제봉투로 갑니다.", ["닭뼈"]),
    "jangpan": ("대형폐기물", "생활용품",
                "값을 개수가 아니라 면적이나 길이로 매깁니다.", []),
    "moniteo": ("조건부", "폐전기·전자제품",
                "크기에 따라 갈립니다. 작은 모니터 한 대만으로는 안 됩니다.", []),
    "onsumaeteu": ("대형폐기물", "폐전기·전자제품",
                   "본체와 매트가 한 벌이라 대형폐기물로 신고하는 쪽이 빠릅니다.", []),
    "otjang": ("대형폐기물", "가구류",
               "신고 화면에서는 대개 '장롱' 항목으로 접수합니다. 쪽수로 값이 갈립니다.", []),
    "jangnong": ("대형폐기물", "가구류",
                 "'장롱'의 흔한 오기지만 지자체 요금표에 이 표기가 실제로 쓰입니다.", []),
    "otgeoli": ("조건부", "복합재질",
                "철사는 고철, 플라스틱은 종량제입니다. 훈령이 재활용에서 뺀 품목입니다.", []),
    # E-순환거버넌스 목록에 없고 '침대형 전기제품'은 수거 불가로 적혀 있다.
    "jeongijangpan": ("대형폐기물", "폐전기·전자제품",
                      "폐가전 수거품목에 없습니다. 대형폐기물 경로가 확실합니다.", []),
    "setakgi": ("무상수거", "폐전기·전자제품",
                "대형이라 한 대만 있어도 무상방문수거 신청이 됩니다.", []),
    "hyudaepon": ("전용수거함", "폐전기·전자제품",
                  "대형폐기물이 아닙니다. 전용 수거함에 넣으면 끝입니다.", ["핸드폰"]),
    "byeongi": ("대형폐기물", "도자기류",
                "도기라 재활용 경로가 없습니다. 대형폐기물 신고뿐입니다.", ["양변기"]),
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
