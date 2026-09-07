-- 검색어 로그에서 온 별칭 1건 (docs/32).
-- '썬크'로 친 검색이 0건이었다. 화장품 aliases에 '선크림'은 있는데
-- '썬크림'이 없다. 오타가 아니라 둘 다 쓰이는 표기라 별칭으로 넣는다.
-- (오타는 페이지가 아니라 검색이 받는다 - lib/search.ts의 jamo 폴백)
--
-- 순서를 손으로 적는다. distinct unnest 로 넣으면 순서가 흐트러지는데
-- 별칭은 화면에 그 순서로 노출된다.

update items set
  aliases = array['화장품 공병', '남은 화장품', '선크림', '썬크림', '화장품 용기'],
  updated_at = now()
where slug = 'hwajangpum';
