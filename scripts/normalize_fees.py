# -*- coding: utf-8 -*-
"""대형폐기물 수수료 원본 CSV를 단일 스키마로 정규화.

입력: data/raw/fees/*.csv + manifest.json (fetch_fee_datasets.py 산출물)
출력: data/processed/fees.csv, data/processed/fees_report.json

지자체마다 컬럼명이 다르고 인코딩도 UTF-8·EUC-KR이 섞여 있다. 별칭 표로 흡수하고,
수수료 테이블이 아닌 파일(수거업체 목록 등)은 품목·금액 컬럼이 없으므로 걸러진다.

프로젝트 규칙: 모든 행에 출처 URL과 기준일자를 함께 남긴다.
"""
import csv
import io
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw", "fees")
OUT = os.path.join(ROOT, "data", "processed")

# 컬럼 별칭. 왼쪽이 정규 이름이다.
ALIAS = {
    # 오타 표기(페기물품목·폐기물품병)가 원본에 그대로 있어 같이 받는다
    "item":     ["대형폐기물명", "폐기물명", "폐기물 명", "품목", "품명", "물품", "품목명",
                 "페기물품목", "폐기물품목", "폐기물품병", "수거품목명",
                 "폐기물이름", "이름"],
    "spec":     ["대형폐기물규격", "폐기물규격", "폐기물 규격", "규격", "규격내용", "규격명"],
    "fee":      ["수수료", "수수료(원)", "금액", "단가", "부과금액", "처리수수료", "배출수수료",
                 "수거수수료", "폐기물수거수수료", "수거품목금액", "수수료금액",
                 "처리비", "총수수료", "총수수료(원)", "폐기수수료", "가격", "가격(원)"],
    "category": ["대형폐기물구분명", "폐기물구분", "폐기물 구분", "구분", "종류", "대분류",
                 "분류", "품목구분", "품목종류", "폐기물종류"],
    "base_date": ["데이터기준일자", "기준일자", "데이터 기준일자"],
    "sido":     ["시도명"],
    "sigungu":  ["시군구명"],
    "paid":     ["유무료여부"],
}
LOOKUP = {}
for canon, names in ALIAS.items():
    for n in names:
        LOOKUP[n] = canon


def norm_key(s):
    """BOM·공백·괄호 안 단위를 지운 비교용 키."""
    s = (s or "").replace("\ufeff", "").strip()
    return re.sub(r"\s+", "", s)


def read_text(path):
    raw = open(path, "rb").read()
    for enc in ("utf-8-sig", "cp949", "utf-8"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "replace")


def map_header(header):
    """원본 헤더 → {정규명: 인덱스}. 못 찾은 컬럼은 빠진다."""
    m = {}
    for i, col in enumerate(header):
        k = norm_key(col)
        if k in LOOKUP:
            m.setdefault(LOOKUP[k], i)
            continue
        # 수수료(원)  처럼 단위가 붙은 변형
        base = re.sub(r"\(.*?\)", "", k)
        if base in LOOKUP:
            m.setdefault(LOOKUP[base], i)
    return m


# 개별 신청·결제 기록을 가려내는 표지. 요금표가 아니라 트랜잭션 로그다.
# (예: 수성구 앱 결제내역 56,476행 — 같은 품목이 수만 번 반복돼 대표 요금이 될 수 없다)
TX_MARKERS = {
    "앱식별자", "사용자식별자", "신청번호", "신청일", "신청일자", "접수일자", "예약번호",
    "배출일", "작업번호", "방문자수", "판매처명", "결제구분", "납부일자", "출력일자",
    "수거완료물품수량", "게시물순서", "현장결제건수",
    "환불접수일", "환불처리일", "수거요청일", "신청접수일자", "배출일자", "수거일자",
    "발주일자", "결제방법", "결제금액", "수수료합계",
}


def is_transaction(header):
    return any(norm_key(h) in TX_MARKERS for h in header)


FEE_RE = re.compile(r"-?[\d,]+")


def parse_fee(v):
    if v is None:
        return None
    v = v.strip().replace('"', "")
    if not v or v in ("-", "무료"):
        return 0 if v == "무료" else None
    m = FEE_RE.search(v)
    if not m:
        return None
    try:
        n = int(m.group(0).replace(",", ""))
    except ValueError:
        return None
    return n if 0 <= n <= 1_000_000 else None


SIDO = [
    "서울특별시", "부산광역시", "대구광역시", "인천광역시", "광주광역시", "대전광역시",
    "울산광역시", "세종특별자치시", "경기도", "강원특별자치도", "강원도", "충청북도",
    "충청남도", "전북특별자치도", "전라북도", "전라남도", "경상북도", "경상남도",
    "제주특별자치도", "전남광주통합특별시",
]
# 표기가 바뀐 광역단체는 현행 명칭으로 모은다.
SIDO_CANON = {"강원도": "강원특별자치도", "전라북도": "전북특별자치도"}
# 공사·공단이 제공기관인 경우 이름에서 관할 시군구가 나온다.
ORG_HINT = {
    "의정부도시공사": ("경기도", "의정부시"),
    "파주도시관광공사": ("경기도", "파주시"),
    "오산도시공사": ("경기도", "오산시"),
    "오산시시설관리공단": ("경기도", "오산시"),
    "세종특별자치시시설관리공단": ("세종특별자치시", ""),
}
# 접미 앞 1글자만 있는 자치구(동구·서구·남구)가 있어 하한을 1로 둔다.
SGG_RE = re.compile(r"([가-힣]{1,7}(?:시|군|구))")


def region_from(title, provider):
    """제목·제공기관에서 시도/시군구를 뽑는다. 표기 흔들림을 여기서 흡수한다."""
    for key, val in ORG_HINT.items():
        if key in (provider or "") or key in (title or ""):
            return val

    text = ((title or "") + " " + (provider or "")).replace("_", " ")
    sido = ""
    for name in SIDO:
        if name in text:
            sido = SIDO_CANON.get(name, name)
            break

    sigungu = ""
    for cand in SGG_RE.findall(text):
        if cand in SIDO or cand == sido:
            continue
        if cand.endswith("공사") or cand.endswith("공단"):
            continue
        sigungu = cand
        break

    # '오산시시'처럼 접미가 겹친 표기를 되돌린다.
    if sigungu.endswith("시시") or sigungu.endswith("군군") or sigungu.endswith("구구"):
        sigungu = sigungu[:-1]
    # 통합시는 시도 자리에 신설 명칭이 오고 실제 관할은 시군구에 있다.
    if sido == "전남광주통합특별시" and not sigungu:
        sigungu = ""
    return sido, sigungu


def main():
    os.makedirs(OUT, exist_ok=True)
    mpath = os.path.join(RAW, "manifest.json")
    if not os.path.exists(mpath):
        raise SystemExit("manifest.json 없음 — fetch_fee_datasets.py 먼저 실행")
    manifest = json.load(open(mpath, encoding="utf-8"))
    by_file = {d["saved_as"]: d for d in manifest["datasets"] if d.get("saved_as")}

    rows, report = [], []
    for fname in sorted(os.listdir(RAW)):
        if not fname.lower().endswith(".csv"):
            continue
        meta = by_file.get(fname, {})
        path = os.path.join(RAW, fname)
        try:
            table = list(csv.reader(io.StringIO(read_text(path))))
        except Exception as e:
            report.append({"file": fname, "status": "read_error", "detail": str(e)})
            continue
        if not table:
            report.append({"file": fname, "status": "empty"})
            continue

        header = table[0]
        if is_transaction(header):
            report.append({"file": fname, "status": "skipped_transaction_log",
                           "header": [norm_key(h) for h in header]})
            continue
        cmap = map_header(header)
        if "item" not in cmap or "fee" not in cmap:
            report.append({
                "file": fname, "status": "skipped_no_fee_table",
                "header": [norm_key(h) for h in header],
            })
            continue

        sido_d, sigungu_d = region_from(meta.get("title"), meta.get("provider"))
        kept = 0
        for r in table[1:]:
            if not r or len(r) <= cmap["item"]:
                continue
            item = (r[cmap["item"]] or "").strip()
            fee = parse_fee(r[cmap["fee"]] if len(r) > cmap["fee"] else None)
            if not item or fee is None:
                continue

            def cell(key):
                i = cmap.get(key)
                return (r[i].strip() if i is not None and len(r) > i else "") or ""

            rows.append({
                "sido": cell("sido") or (sido_d or ""),
                "sigungu": cell("sigungu") or (sigungu_d or ""),
                "category": cell("category"),
                "item": item,
                "spec": cell("spec"),
                "fee": fee,
                "base_date": cell("base_date") or (meta.get("base_date") or ""),
                "dataset_id": meta.get("dataset_id", ""),
                "source_url": meta.get("source_url", ""),
            })
            kept += 1
        report.append({"file": fname, "status": "ok", "rows": kept,
                       "mapped": sorted(cmap.keys())})
        print("  %-58s %5d행" % (fname[:58], kept))

    # 원본 파일 순서나 다운로드 시점이 흔들려도 출력은 고정되게 정렬한다.
    # 안 하면 내용은 그대로인데 매번 diff가 나서 최신성 체크가 오탐한다.
    rows.sort(key=lambda r: (r["sido"], r["sigungu"], r["category"], r["item"],
                              r["spec"], r["fee"], r["dataset_id"]))

    cols = ["sido", "sigungu", "category", "item", "spec", "fee", "base_date",
            "dataset_id", "source_url"]
    with io.open(os.path.join(OUT, "fees.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    regions = sorted({(r["sido"], r["sigungu"]) for r in rows})
    summary = {
        "generated_at": manifest.get("collected_at"),
        "total_rows": len(rows),
        "files_ok": sum(1 for r in report if r["status"] == "ok"),
        "files_skipped": sum(1 for r in report if r["status"] != "ok"),
        "regions": len(regions),
        "distinct_items": len({r["item"] for r in rows}),
        "files": report,
    }
    with io.open(os.path.join(OUT, "fees_report.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("\n총 %d행 / 지역 %d / 고유 품목 %d"
          % (len(rows), len(regions), summary["distinct_items"]))
    print("스킵 %d파일" % summary["files_skipped"])


if __name__ == "__main__":
    main()
