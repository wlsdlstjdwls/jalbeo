import feesJson from '../data/fees.json';

/** 품목별 수수료 통계. scripts/build_fee_stats.py 산출물 (docs/12). */
export interface FeeStat {
  median: number;
  min: number;
  max: number;
  q1: number;
  q3: number;
  regions: number;
  cheapest: { region: string; fee: number };
  dearest: { region: string; fee: number };
  baseDate: string;
  byRegion: Record<string, number>;
}

interface RawStat {
  median: number;
  min: number;
  max: number;
  q1: number;
  q3: number;
  regions: number;
  cheapest: { region: string; fee: number };
  dearest: { region: string; fee: number };
  base_date: string;
  by_region: Record<string, number>;
}

const raw = feesJson as unknown as Record<string, RawStat>;

/** 수수료 데이터가 없는 품목이 있다. 음식물·재활용품은 애초에 대형폐기물이 아니다. */
export function feeFor(slug: string): FeeStat | null {
  const r = raw[slug];
  if (!r) return null;
  return {
    median: r.median,
    min: r.min,
    max: r.max,
    q1: r.q1,
    q3: r.q3,
    regions: r.regions,
    cheapest: r.cheapest,
    dearest: r.dearest,
    baseDate: r.base_date,
    byRegion: r.by_region,
  };
}
