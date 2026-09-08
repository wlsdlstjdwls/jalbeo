-- 20차 확장 (235 -> 238). 근거는 실측 15차(저본체 별칭 192개, 386키워드, 합계 37,625).
-- 3 발행, 4 개명, 4 유지. 본체의 2배를 넘은 별칭이 11개였다(판단 12).
--
-- 이 회차는 신규 씨앗이 아니라 "이미 별칭으로 접어 둔 말"을 다시 잰 것이다.
-- 접어 두면 그 단어의 수요가 안 보이는데(판단 12), 본체가 작을수록 뒤집힘이
-- 크다. 드라이기는 본체 헤어드라이어의 57.6배, 고데기는 34.2배였다.
--
-- 발행 셋은 본체 첫 문단이 그 질문에 답하지 않는다(판단 40).
--   책(5,550) - 종이 페이지 첫 문단은 "코팅, 오염, 이물질부터 걸러야"다.
--     책을 찾는 사람은 표지를 떼야 하는지와 수십 권을 어떻게 내놓는지를 묻는다.
--   귤껍질(2,840) - 과일껍질 페이지에 '귤'이 한 글자도 없었다. 어미도 뒤집혔다
--     (분리수거 2,700 대 버리는법 140). 말린 껍질이 일반쓰레기라는 통설이
--     품목사전과 어긋나 검색이 몰린다(판단 38).
--   고데기(1,880) - 드라이기 페이지 첫 문단이 "훈령이 이름을 적어 둔 품목"인데
--     고데기는 훈령 예시에 이름이 없다. 그 문장이 고데기에는 거짓이다.
--     충전식 무선 제품이 흔해 전지 갈래가 하나 더 붙는다.
--
-- 개명 넷은 같은 물건인데 별칭이 훨씬 크다(판단 12). slug를 바꾸고 옛 경로는
-- site/vercel.json 301로 넘긴다.
--
-- 유지 넷. 양키캔들(765, 2.5배)은 브랜드명이고 양초 첫 문단이 그대로 답이다.
-- 전기포트(495, 5.0배)는 주전자의 부분집합이고 주전자 첫 문단이 "전기가
-- 들어가는지로 답이 완전히 갈립니다"로 그 질문에 답한다. 토너(460, 4.6배)와
-- 햇반용기(160, 2.9배)도 본체 첫 문단이 답이고 절대량이 작다.
--
-- 책 축의 절차 어미(헌책 방문수거 4,690, 헌책수거 1,630, 중고책기부 1,480 등)를
-- 다 더해도 약 15,000으로 새 가이드 하한선 16,035에 못 미친다(판단 20).
-- 헌책 수거와 기증은 책 페이지 안의 절로 둔다(판단 21).

-- 1) 개명 4건
-- 헤어드라이어(55) -> 드라이기(3,170). 57.6배. 같은 물건이다. 고데기는 별칭에서
-- 빼서 페이지로 올린다.
update items set
  slug = 'deuraigi',
  name = '드라이기',
  aliases = '{"헤어드라이어","헤어드라이기","헤어 드라이어","드라이어","매직기","에어랩"}',
  monthly_volume = 3170,
  updated_at = now()
where slug = 'heeodeuraieo';

-- 보온병(485) -> 텀블러(3,600). 7.4배. 품목사전이 보온병을 텀블러의 '배출방법이
-- 동일한 유사품목'으로 걸어 둔다.
update items set
  slug = 'teombeulleo',
  name = '텀블러',
  aliases = '{"보온병","스텐텀블러","스테인리스 텀블러","보온컵","마호병","진공 텀블러"}',
  verdict_line = '재질별로 갈라서 내고, 못 가르면 종량제봉투입니다.',
  monthly_volume = 3600,
  updated_at = now()
where slug = 'boonbyeong';

-- 마우스(590) -> 키보드(2,600). 4.4배. 다른 물건이지만 품목사전이 같은 문장으로
-- 답하고 페이지가 이미 둘을 같이 다룬다. 갈라 내면 판단 5번에 걸린다.
update items set
  slug = 'kibodeu',
  name = '키보드',
  aliases = '{"마우스","무선마우스","마우스패드","게이밍마우스","트랙볼","기계식키보드"}',
  monthly_volume = 2600,
  updated_at = now()
where slug = 'mauseu';

-- 보냉가방(360) -> 보냉백(2,130). 5.9배. 같은 물건의 다른 표기다.
update items set
  slug = 'bonaengbaek',
  name = '보냉백',
  aliases = '{"보냉가방","아이스박스","보랭백","쿨러백","보냉 가방"}',
  verdict_line = '은박과 부직포가 붙어 있어 분리가 안 됩니다. 크면 대형폐기물입니다.',
  monthly_volume = 2130,
  updated_at = now()
where slug = 'bonaenggabang';

-- 2) 신규 3개
insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('chaek','책','{"헌책","중고책","도서","단행본","양장본","만화책","동화책","전공서적","참고서","문제집"}','재활용',
   '종이류입니다. 코팅 표지와 스프링만 떼고, 양이 많으면 끈으로 묶습니다.',
   '종이류',false,false,5550,true,true),

  ('gyulkkeopjil','귤껍질','{"귤 껍질","감귤껍질","말린 귤껍질","한라봉 껍질","오렌지 껍질","귤 상자"}','음식물',
   '음식물쓰레기입니다. 말려도 음식물쓰레기입니다.',
   '음식물',false,true,2840,true,true),

  ('godegi','고데기','{"봉고데기","판고데기","헤어 아이론","아이롱","무선고데기","볼륨매직기"}','전용수거함',
   '소형가전 수거함입니다. 충전식은 통째로, 완전히 식혀서 냅니다.',
   '폐전기전자제품',false,false,1880,true,true)
on conflict (slug) do update set
  name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict,
  verdict_line=excluded.verdict_line, category=excluded.category,
  housing_split=excluded.housing_split, region_varies=excluded.region_varies,
  monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has,
  published=true, updated_at=now();

-- 3) 갈라 낸 말은 본체 별칭에서 뺀다. 남겨 두면 검색이 두 페이지에 다 걸리고
--    수수료 통계도 두 곳에 모인다(판단 39).
-- 종이에서 '책'을 뺀다. 교과서, 잡지, 노트는 종이에 둔다.
update items set aliases = array['신문','잡지','노트','스프링노트','상장','교과서','명함','쇼핑백','종이 쇼핑백','종이가방','종이봉투'], updated_at = now() where slug = 'jongi';
-- 과일껍질에서 '귤껍질'을 뺀다. 사과껍질(120)은 그대로 둔다.
update items set aliases = array['사과껍질','과일 껍질','배껍질','감껍질','멜론껍질','파인애플껍질'], updated_at = now() where slug = 'gwailkkeopjil';
