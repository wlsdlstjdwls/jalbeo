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

/** 빌드 시점 DB 스냅샷. 발행된 품목만 들어 있다. */
export const items = itemsJson as unknown as ItemRow[];
export const bySlug = new Map(items.map((i) => [i.slug, i]));
