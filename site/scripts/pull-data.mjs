/**
 * 빌드 직전 Supabase -> 정적 JSON 스냅샷.
 *
 * DB는 저작 저장소일 뿐이다. 이 스크립트가 빌드 때 1회 읽어 JSON으로 떨구고,
 * 페이지는 그 JSON만 본다. 사용자 요청 경로에 DB가 끼지 않는다.
 *
 * 자격증명이 없으면 커밋된 스냅샷을 그대로 쓴다 -> 로컬·CI 어디서든 빌드가 깨지지 않는다.
 */
import { mkdir, writeFile, access } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const OUT = join(dirname(fileURLToPath(import.meta.url)), '..', 'src', 'data');
const URL_ = process.env.SUPABASE_URL;
const KEY = process.env.SUPABASE_ANON_KEY;

/**
 * 테이블 -> PostgREST 질의. 발행된 품목과 그에 딸린 데이터만 가져온다.
 *
 * bulky_fees는 여기 없다 — 원안 설계 잔재로, 실제 수수료는 별도 파이프라인
 * (data/raw/fees -> normalize_fees.py -> build_fee_stats.py -> fees.json)이
 * 만든다. DB 테이블 자체(db/migrations)는 남아 있지만 site는 더 이상 읽지 않는다.
 */
const TABLES = {
  // 미측정 품목(monthly_volume null)이 뒤로 가되, 그 안에서는 이름순으로 고정한다.
  // 2차 정렬이 없으면 빌드마다 목록 꼬리 순서가 바뀌어 diff가 지저분해진다.
  items: 'items?select=*&published=eq.true&order=monthly_volume.desc.nullslast,name.asc',
  regions: 'regions?select=*&order=sido,sigungu',
  item_region_rules: 'item_region_rules?select=*',
  guideline_verdicts: 'guideline_verdicts?select=*',
};

async function fetchTable(query) {
  const res = await fetch(`${URL_}/rest/v1/${query}`, {
    headers: { apikey: KEY, Authorization: `Bearer ${KEY}` },
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} — ${query}`);
  return res.json();
}

async function exists(path) {
  try { await access(path); return true; } catch { return false; }
}

async function main() {
  await mkdir(OUT, { recursive: true });

  if (!URL_ || !KEY) {
    const missing = [];
    for (const name of Object.keys(TABLES)) {
      if (!(await exists(join(OUT, `${name}.json`)))) missing.push(name);
    }
    for (const name of missing) {
      await writeFile(join(OUT, `${name}.json`), '[]\n');
    }
    console.warn(
      '[pull-data] SUPABASE_URL / SUPABASE_ANON_KEY 없음 — 커밋된 스냅샷으로 빌드합니다.' +
      (missing.length ? ` (없어서 빈 배열로 만든 것: ${missing.join(', ')})` : ''),
    );
    return;
  }

  for (const [name, query] of Object.entries(TABLES)) {
    const rows = await fetchTable(query);
    await writeFile(join(OUT, `${name}.json`), JSON.stringify(rows, null, 1) + '\n');
    console.log(`[pull-data] ${name}: ${rows.length}행`);
  }
}

main().catch((err) => {
  console.error('[pull-data] 실패:', err.message);
  process.exit(1);
});
