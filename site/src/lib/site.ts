/**
 * 정식 도메인. 이 값과 다른 호스트(미리보기 배포 등)에서는 색인을 막는다.
 *
 * Base.astro(meta robots)와 robots.txt.ts가 반드시 같은 기준으로 판정해야 한다.
 * 둘이 따로 정의되면 도메인 연결 시 한쪽만 고치는 실수가 나고, jalbeo.vercel.app이
 * 먼저 색인되어 게이트 2(색인 테스트) 결과가 오염된다.
 */
export const PRODUCTION_HOST = 'jalbeo.com';

export function isProductionHost(host: string): boolean {
  return host === PRODUCTION_HOST || host.endsWith(`.${PRODUCTION_HOST}`);
}
