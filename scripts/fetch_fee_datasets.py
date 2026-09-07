# -*- coding: utf-8 -*-
"""대형폐기물 처리수수료 공공데이터 수집.

출처: 공공데이터포털(data.go.kr) 파일데이터 검색 '대형폐기물 수수료'.
docs/06-action-plan.md 5번 작업. 품목 페이지의 '비용' 축 근거 데이터.

프로젝트 규칙에 따라 데이터셋마다 출처 URL과 기준일자를 manifest.json에 남긴다.
정규화는 normalize_fees.py가 맡는다. 이 스크립트는 원본을 그대로 받는다.
"""
import json
import os
import re
import ssl
import sys
import time
import urllib.parse
import urllib.request

# Windows 콘솔이 cp949라 유니코드 기호에서 죽는다. 출력만 UTF-8로 고정한다.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "data", "raw", "fees")
BASE = "https://www.data.go.kr"
KEYWORD = "대형폐기물 수수료"
UA = {"User-Agent": "Mozilla/5.0 Chrome/120"}
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def get(url, referer=None, binary=False):
    h = dict(UA)
    if referer:
        h["Referer"] = referer
    for attempt in range(3):
        try:
            r = urllib.request.urlopen(
                urllib.request.Request(url, headers=h), timeout=40, context=CTX
            )
            raw = r.read()
            return (raw, r.headers) if binary else (raw.decode("utf-8", "replace"), r.headers)
        except Exception as e:
            if attempt == 2:
                print("  ! %s" % e)
                return (None, None)
            time.sleep(2 * (attempt + 1))


def list_datasets():
    """검색 결과를 넘기며 파일데이터 ID를 모은다."""
    ids, page = [], 1
    while True:
        url = (
            BASE + "/tcs/dss/selectDataSetList.do?dType=FILE"
            "&keyword=" + urllib.parse.quote(KEYWORD)
            + "&perPage=10&currentPage=%d" % page
        )
        html, _ = get(url)
        if not html:
            break
        found = re.findall(r"/data/(\d+)/fileData\.do", html)
        new = [i for i in dict.fromkeys(found) if i not in ids]
        if not new:
            break
        ids.extend(new)
        print("  page %d — 누적 %d건" % (page, len(ids)))
        page += 1
        time.sleep(0.6)
        if page > 40:
            break
    return ids


def strip_tags(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()


def parse_meta(html, did):
    """데이터셋 페이지에서 제목·제공기관·기준일자·다운로드 링크를 뽑는다."""
    m = re.search(r"<title>([^<]+)</title>", html)
    title = strip_tags(m.group(1)).replace("| 공공데이터포털", "").strip() if m else ""

    def field(label):
        m = re.search(
            r"<th[^>]*>\s*%s\s*</th>\s*<td[^>]*>(.*?)</td>" % re.escape(label),
            html, re.S,
        )
        return strip_tags(m.group(1)) if m else None

    dl = re.search(
        r"/cmm/cmm/fileDownload\.do\?atchFileId=([A-Za-z0-9_]+)&(?:amp;)?fileDetailSn=(\d+)",
        html,
    )
    return {
        "dataset_id": did,
        "title": title,
        "source_url": BASE + "/data/%s/fileData.do" % did,
        "provider": field("제공기관"),
        "updated": field("수정일") or field("등록일"),
        "base_date": field("데이터 기준일자"),
        "download": (
            BASE + "/cmm/cmm/fileDownload.do?atchFileId=%s&fileDetailSn=%s&insertDataPrcus=N"
            % (dl.group(1), dl.group(2))
        ) if dl else None,
    }


def filename_from(headers, fallback):
    cd = headers.get("Content-Disposition", "") if headers else ""
    m = re.search(r'filename="([^"]+)"', cd)
    if not m:
        return fallback + ".csv"
    name = urllib.parse.unquote(m.group(1))
    return re.sub(r'[\/:*?"<>|]', "_", name).strip()


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    print("[1/3] 데이터셋 목록 수집")
    ids = list_datasets()
    print("  총 %d건" % len(ids))
    if not ids:
        # 목록이 비면 데이터가 사라진 게 아니라 접속이 안 된 것이다(해외 IP에서
        # data.go.kr이 타임아웃 나는 일이 있다). manifest를 빈 목록으로 덮어쓰면
        # normalize_fees.py가 0행을 정상 산출물로 쓰고, 최신성 체크가 그걸
        # "전부 삭제됨"으로 읽어 오탐 이슈를 낸다. 기존 manifest를 그대로 두고
        # 실패로 끝낸다.
        raise SystemExit("수집 실패: 데이터셋 목록 0건. manifest.json은 건드리지 않는다")

    print("[2/3] 메타 + 파일 수집")
    manifest, ok, fail = [], 0, 0
    for n, did in enumerate(ids, 1):
        page_url = BASE + "/data/%s/fileData.do" % did
        html, _ = get(page_url)
        if not html:
            fail += 1
            continue
        meta = parse_meta(html, did)
        if not meta["download"]:
            print("  [%d/%d] %s — 다운로드 링크 없음" % (n, len(ids), did))
            meta["saved_as"] = None
            manifest.append(meta)
            fail += 1
            time.sleep(0.5)
            continue

        raw, headers = get(meta["download"], referer=page_url, binary=True)
        if not raw or len(raw) < 40:
            print("  [%d/%d] %s — 빈 응답" % (n, len(ids), did))
            meta["saved_as"] = None
            manifest.append(meta)
            fail += 1
            time.sleep(0.5)
            continue

        fname = filename_from(headers, did)
        with open(os.path.join(OUTDIR, fname), "wb") as f:
            f.write(raw)
        meta["saved_as"] = fname
        meta["bytes"] = len(raw)
        manifest.append(meta)
        ok += 1
        print("  [%d/%d] %s (%d bytes)" % (n, len(ids), fname[:58], len(raw)))
        time.sleep(0.6)

    if ok == 0:
        raise SystemExit("수집 실패: 다운로드 0건 (실패 %d). manifest.json은 건드리지 않는다" % fail)

    print("[3/3] manifest 기록")
    with open(os.path.join(OUTDIR, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(
            {
                "collected_at": time.strftime("%Y-%m-%d"),
                "keyword": KEYWORD,
                "search_url": BASE + "/tcs/dss/selectDataSetList.do?dType=FILE&keyword="
                + urllib.parse.quote(KEYWORD),
                "total": len(ids),
                "downloaded": ok,
                "failed": fail,
                "datasets": manifest,
            },
            f, ensure_ascii=False, indent=2,
        )
    print("완료 — 성공 %d / 실패 %d" % (ok, fail))


if __name__ == "__main__":
    main()
