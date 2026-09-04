-- 8차 확장 (161 -> 164). 별칭에서 갈라져 나온 신규 품목 3개 + 호일 개명.
-- 근거: data/keywords/gate1-volumes-6.csv (실측 6차, 2026-09-04)
-- 대상 선정: data/keywords/gate1-batches-6.md (별칭 40개 재측정)
--
-- monthly_volume은 '{품목}버리는법' + '{품목}분리수거' 두 어미의 합이다.
--
-- 6차는 발굴이 아니라 **이미 접어 둔 별칭을 다시 재는** 회차다. 별칭을 붙이면
-- 그 단어의 수요가 안 보인다 (docs/18 12번). 40개 중 본체의 2배를 넘긴 것이
-- 5개였고, 그중 답이 갈리는 3개를 페이지로 올리고 1개를 개명한다.
-- 전기매트(365, 전기장판의 2.61배)는 같은 물건이고 배수가 낮아 별칭으로 둔다.

-- 1) 호일 -> 은박지. 같은 물건인데 수요가 5.5배 차이났다 (1,395 대 255).
--    본문이 이미 은박지와 쿠킹호일을 함께 다루고 있어 그대로 둔다.
--    검색량이 '분리수거' 어미에 몰려 있다 (1,380 대 15). 재활용이 되는지를
--    묻는 검색어인데 답은 안 된다는 쪽이다.
update items set
  slug = 'eunbakji',
  name = '은박지',
  aliases = '{"호일","쿠킹호일","알루미늄 호일","은박 접시","종이호일"}',
  monthly_volume = 1395,
  updated_at = now()
where slug = 'hoil';

-- 2) 신규 품목 3개
insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('leddeung','LED등','{"엘이디등","방등","거실등","평판등","천장등","등기구","LED 조명"}','조건부',
   '전구만 빼면 수거함, 등기구째면 대형폐기물입니다.',
   '복합재질',false,true,880,true,true),

  ('mogijang','모기장','{"침대 모기장","원터치 모기장","캠핑 모기장","유아 모기장","방충 텐트"}','조건부',
   '의류수거함에 넣으면 안 됩니다. 폴대를 빼면 대부분 종량제봉투입니다.',
   '섬유류',false,true,505,false,true),

  ('bapsang','밥상','{"교자상","다과상","좌탁","차탁자","소반","좌식 테이블"}','대형폐기물',
   '다리를 접어도 수수료 구간은 안 내려갑니다. 상판 크기로 잽니다.',
   '가구류',false,false,265,false,true);

-- 3) 갈라져 나간 별칭을 본체에서 뗀다.
--    led등(880)은 LED 전구(115)의 7.65배였다. 다만 같은 물건이 아니다.
--    램프는 형광등 수거함, 등기구는 대형폐기물이라 답이 갈린다. 개명이 아니라 분리다.
update items set
  aliases = '{"led","엘이디 전구","LED 벌브","LED 직관등"}',
  updated_at = now()
where slug = 'ledjeongu';

--    모기장(505)은 방충망(105)의 4.81배. 섬유 제품과 알루미늄 새시는 답이 다르다.
update items set
  aliases = '{"방충망 틀","창문 방충망","현관 방충망"}',
  updated_at = now()
where slug = 'bangchungmang';

--    밥상(265)과 교자상(60)을 식탁(80)에서 뗀다. 좌식 상은 수수료 구간이 따로 있다.
update items set
  aliases = '{"대리석 식탁","4인용 식탁","6인용 식탁","주방 테이블"}',
  updated_at = now()
where slug = 'siktak';
