import itemsJson from '../data/items.json';

export interface ItemRow {
  slug: string;
  name: string;
  aliases: string[] | null;
  verdict: string;
  verdict_line: string;
  category: string | null;
  housing_split: boolean;
  region_varies: boolean;
  monthly_volume: number | null;
  competitor_has: boolean;
  published: boolean;
}

/**
 * 가운뎃점은 사이트 카피에서 쓰지 않는다. DB 원문은 2026-09-04에 한 번 정리했지만
 * 저작은 계속 DB에서 하므로, 스냅샷을 읽는 이 지점에 방어선을 남겨 둔다.
 * (JSON을 직접 고치는 것은 소용이 없다. 빌드마다 pull-data가 덮어쓴다.)
 */
function strip(text: string): string {
  return text
    // 붙여 쓰는 복합어는 쉼표를 넣으면 뜻이 갈라진다.
    .replace(/전기[·ㆍ]\s*전자/g, '전기전자')
    .replace(/시[·ㆍ]군[·ㆍ]구/g, '시군구')
    .replace(/\s*[·ㆍ]\s*/g, ', ');
}

function noMidDot<T>(row: T): T {
  const out = { ...row } as Record<string, unknown>;
  for (const [k, v] of Object.entries(out)) {
    if (typeof v === 'string') out[k] = strip(v);
    else if (Array.isArray(v)) out[k] = v.map((x) => (typeof x === 'string' ? strip(x) : x));
  }
  return out as T;
}

/** 빌드 시점 DB 스냅샷. 발행된 품목만 들어 있다. */
export const items = (itemsJson as unknown as ItemRow[]).map(noMidDot);
export const bySlug = new Map(items.map((i) => [i.slug, i]));
