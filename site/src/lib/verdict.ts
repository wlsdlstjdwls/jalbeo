/** 판정별 색 토큰. 한 눈에 갈래가 보이게 색을 나눈다. */
export const VERDICT_TONE: Record<string, string> = {
  '재활용': 'green',
  '무상수거': 'blue',
  '전용수거함': 'violet',
  '대형폐기물': 'amber',
  '조건부': 'slate',
  '일반쓰레기': 'red',
};

export function tone(verdict: string): string {
  return VERDICT_TONE[verdict] ?? 'slate';
}
