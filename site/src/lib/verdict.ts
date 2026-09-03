/**
 * 판정별 색. 컬러블록 컨셉이라 색은 배경으로만 쓰고 글자는 항상 #111이다.
 * 색만으로 구분되지 않게 판정 텍스트 라벨을 항상 함께 표기한다.
 */
export const VERDICT_BG: Record<string, string> = {
  '재활용': '#c9f24d',
  '무상수거': '#a9c7ff',
  '전용수거함': '#d5c2ff',
  '대형폐기물': '#f7c65a',
  '음식물': '#8fd9a8',
  '조건부': '#e4e0d6',
  '일반쓰레기': '#ff9f8f',
};

/** 칩·목록 정렬 순서 */
export const VERDICT_ORDER = [
  '재활용', '무상수거', '전용수거함', '대형폐기물', '음식물', '조건부', '일반쓰레기',
];

export function bg(verdict: string): string {
  return VERDICT_BG[verdict] ?? VERDICT_BG['조건부'];
}
