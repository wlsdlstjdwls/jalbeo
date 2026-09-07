# -*- coding: utf-8 -*-
"""환경부 훈령 별표1 -> 품목별 분리배출 판정 데이터.

입력: data/raw/guidelines/...분리수거대상-재활용가능자원의-품목-및-분리배출요령.pdf
출력: data/guidelines/disposal-rules.json  (셀 단위 구조화 원문)
      data/guidelines/item-verdicts.csv    (품목명 -> O·X 룩업)

표 괘선에서 행 경계를, x좌표에서 열을 잡아 셀 단위로 읽는다.
'해당품목'은 그 분류로 배출 가능(O), '비해당품목'은 불가(X)다.
"""
import csv
import json
import os
import re

import fitz

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data", "raw", "guidelines",
                   "재활용가능자원의-분리수거-등에-관한-지침"
                   "_별표0001_분리수거대상-재활용가능자원의-품목-및-분리배출요령.pdf")
OUTDIR = os.path.join(ROOT, "data", "guidelines")
SOURCE = {
    "rule": "재활용가능자원의 분리수거 등에 관한 지침 [별표1]",
    "kind": "기후에너지환경부 훈령 제18호",
    "issued": "2026-01-01",
    "source_url": "https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON",
    "collected_at": "2026-09-03",
    "parsed_sections": "1(품목별 배출)만 파싱. 섹션 2(통합배출)·3(기타)은 "
                       "표 구조가 달라 원본 PDF/HWP로만 보관",
}

# 섹션 2(통합배출)는 열 구성이 달라 제외한다
# 섹션 1만 파싱한다. 섹션 2(통합배출)는 4열, 섹션 3(기타)은 열 좌표가 달라
# 자동 파싱이 깨진다 — 원본 PDF·HWP로 보관하고 필요 시 수동 정리한다.
PAGES = {0: "1. 품목별 배출", 1: "1. 품목별 배출", 2: "1. 품목별 배출",
         3: "1. 품목별 배출", 4: "1. 품목별 배출"}
COL_B, COL_C = 150, 300
HEADERS = {"품목", "세부품목", "배출요령", "배", "출", "요", "령"}
CATEGORY = re.compile(r"^[가-힣]\.\s*")


def row_bounds(page):
    """표 가로 괘선 y좌표 -> 행 경계."""
    ys = set()
    for drawing in page.get_drawings():
        for item in drawing["items"]:
            if item[0] == "l":
                (x0, y0), (x1, y1) = item[1], item[2]
                if abs(y0 - y1) < 1.5 and abs(x1 - x0) > 200:
                    ys.add(round(y0))
            elif item[0] == "re":
                rect = item[1]
                if rect.height < 2 and rect.width > 200:
                    ys.add(round(rect.y0))
    return sorted(ys)


def cells(page):
    """[(행번호, 열번호, 텍스트)] — 괘선 사이 밴드로 행을, x로 열을 나눈다."""
    bounds = row_bounds(page)
    if len(bounds) < 2:
        return []
    buckets = {}
    for x0, y0, x1, y1, word, *_ in page.get_text("words"):
        mid = (y0 + y1) / 2
        row = None
        for i in range(len(bounds) - 1):
            if bounds[i] <= mid < bounds[i + 1]:
                row = i
                break
        if row is None:
            continue
        col = 0 if x0 < COL_B else (1 if x0 < COL_C else 2)
        buckets.setdefault((row, col), []).append((round(y0), x0, word))
    out = []
    for (row, col) in sorted(buckets):
        words = sorted(buckets[(row, col)])
        text = " ".join(w for _, _, w in words)
        text = re.sub(r"\s+", " ", text).strip()
        if text and text not in HEADERS:
            out.append((row, col, text))
    return out


def split_rules(blob):
    """배출요령 셀 -> '-' 불릿과 '※' 주석으로 분해."""
    blob = re.sub(r"\s*([-※])\s*", r"\n\1", blob)
    rules, notes = [], []
    for part in blob.split("\n"):
        part = part.strip()
        if part.startswith("-"):
            rules.append(part.lstrip("-").strip())
        elif part.startswith("※"):
            notes.append(part.lstrip("※").strip())
        elif part and rules:
            rules[-1] += part
    return rules, notes


VERBISH = re.compile(r"(배출|반납|제거|사용|해야|하여|되지|않는|경우|따라|한후|이외|부착)")
ROUTES = ("종량제봉투", "특수규격마대", "대형폐기물", "대형페기물", "불연성마대", "지자체조례")
TAILS = (
    re.compile(r"^(.{2,12}?)등(?:은|는)?(?:%s)" % "|".join(ROUTES)),  # 배출 경로로 끝남
    re.compile(r"^(.{2,10}?)등(?=.*해당하지)"),                        # 포괄 정의로 끝남
)


def is_route(text):
    return any(r in text for r in ROUTES)


def tail_item(text):
    for pat in TAILS:
        m = pat.match(text)
        if m:
            return m.group(1)
    return None


def split_items(blob):
    blob = re.sub(r"\([^)]*\)", "", blob)
    parts = [p.strip() for p in re.split(r"[,、]", blob)]
    if len(parts) == 1 and len(parts[0]) > 20:
        return []
    out = []
    for p in parts:
        p = re.sub(r"^(및|또는)\s*", "", p).strip().rstrip("등").strip()
        p = re.sub(r"\s+", "", p)
        # 목록의 마지막 품목에는 꼬리말이 붙어서 온다. "사기·도자기류 등은
        # 특수규격마대…"처럼 배출 경로로 끝나거나, "멀티탭등대형전기·전자
        # 제품에해당하지않는…"처럼 포괄 정의로 끝난다. 통째로는 서술문이라
        # 걸러지므로 '등' 앞의 명사만 떼어 살린다.
        tail = tail_item(p)
        if tail and not VERBISH.search(tail) and not is_route(tail):
            out.append(tail)
        elif is_route(p):
            continue  # 배출 경로 문구는 품목이 아니다
        elif 1 < len(p) <= 20 and not VERBISH.search(p):
            out.append(p)
    return out


def parse():
    doc = fitz.open(SRC)
    records = []
    for pno, page in enumerate(doc):
        if pno not in PAGES:
            continue
        grid = {}
        for row, col, text in cells(page):
            grid.setdefault(row, {})[col] = text
        # 대분류 셀은 여러 행에 걸쳐 있어 조각으로 잡힌다. 마커('가.') 기준으로 묶는다.
        order = sorted(grid)
        segs, cur_rows, cur_text = [], [], []
        for row in order:
            raw = grid[row].get(0, "")
            if raw and re.match(r"^(비고|\d+\.)", raw):
                raw = ""
            if raw and CATEGORY.match(raw):
                if cur_rows:
                    segs.append((cur_rows, " ".join(cur_text)))
                cur_rows, cur_text = [], [CATEGORY.sub("", raw).strip()]
            elif raw:
                cur_text.append(raw.strip())
            cur_rows.append(row)
        if cur_rows:
            segs.append((cur_rows, " ".join(cur_text)))
        cat_of = {}
        for rows_, text in segs:
            for row in rows_:
                cat_of[row] = re.sub(r"\s+", " ", text).strip()

        for row in order:
            cell = grid[row]
            subitem = cell.get(1, "").lstrip("·").strip()
            if not subitem:
                # 세부품목 칸이 빈 채 배출요령만 있는 행은 앞 페이지 마지막
                # 셀의 이어짐이다. 대형 전기·전자제품 해당품목 예시가 4쪽
                # 끝에서 잘려 5쪽 첫 행으로 넘어간다 — 버리면 러닝머신부터
                # 데스크탑PC세트까지 12개가 통째로 사라진다.
                tail = cell.get(2, "").strip()
                if tail and records and not cell.get(0, "").strip():
                    fill(records[-1], records[-1]["_raw"] + " " + tail)
                continue
            cat = cat_of.get(row, "") or (records[-1]["category"] if records else "")
            rec = {"section": PAGES[pno], "page": pno + 1,
                   "category": cat,
                   "subitem": re.sub(r"\s+", " ", subitem),
                   "rules": [], "includes": [], "excludes": [], "notes": []}
            fill(rec, cell.get(2, ""))
            records.append(rec)
    for rec in records:
        rec.pop("_raw", None)
    return records


def fill(rec, raw):
    """배출요령 셀 원문 -> rules/includes/excludes/notes. 이어짐이 붙으면 다시 부른다."""
    rec["_raw"] = raw
    rules, notes = split_rules(raw)
    rec["rules"] = rules
    rec["includes"], rec["excludes"], rec["notes"] = [], [], []
    for n in notes:
        m = re.match(r"(비해당품목|해당품목예시|해당품목)\s*[::]\s*(.+)", n.replace(" ", ""))
        if m:
            key = "excludes" if m.group(1).startswith("비") else "includes"
            rec[key].extend(split_items(m.group(2)))
        else:
            rec["notes"].append(n)


def main():
    records = parse()
    with open(os.path.join(OUTDIR, "disposal-rules.json"), "w", encoding="utf-8") as f:
        json.dump({"source": SOURCE, "records": records}, f, ensure_ascii=False, indent=2)

    rows = []
    for r in records:
        for name in r["includes"]:
            rows.append({"item": name, "verdict": "O", "category": r["category"],
                         "subitem": r["subitem"], "basis": "해당품목"})
        for name in r["excludes"]:
            rows.append({"item": name, "verdict": "X", "category": r["category"],
                         "subitem": r["subitem"], "basis": "비해당품목"})

    # PDF 재추출 시 좌표가 미세하게 흔들리면 행 순서가 바뀔 수 있다. 내용이
    # 같아도 매번 diff가 나서 최신성 체크가 오탐하므로 출력 직전 정렬로 고정한다.
    rows.sort(key=lambda r: (r["category"], r["subitem"], r["verdict"], r["item"]))

    with open(os.path.join(OUTDIR, "item-verdicts.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["item", "verdict", "category", "subitem", "basis"])
        w.writeheader()
        w.writerows(rows)

    print("레코드 %d개 / 판정 %d건 (O %d, X %d)" % (
        len(records), len(rows),
        sum(1 for r in rows if r["verdict"] == "O"),
        sum(1 for r in rows if r["verdict"] == "X")))
    print("대분류 %d개: %s" % (
        len({r["category"] for r in records}),
        " / ".join(sorted({r["category"] for r in records}))))


if __name__ == "__main__":
    main()
