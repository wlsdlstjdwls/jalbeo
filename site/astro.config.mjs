// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// 배포 도메인 확정 전까지는 임시값. 도메인 연결 시 여기부터 바꾼다.
const SITE = process.env.SITE_URL ?? 'https://jalbeo.com';

export default defineConfig({
  site: SITE,
  // 관리자 화면은 색인 대상이 아니다 (robots.txt / meta 와 같은 기준).
  integrations: [sitemap({ filter: (page) => !new URL(page).pathname.startsWith('/admin') })],
  build: { format: 'directory' },
  // 영양제 -> 약 개명(2026-09-04). 옛 경로로 들어온 요청을 흘려보낸다.
  redirects: { '/yeongyangje': '/yak' },
});
