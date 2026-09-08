import feesJson from '../data/fees.json';

/**
 * 품목별 수수료 통계. scripts/build_fee_stats.py 산출물 (docs/12, docs/26).
 *
 * 과금 단위가 갈린다. 다수 지자체가 장롱을 '1쪽당'(문짝 하나당)으로 매기고,
 * 카펫은 3.3㎡당, 장판은 5m당, 깨진 유리는 kg당이다. 통짜 요금과 같은
 * 중앙값에 섞으면 배수만큼 틀린다. 파이썬 쪽에서 기준 단위(㎡, m, kg)로
 * 환산해 두므로 여기서는 단위 이름만 붙이면 된다.
 */
export type FeeUnitName = 'whole' | 'panel' | 'area' | 'length' | 'weight' | 'volume' | 'volume_m3';
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
  /** 지역 수가 가장 많은 단위. 화면에서 먼저 말해야 하는 단위다. */
  primary: FeeUnitName;
  baseDate: string;
  /** primary가 맨 앞. 표본 3지역 미만인 단위는 아예 안 들어온다. */
  units: { name: FeeUnitName; stat: FeeUnit }[];
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

type RawStat = {
  primary: FeeUnitName;
  base_date: string;
} & Partial<Record<FeeUnitName, RawUnit>>;

const UNIT_ORDER: FeeUnitName[] = ['whole', 'panel', 'area', 'length', 'weight', 'volume', 'volume_m3'];

/** 화면에 그대로 쓰는 단위 이름. 파이썬의 UNIT_LABEL과 같아야 한다. */
export const UNIT_LABEL: Record<FeeUnitName, string> = {
  whole: '전후',
  panel: '1쪽당',
  area: '1㎡당',
  length: '1m당',
  weight: '1kg당',
  volume: '1ℓ당',
  volume_m3: '1㎥당',
};

const raw = feesJson as unknown as Record<string, RawStat>;

/** 수수료 데이터에 등장하는 시군구 전체(47개, 판단 19). 지역 선택 드롭다운에 쓴다. */
export const ALL_REGIONS: string[] = (() => {
  const set = new Set<string>();
  for (const item of Object.values(raw)) {
    for (const name of UNIT_ORDER) {
      const unit = item[name];
      if (unit) for (const region of Object.keys(unit.by_region)) set.add(region);
    }
  }
  return [...set].sort((a, b) => a.localeCompare(b, 'ko'));
})();

function toUnit(r: RawUnit | undefined): FeeUnit | null {
  if (!r) return null;
  const { by_region, ...rest } = r;
  return { ...rest, byRegion: by_region };
}

/** 수수료가 없는 품목이 있다. 음식물이나 재활용품은 애초에 대형폐기물이 아니다. */
export function feeFor(slug: string): FeeStat | null {
  const r = raw[slug];
  if (!r) return null;
  const units = [r.primary, ...UNIT_ORDER.filter((u) => u !== r.primary)]
    .map((name) => ({ name, stat: toUnit(r[name]) }))
    .filter((u): u is { name: FeeUnitName; stat: FeeUnit } => u.stat !== null);
  if (!units.length) return null;
  return { primary: r.primary, baseDate: r.base_date, units };
}
