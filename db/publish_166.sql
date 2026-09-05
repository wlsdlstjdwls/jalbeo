-- 9차 확장 (164 -> 166). 재크롤 3차 신규후보 2개.
-- 근거: data/keywords/candidates-r3-triage.csv (재크롤 2차 크롤 결과의 수기 판정)
--
-- 동물사체, 폐목재 둘 다 크롤 빈도가 바닥(freq=1)이라 실측(네이버 키워드도구)을
-- 생략했다. 신규후보라 별칭 판정처럼 배수를 다툴 상대가 없고, 이미 최하위라
-- 실측해도 우선순위가 안 뒤집힌다. monthly_volume은 미측정이므로 null이다.

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('dongmulsache','동물사체','{"반려동물 사체","강아지 사체","고양이 사체","애완동물 사체","동물 시체"}','조건부',
   '병원에서 죽었으면 병원이 처리합니다. 집에서 죽었으면 종량제봉투나 장묘업체, 매장은 과태료 100만원 이하입니다.',
   '생활폐기물',false,true,null,false,true),

  ('pyemokjae','폐목재','{"목재 쓰레기","나무 폐기물","각목","합판 조각","나무 팔레트"}','조건부',
   '손바닥 크기 자투리는 종량제, 못 박힌 원목 조각이나 큰 판자는 대형폐기물 신고입니다.',
   '건축폐자재',false,true,null,true,true)
on conflict (slug) do update set
  name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict,
  verdict_line=excluded.verdict_line, category=excluded.category,
  housing_split=excluded.housing_split, region_varies=excluded.region_varies,
  monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has,
  published=true, updated_at=now();
