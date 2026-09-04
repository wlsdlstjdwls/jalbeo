import type { APIRoute } from 'astro';
import { isProductionHost } from '../lib/site';

/**
 * 도메인 연결 전에는 색인을 막는다.
 *
 * jalbeo.vercel.app 이 먼저 색인되면 게이트 2(색인 테스트) 결과가 오염된다.
 * 나중에 도메인을 붙이고 301을 걸어도 색인 타이밍이 리셋되므로,
 * 정식 도메인에서만 크롤링을 허용한다. 판정 기준은 Base.astro와 공유 (lib/site.ts).
 */

export const GET: APIRoute = ({ site }) => {
  const isProduction = isProductionHost(site?.host ?? '');

  const body = isProduction
    ? [
        'User-agent: *',
        'Allow: /',
        '# 관리자 화면. 색인 대상이 아니다 (src/pages/admin.astro)',
        'Disallow: /admin',
        '',
        `Sitemap: ${new URL('sitemap-index.xml', site).href}`,
        '',
      ].join('\n')
    : [
        '# 도메인 연결 전 임시 차단 (src/pages/robots.txt.ts)',
        'User-agent: *',
        'Disallow: /',
        '',
      ].join('\n');

  return new Response(body, {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
};
