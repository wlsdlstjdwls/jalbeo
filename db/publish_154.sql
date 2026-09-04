-- 6차 확장 (148 -> 154). 신규 품목 6개 + 영양제 페이지 개명.
-- 근거: data/keywords/gate1-volumes-3.csv (실측 3차, 2026-09-04)
--
-- monthly_volume은 '{품목}버리는법' + '{품목}분리수거' 두 어미의 합이다.
-- 1차 실측값(gate1-volumes.csv)은 연관어 덤프라 품목마다 어미 커버리지가
-- 달라 스케일이 다르다. 두 값을 한 컬럼에서 정렬에 쓸 때 이 점을 감안한다.

-- 1) 영양제 -> 약. 검색 수요가 92배 차이났다 (약 4,140 대 영양제 45).
--    본문은 이미 약과 영양제를 함께 다루고 있어 그대로 둔다.
update items set
  slug = 'yak',
  name = '약',
  aliases = '{"영양제","폐의약품","조제약","알약","약봉지"}',
  verdict_line = '종량제봉투와 변기에 버리면 안 됩니다. 약국이나 주민센터의 폐의약품 수거함으로 갑니다.',
  monthly_volume = 4265,
  updated_at = now()
where slug = 'yeongyangje';

-- 2) 신규 품목 6개
insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('gawi','가위','{"칼","부엌가위","문구용 가위","커터"}','일반쓰레기',
   '금속이지만 고철로 안 받습니다. 종이에 싸서 종량제봉투로 갑니다.',
   '금속류',false,true,2680,false,true),
  ('jeonseon','전선','{"케이블","전기선","랜선","연장선","전선줄"}','조건부',
   '한두 가닥은 종량제봉투, 한 뭉치면 고철입니다. 피복은 벗기지 않습니다.',
   '고철류',false,false,1380,false,true),
  ('namujeotgarak','나무젓가락','{"일회용 젓가락","대나무젓가락","이쑤시개","나무 꼬치"}','일반쓰레기',
   '음식물이 아닙니다. 양념이 묻어 있어도 종량제봉투로 갑니다.',
   '생활용품',false,true,985,false,true),
  ('kikbodeu','킥보드','{"전동킥보드","어린이 킥보드","씽씽이"}','조건부',
   '전동이면 배터리부터 분리합니다. 본체는 대형폐기물 신고 대상입니다.',
   '폐전기전자제품',false,false,580,false,true),
  ('gonggicheongjeonggi','공기청정기','{"공청기","가정용 공기청정기"}','무상수거',
   '1대만 있어도 무료로 가져갑니다. 필터는 따로 종량제봉투입니다.',
   '폐전기전자제품',false,false,460,false,true),
  ('jeongsugi','정수기','{"냉온수기","렌탈 정수기","얼음정수기"}','조건부',
   '렌탈이면 버리는 게 아니라 반납입니다. 내 것이고 전기를 쓰면 무상수거 대상입니다.',
   '폐전기전자제품',false,false,370,false,true)
on conflict (slug) do update set
  name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict,
  verdict_line=excluded.verdict_line, category=excluded.category,
  region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume,
  published=true, updated_at=now();
