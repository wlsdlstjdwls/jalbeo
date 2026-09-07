# -*- coding: utf-8 -*-
"""IndexNow로 URL을 한 번에 통지한다 (빙, 얀덱스, 네이버, 세즈남, 옙이 공유).

구글은 IndexNow에 참여하지 않는다 - 구글은 scripts/indexing_queue.py로 계속
하루 할당량만큼 손으로 넣는다. 이 스크립트는 그 나머지 엔진 전용이다.

    python scripts/indexnow_submit.py            # 사이트맵 전체 제출
    python scripts/indexnow_submit.py --dry       # 보기만, 전송 안 함

키 파일은 site/public/<키>.txt에 있고 배포돼 있어야 한다 - IndexNow가
keyLocation을 가져와 소유를 확인하기 때문이다. 이 스크립트를 처음 돌리기
전에 반드시 한 번 배포(git push)부터 한다.

기록은 data/indexing/indexnow_log.json. 하루 할당량은 없지만 - 새 페이지가
없는데 반복 제출하면 낭비이므로 마지막 제출 시각과 건수를 남긴다.
"""
import argparse
import datetime
import io
import json
import os
import re
import sys
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_DIR = os.path.join(ROOT, "data", "indexing")
STATE = os.path.join(STATE_DIR, "indexnow_log.json")
SITEMAP = "https://jalbeo.com/sitemap-0.xml"
LOCAL_SITEMAP = os.path.join(ROOT, "site", "dist", "sitemap-0.xml")

HOST = "jalbeo.com"
KEY = "7dbb9be6e5cc42ad8418a65a10bdc0e0"
KEY_LOCATION = "https://%s/%s.txt" % (HOST, KEY)
ENDPOINT = "https://api.indexnow.org/indexnow"
BATCH = 10000  # IndexNow 한 번 호출당 최대 URL 수


def load_urls():
    """사이트맵이 발행 목록의 원본이다. 라이브를 먼저 보고, 안 되면 로컬 빌드."""
    xml = None
    try:
        with urllib.request.urlopen(SITEMAP, timeout=15) as r:
            xml = r.read().decode("utf-8")
    except Exception:
        if os.path.exists(LOCAL_SITEMAP):
            xml = io.open(LOCAL_SITEMAP, encoding="utf-8").read()
    if not xml:
        sys.exit("사이트맵을 못 읽었다. 네트워크를 보거나 site에서 npm run build 를 먼저 돌려라.")
    return re.findall(r"<loc>([^<]+)</loc>", xml)


def load_state():
    if os.path.exists(STATE):
        return json.load(io.open(STATE, encoding="utf-8"))
    return {"runs": []}


def save_state(state):
    if not os.path.isdir(STATE_DIR):
        os.makedirs(STATE_DIR)
    with io.open(STATE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def submit(urls):
    """최대 BATCH개씩 나눠 POST. 응답 상태코드를 그대로 반환한다."""
    results = []
    for i in range(0, len(urls), BATCH):
        chunk = urls[i:i + BATCH]
        body = json.dumps({
            "host": HOST,
            "key": KEY,
            "keyLocation": KEY_LOCATION,
            "urlList": chunk,
        }).encode("utf-8")
        req = urllib.request.Request(
            ENDPOINT, data=body, method="POST",
            headers={"Content-Type": "application/json; charset=utf-8"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                results.append((len(chunk), r.status))
        except urllib.error.HTTPError as e:
            # IndexNow는 200/202가 정상, 나머지는 본문에 이유가 있다
            results.append((len(chunk), e.code))
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="전송하지 않고 URL 수만 본다")
    args = ap.parse_args()

    urls = load_urls()
    print("사이트맵 URL %d개" % len(urls))
    print("키 위치: %s" % KEY_LOCATION)

    if args.dry:
        print("(--dry 라 전송 안 했다)")
        return

    results = submit(urls)
    state = load_state()
    stamp = datetime.datetime.now().isoformat(timespec="seconds")
    ok = all(200 <= code < 300 for _, code in results)
    state["runs"].append({
        "at": stamp,
        "url_count": len(urls),
        "results": [{"count": c, "status": s} for c, s in results],
        "ok": ok,
    })
    save_state(state)

    for count, status in results:
        print("%d개 전송 -> HTTP %d" % (count, status))
    print("기록함 -> %s" % os.path.relpath(STATE, ROOT))
    if not ok:
        sys.exit("일부 배치가 실패했다. 상태코드를 확인해라 (403은 키 파일 미배포 가능성).")


if __name__ == "__main__":
    main()
