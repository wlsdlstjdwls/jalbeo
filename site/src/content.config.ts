import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

/**
 * 품목 페이지 본문. 파일명이 곧 slug이고, DB의 items.slug와 맞춘다.
 *
 * 역할 분담:
 *   DB(Supabase) — 판정·검색량·플래그·지역 데이터·수수료 (표 형태, 대량, 자주 갱신)
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
    updated: z.string(),                       // 최종 확인일 YYYY-MM-DD

    // STEP 2에서 물어볼 갈래. 없으면 주거 형태(아파트 / 단독·빌라)를 쓴다 (lib/flow.ts).
    // 품목마다 진짜로 답이 갈리는 축이 다르므로 특수한 품목만 여기서 덮어쓴다.
    options: z.array(z.object({
      label: z.string(),
      hint: z.string(),
      tone: z.string(),      // 카드 배경색을 고르는 판정 키
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

export const collections = { items };
