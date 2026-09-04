-- 7차 확장 (154 -> 161). 신규 품목 7개 + 별칭 재배치.
-- 근거: data/keywords/gate1-volumes-5.csv (실측 5차, 2026-09-04)
-- 후보 발굴: data/keywords/candidates-r2-triage.csv (재크롤 2차)
--
-- monthly_volume은 '{품목}버리는법' + '{품목}분리수거' 두 어미의 합이다.
-- 에어컨만 예외로 '{품목}무상수거' + '{품목}철거비용'이다. 품목 어미로는 50이었는데
-- 어미가 품목이 아니라 서비스에 붙어 있었다 (docs/14 2번, docs/18).

-- 1) 신규 품목 7개
insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('yogamaeteu','요가매트','{"홈트매트","운동매트","필라테스매트","트레이닝매트"}','조건부',
   '플라스틱류로 내면 안 됩니다. 잘라서 종량제봉투에 담는 것이 기본입니다.',
   '복합재질',false,true,3370,true,true),

  ('eeokeon','에어컨','{"벽걸이에어컨","스탠드에어컨","실외기","창문형에어컨","이동식에어컨"}','무상수거',
   '수거는 공짜인데 철거는 유료입니다. 떼어 놓아야 가져갑니다.',
   '폐전기전자제품',false,false,2220,true,true),

  ('sillikon','실리콘','{"실리콘식기","실리콘주방용품","실리콘뚜껑","실리콘케이스","실리콘몰드"}','일반쓰레기',
   '플라스틱이 아닙니다. 열로 안 녹아 재활용 공정에 못 들어갑니다.',
   '생활용품',false,true,1500,true,true),

  ('gomu','고무','{"고무장갑","고무패킹","고무호스","고무줄","라텍스장갑","니트릴장갑"}','일반쓰레기',
   '천연이든 합성이든 종량제봉투입니다. 가황된 고무는 다시 못 녹입니다.',
   '생활용품',false,true,1010,true,true),

  ('gyujotobalmaeteu','규조토 발매트','{"규조토매트","규조토","주방 발매트","발매트"}','일반쓰레기',
   '종량제봉투가 아니라 불연성 마대입니다. 흙을 굳힌 물건이라 타지 않습니다.',
   '도자기류',false,true,955,false,true),

  ('peojeulmaeteu','퍼즐매트','{"놀이매트","놀이방매트","층간소음매트","폼매트","롤매트","코일매트"}','조건부',
   '낱장이면 종량제봉투, 한 방 분량이면 대형폐기물입니다.',
   '복합재질',false,true,835,true,true),

  ('agiyokjo','아기욕조','{"유아욕조","아기 욕조","신생아욕조","욕조"}','조건부',
   '플라스틱이지만 플라스틱류로 못 냅니다. 크기로 갈립니다.',
   '생활용품',false,true,435,false,true);

-- 2) 별칭 재배치.
--    범퍼침대(105)가 놀이방매트, 범퍼매트를 달고 있었는데 실측해 보니 그 별칭 쪽이
--    8배 크다 (퍼즐매트 835, 놀이매트 255). docs/14의 영양제 -> 약과 같은 자리다.
--    다만 범퍼침대와 퍼즐매트는 다른 물건이므로 개명이 아니라 별칭을 옮긴다.
update items set
  aliases = '{}',
  updated_at = now()
where slug = 'beompeochimdae';

--    러그가 매트 계열을 통째로 들고 있었다. 요가매트(3,370)가 러그(1,555)보다 크다.
--    요가매트와 발매트는 각자 페이지가 생겼으므로 러그에서 뺀다.
--    카펫 계열만 남긴다.
update items set
  aliases = '{"카페트","카펫","타일카페트"}',
  updated_at = now()
where slug = 'reogeu';

--    전기매트는 전기장판이 맞다 (열선 제품).
update items set
  aliases = array_append(aliases, '전기매트'),
  updated_at = now()
where slug = 'jeongijangpan' and not ('전기매트' = any(aliases));

--    차량 매트는 고무 매트다.
update items set
  aliases = array_append(aliases, '차량매트'),
  updated_at = now()
where slug = 'gomu' and not ('차량매트' = any(aliases));

--    실측에서 떨어진 것들을 별칭으로 접는다 (기준선 300 미달).
--    은박비닐 150 -> 비닐, 화환 125 -> 조화, 폐목재 20 -> 문짝은 답이 달라 접지 않는다.
update items set
  aliases = array_append(aliases, '은박비닐'),
  updated_at = now()
where slug = 'binil' and not ('은박비닐' = any(aliases));

update items set
  aliases = array_append(aliases, '화환'),
  updated_at = now()
where slug = 'johwa' and not ('화환' = any(aliases));
