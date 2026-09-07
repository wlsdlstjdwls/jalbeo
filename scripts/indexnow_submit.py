# -*- coding: utf-8 -*-
"""IndexNow로 URL을 통지한다 (빙, 얀덱스, 네이버, 세즈남, 옙이 공유).

구글은 IndexNow에 참여하지 않는다 - 구글은 scripts/indexing_queue.py로 계속
하루 할당량만큼 손으로 넣는다. 이 스크립트는 그 나머지 엔진 전용이다.

    python scripts/indexnow_submit.py            # 신규 URL만 제출
    python scripts/indexnow_submit.py --dry       # 보기만, 전송 안 함
    python scripts/indexnow_submit.py --force     # 이미 낸 것도 전부 재제출

**안 바뀐 URL을 반복 제출하면 안 된다.** IndexNow는 그런 호스트를 스팸으로
보고 순위를 낮추고, 짧은 시간에 몰아 쏘면 429(rate limit)가 뜬다. 그래서
이 스크립트는 사이트맵 전체가 아니라 data/indexing/indexnow_log.json에
아직 없는 URL만 골라 보낸다 - --force는 키 교체 등 정말 전부 다시 알려야
할 때만 쓴다.

키 파일은 site/public/<키>.txt에 있고 배포돼 있어야 한다 - IndexNow가
keyLocation을 가져와 소유를 확인하기 때문이다.
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
        state = json.load(io.open(STATE, encoding="utf-8"))
        state.setdefault("submitted", {})
        state.setdefault("runs", [])
        return state
    return {"submitted": {}, "runs": []}


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
            # IndexNow는 200/202가 정상, 429는 과다 제출이니 바로 멈춰야 한다
            results.append((len(chunk), e.code))
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="전송하지 않고 신규 URL 수만 본다")
    ap.add_argument("--force", action="store_true",
                    help="이미 제출 기록이 있는 URL도 전부 다시 보낸다 (키 교체 등 예외 상황용)")
    args = ap.parse_args()

    urls = load_urls()
    state = load_state()

    targets = urls if args.force else [u for u in urls if u not in state["submitted"]]
    print("사이트맵 URL %d개, 그 중 대상 %d개%s"
          % (len(urls), len(targets), " (--force)" if args.force else ""))
    print("키 위치: %s" % KEY_LOCATION)

    if not targets:
        print("신규 URL 없음 - 전송 안 함 (반복 제출은 스팸으로 처리될 수 있다)")
        return

    if args.dry:
        print("(--dry 라 전송 안 했다)")
        return

    results = submit(targets)
    stamp = datetime.datetime.now().isoformat(timespec="seconds")
    ok = all(200 <= code < 300 for _, code in results)

    if ok:
        for u in targets:
            state["submitted"][u] = stamp

    state["runs"].append({
        "at": stamp,
        "url_count": len(targets),
        "results": [{"count": c, "status": s} for c, s in results],
        "ok": ok,
    })
    save_state(state)

    for count, status in results:
        print("%d개 전송 -> HTTP %d" % (count, status))
    print("기록함 -> %s" % os.path.relpath(STATE, ROOT))
    if not ok:
        sys.exit("일부 배치가 실패했다. 상태코드를 확인해라 (403은 키 파일 미배포, 429는 과다 제출 가능성).")


if __name__ == "__main__":
    main()
