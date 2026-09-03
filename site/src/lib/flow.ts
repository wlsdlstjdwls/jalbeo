/**
 * 3단계 플로우(품목 → 조건 → 결과)의 STEP 2·3 데이터.
 *
 * 품목별 조건이 특수하면 마크다운 frontmatter의 options/optionsNote/cta로 덮어쓴다.
 * 없으면 주거 형태(아파트 / 단독·빌라)를 기본 갈래로 쓴다.
 */
export interface FlowOption {
  label: string;
  hint: string;
  /** 카드 배경색을 고르는 판정 키 */
  tone: string;
  /** 결과 헤드라인 */
  head: string;
  /** 결과 본문 */
  body: string;
}

export const HOUSING_OPTIONS: FlowOption[] = [
  {
    label: '아파트',
    hint: '단지 내 배출 장소 있음',
    tone: '재활용',
    head: '관리사무소에 먼저 물어보세요.',
    body: '단지 안에 집하 장소나 전용수거함이 있는 경우가 많습니다. 있으면 신고·수수료 없이 처리되는 경우도 있어 가장 빠른 확인 경로입니다.',
  },
  {
    label: '단독 · 빌라',
    hint: '수거차량 진입 여부가 관건',
    tone: '조건부',
    head: '배출 장소와 요일을 먼저 확인하세요.',
    body: '골목이 좁아 수거차량이 들어오지 못하면 예약할 때 미리 알려야 합니다. 지자체별로 배출 요일과 지정 장소가 정해져 있습니다.',
  },
];

export const HOUSING_NOTE =
  '같은 품목이라도 주거 형태에 따라 배출 장소와 절차가 달라집니다. 아파트는 단지 내 경로가 있는 경우가 많습니다.';

export interface Cta {
  label: string;
  href: string;
  body: string;
}

/** 판정별 기본 다음 행동. 품목이 특수하면 frontmatter의 cta가 이긴다. */
export const CTA: Record<string, Cta> = {
  '무상수거': {
    label: '1599-0903 예약',
    href: 'tel:15990903',
    body: '폐가전 무상방문수거. 전화 또는 홈페이지 예약, 수수료 없음. 평일 08:00~18:00 운영.',
  },
  '대형폐기물': {
    label: '지자체 신고 확인',
    href: 'https://www.gov.kr',
    body: '거주 지자체 홈페이지나 주민센터에서 신고하고 스티커를 받습니다. 품목·크기별 수수료는 지자체마다 다릅니다.',
  },
  '재활용': {
    label: '분리배출 기준 보기',
    href: 'https://www.recycling-info.or.kr',
    body: '재질별로 나눠 배출하면 그대로 자원이 됩니다. 이물질 제거와 재질 분리가 핵심입니다.',
  },
  '전용수거함': {
    label: '수거함 위치 확인',
    href: 'https://www.gov.kr',
    body: '주민센터·아파트 단지에 설치된 전용수거함으로 배출합니다. 설치 여부는 지자체마다 다릅니다.',
  },
  '조건부': {
    label: '판단 기준 보기',
    href: 'https://www.recycling-info.or.kr',
    body: '같은 품목이라도 재질과 크기에 따라 경로가 갈립니다. 아래 기준을 먼저 확인하세요.',
  },
  '일반쓰레기': {
    label: '지자체 기준 확인',
    href: 'https://www.gov.kr',
    body: '재활용이 되지 않는 품목입니다. 봉투에 들어가지 않으면 대형폐기물로 신고합니다.',
  },
};

export function ctaFor(verdict: string): Cta {
  return CTA[verdict] ?? CTA['조건부'];
}
