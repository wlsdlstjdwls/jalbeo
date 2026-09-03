// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// 배포 도메인 확정 전까지는 임시값. 도메인 연결 시 여기부터 바꾼다.
const SITE = process.env.SITE_URL ?? 'https://jalbeo.com';

export default defineConfig({
  site: SITE,
  integrations: [sitemap()],
  build: { format: 'directory' },
});
