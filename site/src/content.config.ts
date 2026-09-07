import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

/**
 * 품목 페이지 본문. 파일명이 곧 slug이고, DB의 items.slug와 맞춘다.
 *
 * 역할 분담:
 *   DB(Supabase) — 판정, 검색량, 플래그, 지역 데이터, 수수료 (표 형태, 대량, 자주 갱신)
 *   여기(git)    — 본문과 그 본문이 인용한 출처 (집필물, 이력이 중요)
 *
 * 본문은 품목마다 직접 조사해서 쓴다. 템플릿에 데이터만 갈아끼우면
 * scaled content abuse에 걸린다 (docs/02 리스크 1).
 */
const items = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/items' }),
  schema: z.object({
    // 본문이 인용한 근거. 출처 URL과 기준일자를 반드시 함께 (CLAUDE.md 작업 규칙)
    sources: z.array(z.object({
      title: z.string(),
      url: z.string().url(),
      asOf: z.string(),
    })).min(1),
    related: z.array(z.string()).default([]),  // 헷갈리는 유사 품목 slug
    // 이 품목이 절차를 말하고 있을 때 그 절차를 가진 가이드 slug.
    // 품목 페이지가 신고, 스티커, 무상수거 절차를 저마다 다시 설명하면
    // 같은 답을 하는 페이지가 늘어난다 (확정 판단 5번). 절차는 가이드가 갖고
    // 품목은 링크로 넘긴다.
    relatedGuides: z.array(z.string()).default([]),
    updated: z.string(),                       // 최종 확인일 YYYY-MM-DD

    // STEP 2에서 물어볼 갈래. 없으면 주거 형태(아파트 / 단독주택)를 쓴다 (lib/flow.ts).
    // 품목마다 진짜로 답이 갈리는 축이 다르므로 특수한 품목만 여기서 덮어쓴다.
    options: z.array(z.object({
      label: z.string(),
      hint: z.string(),
      head: z.string(),      // 결과 헤드라인
      body: z.string(),      // 결과 본문
    })).length(2).optional(),
    optionsNote: z.string().optional(),        // 옵션 카드 아래 설명문
    cta: z.object({                            // 결과 헤더 1차 버튼
      label: z.string(),
      href: z.string(),
      body: z.string(),
    }).optional(),
  }),
});

/**
 * 가이드 페이지. 품목이 아니라 '절차'를 묻는 검색어를 받는다.
 * (폐가전무료수거 51,810 / 대형폐기물스티커 16,790 - data/keywords/related-axes.csv)
 *
 * 품목 페이지와 URL 공간을 나눈다(/guides/). 품목 페이지가 루트를 다 먹기 때문이고,
 * 답의 성격도 다르다 - 품목은 "어디에 버리나", 가이드는 "어떻게 신청하나"다.
 */
const guides = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/guides' }),
  schema: z.object({
    title: z.string(),        // h1. 개행은 본문에서 쓰지 않는다
    // <title>. 검색 수요가 h1과 다른 말로 몰려 있으면 여기에 둘 다 태운다
    // (무료수거 51,810 대 무상수거 17,830). 없으면 title을 그대로 쓴다
    seoTitle: z.string().optional(),
    lede: z.string(),         // h1 아래 한 줄. 답을 여기서 먼저 준다
    description: z.string(),  // meta description
    // 본문이 인용한 근거. 출처 URL과 기준일자를 반드시 함께 (CLAUDE.md 작업 규칙)
    sources: z.array(z.object({
      title: z.string(),
      url: z.string().url(),
      asOf: z.string(),
    })).min(1),
    related: z.array(z.string()).default([]),   // 이어보면 좋은 품목 slug
    relatedGuides: z.array(z.string()).default([]),
    updated: z.string(),
  }),
});

export const collections = { items, guides };
