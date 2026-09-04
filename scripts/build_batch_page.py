# -*- coding: utf-8 -*-
"""복붙 묶음 마크다운을 클릭 한 번짜리 HTML 페이지로 굽는다.

키워드 도구는 씨앗을 한 번에 5개까지만 받는다. 그래서 실측은 늘
"묶음을 골라 드래그해서 복사 -> 붙여넣기 -> 조회 -> 다운로드"의 반복이고,
5차는 7묶음, 4차는 35묶음이었다. 드래그가 한 글자만 어긋나도 조회가 틀어진다.

이 페이지는 묶음마다 복사 버튼 하나를 준다. 어디까지 했는지는 브라우저에
남는다(localStorage). 안 돌아간 묶음은 `실패`로 찍어 두면 위로 모인다 -
2차 때 8/12 묶음이 통째로 빠진 걸 4차까지 모르고 끌고 갔다.

쓰는 법:
    python scripts/build_batch_page.py data/keywords/gate1-batches-5.md
    -> data/keywords/gate1-batches-5.html (더블클릭해서 연다)

인자를 안 주면 가장 최근 `gate1-batches-*.md`를 잡는다.
"""
import glob
import io
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KW = os.path.join(ROOT, "data", "keywords")

TOOL_URL = "https://searchad.naver.com/"
# 묶음 헤딩: **3/7** 또는 **3/7** - 꼬리말
HEAD_RE = re.compile(r"^\*\*(\d+)/(\d+)\*\*(.*)$")


def parse(path):
    """마크다운에서 (번호, 꼬리말, [키워드...]) 목록과 문서 제목을 뽑는다."""
    lines = io.open(path, encoding="utf-8").read().split("\n")
    title = next((l[2:].strip() for l in lines if l.startswith("# ")), "실측 묶음")

    batches = []
    pending = None
    fence = False
    buf = []
    for line in lines:
        m = HEAD_RE.match(line.strip())
        if m:
            pending = (int(m.group(1)), m.group(3).strip().strip("-— ").strip())
            continue
        if line.strip() == "```":
            if fence:
                if pending and buf:
                    batches.append({"no": pending[0], "note": pending[1], "kw": buf})
                pending, buf, fence = None, [], False
            else:
                fence = True
                buf = []
            continue
        if fence and pending and line.strip():
            buf.append(line.strip())
    return title, batches


TEMPLATE = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>__TITLE__</title>
<style>
  :root {
    --paper: #f5f3ee; --card: #fff; --ink: #111; --line: #d9d5cb;
    --lime: #c9f24d; --faint: #6b6862; --ok: #2fa84f; --bad: #c8442e;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; background: var(--paper); color: var(--ink);
    font: 400 16px/1.6 "Pretendard Variable", Pretendard, system-ui, sans-serif;
    word-break: keep-all;
  }
  .wrap { max-width: 880px; margin: 0 auto; padding: 28px 20px 60px; }
  h1 { margin: 0; font-size: clamp(24px, 4.6vw, 38px); letter-spacing: -.04em; line-height: 1.12; }
  .sub { margin: 12px 0 0; font-size: 14px; font-weight: 600; color: var(--faint); max-width: 62ch; }
  .bar {
    display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
    margin: 20px 0 0; padding: 14px 16px;
    border: 2px solid var(--ink); background: var(--card);
  }
  .bar b { font-size: 20px; letter-spacing: -.03em; font-variant-numeric: tabular-nums; }
  .track { flex: 1; min-width: 140px; height: 8px; background: var(--line); }
  .track i { display: block; height: 100%; background: var(--lime); border-right: 2px solid var(--ink); }
  a.tool, button {
    cursor: pointer; border: 2px solid var(--ink); background: var(--card);
    padding: 7px 14px; font: inherit; font-size: 13px; font-weight: 800; color: inherit;
  }
  a.tool { text-decoration: none; background: var(--lime); }
  button:hover, a.tool:hover { box-shadow: 3px 3px 0 var(--ink); }
  button:active { box-shadow: none; transform: translate(2px, 2px); }
  .cards { margin-top: 18px; display: grid; gap: 12px; }
  .card { border: 2px solid var(--ink); background: var(--card); padding: 14px 16px; }
  /* 다음에 할 묶음만 띄운다. 어디까지 했는지 세지 않아도 되게. */
  .card.next { box-shadow: 5px 5px 0 var(--ink); }
  .card.done { opacity: .55; }
  .card.fail { border-color: var(--bad); }
  .chead { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
  .no { font-size: 13px; font-weight: 800; letter-spacing: .04em; }
  .note { font-size: 12.5px; font-weight: 700; color: var(--faint); }
  .grow { flex: 1; }
  .state { font-size: 12px; font-weight: 800; }
  .state.done { color: var(--ok); }
  .state.fail { color: var(--bad); }
  pre {
    margin: 10px 0 0; padding: 10px 12px; background: var(--paper);
    border: 1px solid var(--line); font-size: 13.5px; line-height: 1.7;
    white-space: pre-wrap; word-break: break-all; font-family: inherit; font-weight: 600;
  }
  .acts { margin-top: 10px; display: flex; gap: 8px; flex-wrap: wrap; }
  .foot { margin-top: 26px; font-size: 12.5px; font-weight: 600; color: var(--faint); }
  .foot code { background: #ebe7dd; padding: 1px 5px; }
</style>
</head>
<body>
<div class="wrap">
  <h1>__TITLE__</h1>
  <p class="sub">묶음마다 <b>복사</b>를 누르고 키워드 도구 입력창에 붙여넣는다.
    조회와 다운로드까지 끝나면 <b>완료</b>, 조회가 안 돌아갔으면 <b>실패</b>를 찍는다.
    실패는 목록 위로 올라온다. 진행 상태는 이 브라우저에만 남는다.<br />
    브라우저가 클립보드를 막으면 버튼이 <b>선택함, Ctrl+C</b>로 바뀐다. 그때는 Ctrl+C만 누르면 된다.</p>

  <div class="bar">
    <b id="prog">0 / __N__</b>
    <span class="track"><i id="fill" style="width:0%"></i></span>
    <a class="tool" href="__TOOL__" target="_blank" rel="noopener">키워드 도구 열기</a>
    <button type="button" id="reset">진행 초기화</button>
  </div>

  <div class="cards" id="cards"></div>

  <p class="foot">엑셀은 <code>data/keywords/__DIR__/</code> 에 모은다.
    다 모이면 <code>python scripts/__AGG__</code></p>
</div>

<script>
var BATCHES = __DATA__;
var KEY = '__KEY__';
var state = {};
try { state = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) { state = {}; }

function save() {
  try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {}
}

// 클립보드 API는 https와 localhost에서만 산다. 이 페이지는 보통 file://로 열리므로
// 세 겹으로 간다: execCommand -> 클립보드 API -> 블록 자체를 선택해 두기.
// 셋째까지 내려가도 Ctrl+C 한 번이면 되고, 눌렀는데 조용히 실패하는 경우가 없다.
function selectBlock(pre) {
  var range = document.createRange();
  range.selectNodeContents(pre);
  var sel = window.getSelection();
  sel.removeAllRanges();
  sel.addRange(range);
}

function legacyCopy(text) {
  var ta = document.createElement('textarea');
  ta.value = text;
  ta.style.position = 'fixed';
  ta.style.top = '0';
  ta.style.opacity = '0';
  document.body.appendChild(ta);
  ta.focus();
  ta.select();
  var ok = false;
  try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
  document.body.removeChild(ta);
  return ok;
}

// 성공하면 true, 선택만 걸어 뒀으면 false.
function copy(pre, text) {
  if (legacyCopy(text)) { selectBlock(pre); return Promise.resolve(true); }
  selectBlock(pre);
  if (navigator.clipboard && window.isSecureContext) {
    return navigator.clipboard.writeText(text)
      .then(function () { return true; })
      .catch(function () { return false; });
  }
  return Promise.resolve(false);
}

function rank(b) {
  return state[b.no] === 'fail' ? 0 : state[b.no] === 'done' ? 2 : 1;
}

function render() {
  var done = BATCHES.filter(function (b) { return state[b.no] === 'done'; }).length;
  document.getElementById('prog').textContent = done + ' / ' + BATCHES.length;
  document.getElementById('fill').style.width = (done / BATCHES.length * 100) + '%';

  // 실패를 맨 위로 올린다. 빠진 묶음이 목록 아래에 숨으면 또 놓친다.
  var order = BATCHES.slice().sort(function (a, b) {
    return rank(a) - rank(b) || a.no - b.no;
  });
  var todo = order.filter(function (b) { return state[b.no] !== 'done'; });
  var nextNo = todo.length ? todo[0].no : null;

  document.getElementById('cards').innerHTML = order.map(function (b) {
    var st = state[b.no] || '';
    var cls = 'card' + (st ? ' ' + st : '') + (b.no === nextNo ? ' next' : '');
    var lab = st === 'done' ? '완료' : st === 'fail' ? '실패, 다시' : '';
    return '<div class="' + cls + '">' +
      '<div class="chead"><span class="no">' + b.no + ' / ' + BATCHES.length + '</span>' +
      (b.note ? '<span class="note">' + b.note + '</span>' : '') +
      '<span class="grow"></span>' +
      '<span class="state ' + st + '">' + lab + '</span></div>' +
      '<pre id="kw' + b.no + '">' + b.kw.join('\\n') + '</pre>' +
      '<div class="acts">' +
        '<button type="button" data-copy="' + b.no + '">복사</button>' +
        '<button type="button" data-mark="' + b.no + '" data-v="done">완료</button>' +
        '<button type="button" data-mark="' + b.no + '" data-v="fail">실패</button>' +
        '<button type="button" data-mark="' + b.no + '" data-v="">되돌리기</button>' +
      '</div></div>';
  }).join('');
}

document.getElementById('cards').addEventListener('click', function (e) {
  var btn = e.target.closest('button');
  if (!btn) { return; }
  if (btn.dataset.copy) {
    var hit = BATCHES.filter(function (x) { return String(x.no) === btn.dataset.copy; })[0];
    var pre = document.getElementById('kw' + hit.no);
    copy(pre, hit.kw.join('\\n')).then(function (ok) {
      btn.textContent = ok ? '복사됨' : '선택함, Ctrl+C';
      setTimeout(function () { btn.textContent = '복사'; }, ok ? 1200 : 3000);
    });
    return;
  }
  if (btn.dataset.mark) {
    var v = btn.dataset.v;
    if (v) { state[btn.dataset.mark] = v; } else { delete state[btn.dataset.mark]; }
    save();
    render();
  }
});

document.getElementById('reset').addEventListener('click', function () {
  state = {};
  save();
  render();
});

render();
</script>
</body>
</html>
"""


def main():
    if len(sys.argv) > 1:
        src = sys.argv[1]
    else:
        cands = sorted(glob.glob(os.path.join(KW, "gate1-batches-*.md")))
        if not cands:
            sys.exit("gate1-batches-*.md 가 없다.")
        src = cands[-1]
    if not os.path.exists(src):
        sys.exit("없는 파일: %s" % src)

    title, batches = parse(src)
    if not batches:
        sys.exit("묶음을 못 찾았다: %s" % src)

    stem = os.path.splitext(os.path.basename(src))[0]      # gate1-batches-5
    round_no = stem.rsplit("-", 1)[-1]                     # 5
    out = os.path.join(os.path.dirname(src), stem + ".html")

    html = (TEMPLATE
            .replace("__TITLE__", title)
            .replace("__N__", str(len(batches)))
            .replace("__TOOL__", TOOL_URL)
            .replace("__DIR__", "gate1-%s" % round_no)
            .replace("__AGG__", "gate1_batch%s_aggregate.py" % round_no)
            .replace("__KEY__", "jalbeo_batches_%s" % round_no)
            .replace("__DATA__", json.dumps(batches, ensure_ascii=False)))

    io.open(out, "w", encoding="utf-8", newline="\n").write(html)
    print("%d묶음 / 키워드 %d개 -> %s"
          % (len(batches), sum(len(b["kw"]) for b in batches), out))


if __name__ == "__main__":
    main()
