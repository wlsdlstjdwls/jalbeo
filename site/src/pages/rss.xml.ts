import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';
import { isProductionHost } from '../lib/site';
import { items as dbItems } from '../lib/items';

/**
 * RSS 2.0 피드.
 *
 * 사이트맵과 역할이 다르다. 사이트맵은 "이 사이트에 어떤 URL이 있나"이고
 * RSS는 "최근에 뭐가 바뀌었나"다. 네이버 서치어드바이저는 둘을 따로 받고,
 * 신규 문서 수집은 RSS 쪽이 빠르다 (사이트맵만 넣어 두면 수집이 늦다).
 *
 * 정렬 기준은 본문 프런트매터의 `updated`(최종 확인일)다. 발행일이 아니라
 * 확인일인 것이 맞다 - 이 사이트는 규정이 바뀌면 옛 페이지를 고치고,
 * 고친 페이지야말로 재수집이 필요한 문서다.
 *
 * 색인 판정은 robots.txt.ts, Base.astro와 같은 기준을 쓴다 (lib/site.ts).
 * 미리보기 배포에서 피드가 나가면 jalbeo.vercel.app이 먼저 수집된다.
 */

const FEED_TITLE = '잘버려 - 쓰레기 배출 안내';
const FEED_DESCRIPTION =
  '품목별 버리는법과 분리수거 방법, 대형폐기물 수수료와 배출 절차를 근거와 함께 정리한다.';

function escapeXml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/** 'YYYY-MM-DD'를 RFC 822로. 기준일자는 한국 날짜이므로 KST 자정으로 읽는다. */
function toRfc822(day: string): string {
  return new Date(`${day}T00:00:00+09:00`).toUTCString();
}

interface FeedEntry {
  title: string;
  path: string;
  description: string;
  updated: string;
}

export const GET: APIRoute = async ({ site }) => {
  if (!site || !isProductionHost(site.host)) {
    return new Response('Not found', { status: 404 });
  }

  const [bodies, guides] = await Promise.all([
    getCollection('items'),
    getCollection('guides'),
  ]);
  const byId = new Map(bodies.map((b) => [b.id, b]));

  // 페이지가 실제로 있는 품목만 (DB에 발행 표시가 있고 본문도 있는 것).
  // [...slug].astro의 getStaticPaths와 같은 조건이라야 피드에 404가 안 섞인다.
  const itemEntries: FeedEntry[] = dbItems
    .filter((row) => byId.has(row.slug))
    .map((row) => ({
      title: `${row.name} 버리는법, 분리수거 방법`,
      path: `/${row.slug}/`,
      // 답을 요약문에서 먼저 준다. 페이지 meta description과 같은 문장이다.
      description: `${row.name}은(는) ${row.verdict}. ${row.verdict_line}`,
      updated: byId.get(row.slug)!.data.updated,
    }));

  const guideEntries: FeedEntry[] = guides.map((entry) => ({
    title: entry.data.seoTitle ?? entry.data.title,
    path: `/guides/${entry.id}/`,
    description: entry.data.description,
    updated: entry.data.updated,
  }));

  const entries = [...itemEntries, ...guideEntries].sort((a, b) =>
    a.updated === b.updated ? a.title.localeCompare(b.title, 'ko') : b.updated.localeCompare(a.updated),
  );

  const feedUrl = new URL('rss.xml', site).href;
  const lastBuild = entries.length > 0 ? toRfc822(entries[0].updated) : new Date().toUTCString();

  const body = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
    '<channel>',
    `<title>${escapeXml(FEED_TITLE)}</title>`,
    `<link>${escapeXml(site.href)}</link>`,
    `<description>${escapeXml(FEED_DESCRIPTION)}</description>`,
    '<language>ko</language>',
    `<lastBuildDate>${lastBuild}</lastBuildDate>`,
    `<atom:link href="${escapeXml(feedUrl)}" rel="self" type="application/rss+xml" />`,
    ...entries.map((entry) => {
      const url = new URL(entry.path, site).href;
      return [
        '<item>',
        `<title>${escapeXml(entry.title)}</title>`,
        `<link>${escapeXml(url)}</link>`,
        `<guid isPermaLink="true">${escapeXml(url)}</guid>`,
        `<description>${escapeXml(entry.description)}</description>`,
        `<pubDate>${toRfc822(entry.updated)}</pubDate>`,
        '</item>',
      ].join('');
    }),
    '</channel>',
    '</rss>',
    '',
  ].join('\n');

  return new Response(body, {
    headers: { 'Content-Type': 'application/rss+xml; charset=utf-8' },
  });
};
