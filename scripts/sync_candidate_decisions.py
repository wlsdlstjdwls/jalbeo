# -*- coding: utf-8 -*-
"""후보 목록의 `decision` 칸을 실제 상태와 맞춘다.

후보 CSV(`candidates-external.csv`, `candidates-bunri.csv`)의 decision은 손으로
적는다. 그런데 실측을 돌리고 페이지를 내는 동안 그 칸을 안 적어서, 이미 재고
이미 발행한 주제가 계속 '미판정'으로 남아 있었다. 21차 시점에 외부 씨앗 후보
1,129개 중 960개가 미판정으로 보였는데 실제로는 44개가 12~14차에서 이미 측정됐고
나머지도 상당수가 별칭으로 흡수돼 있었다. **풀이 부풀면 "씨앗이 아직 많다"고
잘못 읽는다**(판단 35의 반대 방향 오독).

여기서 채우는 것은 기계로 확인되는 것만이다.
  - 현재 어휘(발행명, 별칭, 시드)에 있으면      -> 기존 커버
  - 실측 N차에서 이미 잰 주제면                 -> 실측N차
사람이 판단해야 하는 '보류', '노이즈', '사업장'은 건드리지 않는다.

    python scripts/sync_candidate_decisions.py --dry
    python scripts/sync_candidate_decisions.py
"""
import csv
import io
import os
import sys
import glob
import importlib.util

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KW = os.path.join(ROOT, "data", "keywords")
TARGETS = ("candidates-external.csv", "candidates-bunri.csv")


def load_extractor():
    path = os.path.join(ROOT, "scripts", "extract_external_seeds.py")
    spec = importlib.util.spec_from_file_location("ex", path)
    mod = importlib.util.module_from_spec(spec)
    cwd = os.getcwd()
    os.chdir(ROOT)          # 그 모듈은 상대경로를 쓴다
    try:
        spec.loader.exec_module(mod)
    finally:
        os.chdir(cwd)
    return mod


def measured_topics(norm):
    """실측 N차에서 이미 잰 주제 -> 'N'. 별칭 회차는 alias 칸을 쓴다."""
    out = {}
    for path in sorted(glob.glob(os.path.join(KW, "gate1-volumes-*.csv"))):
        tag = os.path.basename(path)[len("gate1-volumes-"):-len(".csv")]
        if not tag.isdigit():
            continue
        for r in csv.DictReader(io.open(path, encoding="utf-8-sig")):
            name = r.get("topic") or r.get("alias")
            if name:
                out.setdefault(norm(name), tag)
            later = r.get("later") or ""
            for alt in (x.strip() for x in later.split(",")):
                if alt:
                    out.setdefault(norm(alt), tag)
    return out


def main():
    dry = "--dry" in sys.argv
    mod = load_extractor()
    norm = mod.norm
    cwd = os.getcwd()
    os.chdir(ROOT)
    try:
        vocab = mod.known_vocabulary()
    finally:
        os.chdir(cwd)
    measured = measured_topics(norm)

    for fname in TARGETS:
        path = os.path.join(KW, fname)
        rows = list(csv.DictReader(io.open(path, encoding="utf-8-sig")))
        fields = list(rows[0].keys())
        filled = {"기존 커버": 0, "실측": 0}
        for r in rows:
            if r.get("decision"):
                continue
            key = norm(r["item"])
            if key in vocab:
                r["decision"] = "기존 커버"
                r["note"] = r.get("note") or vocab[key]
                filled["기존 커버"] += 1
            elif key in measured:
                r["decision"] = "실측%s차" % measured[key]
                filled["실측"] += 1
        left = sum(1 for r in rows if not r.get("decision"))
        print("%-28s 기존 커버 %3d, 실측 표시 %3d, 남은 미판정 %4d"
              % (fname, filled["기존 커버"], filled["실측"], left))
        if not dry:
            with io.open(path, "w", encoding="utf-8", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=fields)
                w.writeheader()
                w.writerows(rows)
    if dry:
        print("\n--dry 라서 안 썼다.")


if __name__ == "__main__":
    main()
