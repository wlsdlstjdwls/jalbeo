import type { APIRoute } from 'astro';

/**
 * 지금 서빙 중인 배포의 커밋 SHA. 빌드 시점에 Vercel이 넣어 주는 값을 정적 파일로 굳힌다.
 *
 * .github/workflows/indexnow-submit.yml 이 배포 성공 이벤트를 받은 직후 이 파일을 폴링해
 * 운영 도메인이 새 배포로 전환됐는지(alias 전환 완료) 확인하고 나서 IndexNow를 제출한다.
 * 성공 이벤트 직후엔 도메인이 아직 이전 배포를 가리킬 수 있어, 그때 제출하면 이전
 * 사이트맵을 읽거나 키 파일을 못 찾아 403이 난다(smokespot 2026-09-07 실증).
 * 로컬 빌드에서는 값이 없어 null.
 */
export const GET: APIRoute = () => {
  const body = JSON.stringify({ commit: process.env.VERCEL_GIT_COMMIT_SHA ?? null });
  return new Response(body, {
    headers: { 'Content-Type': 'application/json; charset=utf-8' },
  });
};
