-- 10차 확장 (166 -> 167). 사이트 내 검색어 로그 첫 신호.
-- 근거: search_queries hit_count=0, 방문자 1명 테스트성 검색이라 표본은 얇지만
-- 겹치는 발행 품목이 없어 조사해 바로 발행했다(docs/20 13번, 실측은 생략).

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('kaettawo','캣타워','{"캣폴"}','조건부',
   '소형이고 분해되면 재질별로 종량제, 안 되면 대형폐기물 신고입니다.',
   '복합재질',false,true,null,true,true)
on conflict (slug) do update set
  name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict,
  verdict_line=excluded.verdict_line, category=excluded.category,
  housing_split=excluded.housing_split, region_varies=excluded.region_varies,
  monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has,
  published=true, updated_at=now();
