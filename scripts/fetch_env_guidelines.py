# -*- coding: utf-8 -*-
"""환경부(기후에너지환경부) 분리배출 관련 행정규칙 원문 수집.

출처: 국가법령정보센터 공동활용 API (https://www.law.go.kr/DRF/)
docs/06-action-plan.md 4번 작업. 품목 페이지 O·X 판정의 근거 데이터.

프로젝트 규칙에 따라 출처 URL과 기준일자(발령일자)를 함께 저장한다.
"""
import json
import os
import re
import ssl
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "data", "raw", "guidelines")
BASE = "https://www.law.go.kr/DRF"
OC = "test"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 Chrome/120"}

# 품목 O·X 판정의 근거가 되는 행정규칙
TARGETS = [
    "재활용가능자원의 분리수거 등에 관한 지침",   # 별표에 품목별 분리배출 방법
    "분리배출 표시에 관한 지침",                 # 표시 기호 체계
    "생활계 유해폐기물의 종류",                  # 건전지·형광등·폐의약품 등
]


def fetch(url):
    for attempt in range(3):
        try:
            return urllib.request.urlopen(
                urllib.request.Request(url, headers=UA), timeout=30, context=CTX
            ).read().decode("utf-8", "replace")
        except Exception as e:
            if attempt == 2:
                sys.stderr.write("FAIL %s: %s\n" % (url[:80], e))
                return ""
            time.sleep(2)


def search(query):
    url = BASE + "/lawSearch.do?" + urllib.parse.urlencode({
        "OC": OC, "target": "admrul", "type": "JSON", "query": query, "display": 20})
    try:
        root = json.loads(fetch(url))["AdmRulSearch"]
    except Exception:
        return []
    items = root.get("admrul") or []
    return [items] if isinstance(items, dict) else items


def as_list(v):
    if not v:
        return []
    return v if isinstance(v, list) else [v]


def download(link, path):
    """별표 파일(HWP/PDF) 저장. 본문이 표·이미지라 파일 자체를 보관한다."""
    url = "https://www.law.go.kr" + link
    try:
        raw = urllib.request.urlopen(
            urllib.request.Request(url, headers=UA), timeout=60, context=CTX).read()
    except Exception as e:
        sys.stderr.write("별표 실패 %s: %s" % (link, e))
        return None
    with open(path, "wb") as f:
        f.write(raw)
    return len(raw)


def slug(name):
    return re.sub(r"[^가-힣A-Za-z0-9]+", "-", name).strip("-")


def main():
    manifest = []
    for query in TARGETS:
        hits = [h for h in search(query) if h["행정규칙명"].strip() == query] or search(query)[:1]
        if not hits:
            print("없음: %s" % query)
            continue
        hit = hits[0]
        detail = hit.get("행정규칙상세링크", "")
        rule_id = (re.search(r"ID=(\d+)", detail) or [None, None])[1]
        if not rule_id:
            print("ID 없음: %s" % query)
            continue
        src = BASE + "/lawService.do?" + urllib.parse.urlencode({
            "OC": OC, "target": "admrul", "ID": rule_id, "type": "JSON"})
        try:
            svc = json.loads(fetch(src))["AdmRulService"]
        except Exception as e:
            print("본문 실패: %s (%s)" % (query, e))
            continue

        lines = []
        for art in as_list(svc.get("조문내용")):
            if isinstance(art, dict):
                lines.append(str(art.get("조문내용", "")))
            else:
                lines.append(str(art))
        text = chr(10).join(l for l in lines if l.strip())
        name = slug(hit["행정규칙명"])

        with open(os.path.join(OUTDIR, name + ".json"), "w", encoding="utf-8") as f:
            json.dump(svc, f, ensure_ascii=False, indent=2)
        with open(os.path.join(OUTDIR, name + ".txt"), "w", encoding="utf-8") as f:
            f.write("# %s\n" % hit["행정규칙명"])
            f.write("# 종류: %s / 소관: %s\n" % (hit["행정규칙종류"], hit["소관부처명"]))
            f.write("# 발령일자(기준일자): %s\n" % hit["발령일자"])
            f.write("# 출처: %s\n" % src)
            f.write("# 수집일: %s\n\n" % time.strftime("%Y-%m-%d"))
            f.write(text)

        # 별표 — 품목별 분리배출요령이 여기 들어있다
        attachments = []
        for tbl in as_list(svc.get("별표", {}).get("별표단위")):
            title = slug(tbl.get("별표제목", ""))[:40]
            num = tbl.get("별표번호", "")
            for key, ext in (("별표서식파일링크", "hwp"), ("별표서식PDF파일링크", "pdf")):
                link = tbl.get(key)
                if not link:
                    continue
                fn = "%s_별표%s_%s.%s" % (name, num, title, ext)
                size = download(link, os.path.join(OUTDIR, fn))
                if size:
                    attachments.append({
                        "title": tbl.get("별표제목"), "no": num, "file": fn,
                        "bytes": size, "source_url": "https://www.law.go.kr" + link})
            time.sleep(0.4)
        if attachments:
            print("   별표 %d개 저장" % len(attachments))

        manifest.append({
            "name": hit["행정규칙명"],
            "kind": hit["행정규칙종류"],
            "ministry": hit["소관부처명"],
            "issued": hit["발령일자"],
            "source_url": src,
            "collected_at": time.strftime("%Y-%m-%d"),
            "chars": len(text),
            "file": name + ".txt",
            "attachments": attachments,
        })
        print("%-38s %s  %d자" % (hit["행정규칙명"][:36], hit["발령일자"], len(text)))
        time.sleep(0.5)

    if len(manifest) < len(TARGETS):
        # 일부라도 못 받았으면 manifest를 줄여서 쓰지 않는다. 훈령이 없어진 게
        # 아니라 law.go.kr이 응답을 안 준 경우가 대부분이다.
        raise SystemExit("수집 실패: %d/%d건. manifest.json은 건드리지 않는다"
                         % (len(manifest), len(TARGETS)))
    with open(os.path.join(OUTDIR, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print("\n-> %s" % OUTDIR)


if __name__ == "__main__":
    main()
