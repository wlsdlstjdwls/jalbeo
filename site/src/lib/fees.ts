import feesJson from '../data/fees.json';

/**
 * 품목별 수수료 통계. scripts/build_fee_stats.py 산출물 (docs/12).
 *
 * 과금 단위가 둘로 갈린다. 다수 지자체가 장롱을 '1쪽당'(문짝 하나당)으로
 * 매기므로 통짜 요금과 같은 중앙값에 섞으면 3쪽 장롱에서 3배가 틀린다.
 */
export interface FeeUnit {
  median: number;
  min: number;
  max: number;
  q1: number;
  q3: number;
  regions: number;
  cheapest: { region: string; fee: number };
  dearest: { region: string; fee: number };
  byRegion: Record<string, number>;
}

export interface FeeStat {
  /** 지역 수가 더 많은 쪽. 화면에서 먼저 말해야 하는 단위다. */
  primary: 'whole' | 'panel';
  baseDate: string;
  whole: FeeUnit | null;
  panel: FeeUnit | null;
}

interface RawUnit {
  median: number;
  min: number;
  max: number;
  q1: number;
  q3: number;
  regions: number;
  cheapest: { region: string; fee: number };
  dearest: { region: string; fee: number };
  by_region: Record<string, number>;
}

interface RawStat {
  primary: 'whole' | 'panel';
  base_date: string;
  whole?: RawUnit;
  panel?: RawUnit;
}

const raw = feesJson as unknown as Record<string, RawStat>;

function toUnit(r: RawUnit | undefined): FeeUnit | null {
  if (!r) return null;
  const { by_region, ...rest } = r;
  return { ...rest, byRegion: by_region };
}

/** 수수료가 없는 품목이 있다. 음식물·재활용품은 애초에 대형폐기물이 아니다. */
export function feeFor(slug: string): FeeStat | null {
  const r = raw[slug];
  if (!r) return null;
  return {
    primary: r.primary,
    baseDate: r.base_date,
    whole: toUnit(r.whole),
    panel: toUnit(r.panel),
  };
}
