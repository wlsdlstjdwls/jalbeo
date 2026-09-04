/**
 * 화면에 쓰는 숫자 상수. 품목이 100~150개로 늘어나도 이 값들만 보고
 * 판단할 수 있게 이름을 붙여 한 곳에 모은다.
 */

/** 홈 목록 초기 노출 개수이자 '더보기' 클릭당 추가 개수 (pages/index.astro). */
export const HOME_PAGE_SIZE = 10;

/** '헷갈리는 품목' 카드 최대 노출 개수 (pages/[...slug].astro). */
export const RELATED_LIMIT = 4;
