-- 11차 확장 (167 -> 168) + 별칭 3건. 근거는 docs/32.
-- 원천은 사이트 검색어 로그다(못 찾은 검색). 실측 10차로 다섯 주제를 쟀고
-- 그중 속옷만 페이지가 됐다 -- 검색량 1,550으로 헌옷(585)의 2.6배인데
-- 헌옷 페이지가 속옷을 한 글자도 안 답하고 있었다(판단 12번).

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('sogot','속옷','{"팬티","브래지어","브라","내복","런닝셔츠"}','조건부',
   '입던 것은 종량제봉투입니다. 안 뜯은 새것만 의류수거함입니다.',
   '섬유류',false,false,1550,false,true)
on conflict (slug) do update set
  name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict,
  verdict_line=excluded.verdict_line, category=excluded.category,
  housing_split=excluded.housing_split, region_varies=excluded.region_varies,
  monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has,
  published=true, updated_at=now();

-- 침대커버: 답이 이불 페이지에 이미 있다(커버는 벗겨서 의류수거함).
-- 검색은 침대(대형폐기물)로 잘못 걸리고 있었다.
update items set
  aliases = array['여름이불', '패드', '극세사 이불', '겨울이불', '차렵이불',
                  '침대커버', '이불커버', '침대시트'],
  updated_at = now()
where slug = 'ibul';

-- 피규어: 검색량 90. 답이 장난감과 같아 별칭이다(판단 5번, 8번).
update items set
  aliases = array['아이 장난감', '플라스틱 장난감', '완구', '나무장난감',
                  '블록', '피규어'],
  updated_at = now()
where slug = 'jangnangam';
