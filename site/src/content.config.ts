import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

/**
 * 품목 페이지 1개 = 마크다운 1개.
 *
 * 본문은 품목마다 직접 조사해서 쓴다. 템플릿에 데이터만 갈아끼우면
 * scaled content abuse에 걸린다 (docs/02 리스크 1).
 */
const items = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/items' }),
  schema: z.object({
    // 검색어와 표기
    name: z.string(),                       // 품목명 (H1에 쓰임)
    aliases: z.array(z.string()).default([]), // 쇼파/소파처럼 표기가 갈리는 경우

    // 최상단 O·X 판정
    verdict: z.enum(['재활용', '일반쓰레기', '대형폐기물', '전용수거함', '조건부']),
    verdictLine: z.string(),                // 한 줄 요약. 판정 바로 아래 굵게
    category: z.string().optional(),        // 재활용일 때 어느 분류인지

    // 실측에서 나온 축 (docs/07)
    housing: z.boolean().default(false),    // 아파트/단독 분기가 필요한가 (수식어 1위)
    regionVaries: z.boolean().default(false), // 지자체마다 답이 갈리는가 (16개 품목)

    // 근거. 출처 URL과 기준일자를 반드시 함께 (CLAUDE.md 작업 규칙)
    sources: z.array(z.object({
      title: z.string(),
      url: z.string().url(),
      asOf: z.string(),                     // 기준일자 YYYY-MM-DD
    })).min(1),

    related: z.array(z.string()).default([]), // 헷갈리는 유사 품목 slug
    monthlyVolume: z.number().optional(),     // 게이트 1 실측치 (우선순위 판단용)
    updated: z.string(),                      // 최종 확인일 YYYY-MM-DD
  }),
});

export const collections = { items };
