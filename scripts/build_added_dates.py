"""페이지가 처음 올라온 날을 git에서 뽑아 site/src/lib/added.json에 쓴다.

/updates/와 홈의 '새로 들어온 품목'이 읽는다. 품목 추가를 updates.ts에 손으로
적으면 발행할 때마다 빠뜨린다 (판단 19). 개명한 slug는 --follow로 원래 날짜를
찾는다. 아직 커밋 안 된 새 파일은 오늘 날짜가 된다.

품목이나 가이드를 발행한 뒤, 커밋 직전에 돌린다.
"""
import glob
import json
import os
import subprocess
import time

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "site", "src", "lib", "added.json")


def first_added(path):
    out = subprocess.run(
        ["git", "log", "--follow", "--diff-filter=A", "--format=%ad", "--date=short", "--", path],
        capture_output=True, text=True, cwd=ROOT,
    ).stdout.split()
    return out[-1] if out else time.strftime("%Y-%m-%d")


def main():
    res = {}
    for kind in ("items", "guides"):
        for p in glob.glob(os.path.join(ROOT, "site", "src", "content", kind, "*.md")):
            rel = os.path.relpath(p, ROOT).replace(os.sep, "/")
            res["%s/%s" % (kind, os.path.basename(p)[:-3])] = first_added(rel)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(dict(sorted(res.items())), f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("%d개 기록" % len(res))


if __name__ == "__main__":
    main()
