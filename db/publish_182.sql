-- 13차 확장 (174 -> 182). 근거는 docs/34, 실측 11차 중위권.
-- 자르는 기준은 검색량이 아니라 답이 기존 페이지와 갈리는지다(판단 8번).
-- 9주제를 조사해 8개를 냈고, 양말은 답이 속옷과 같아 별칭으로 넘겼다.
--
-- 항아리는 조사 전 예상(그릇, 화분과 겹침)이 뒤집힌 경우다. 재질 답은 같은데
-- 수수료 축이 완전히 갈렸다 -- 그릇은 5곳 등재인데 항아리는 35곳이고,
-- kg당, 20cm마다 같은 곱셈 단위를 쓴다(판단 24번). 마대냐 신고냐가 갈린다.

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('tenteu','텐트','{"캠핑텐트","원터치텐트","그늘막","타프","천막"}','조건부',
   '폴대는 고철, 천은 종량제봉투입니다. 원터치는 대형폐기물입니다.',
   '복합재질',false,true,1140,true,true),

  ('beullaindeu','블라인드','{"버티컬","버티칼","롤스크린","우드블라인드","콤비블라인드"}','대형폐기물',
   '쪽당으로 받는 곳이 있습니다. 알루미늄이면 뜯어서 고철로 냅니다.',
   '생활용품',false,true,1110,true,true),

  ('sseuregitong','쓰레기통','{"휴지통","분리수거함","페달휴지통","음식물쓰레기통","플라스틱통"}','일반쓰레기',
   '플라스틱인데 재활용은 안 됩니다. 봉투에 들어가면 봉투입니다.',
   '플라스틱류',false,true,980,true,true),

  ('dotjari','돗자리','{"대자리","대나무돗자리","은박돗자리","왕골돗자리","피크닉매트"}','일반쓰레기',
   '재질과 상관없이 재활용은 없습니다. 대나무는 실을 끊으면 봉투에 들어갑니다.',
   '생활용품',false,true,885,true,true),

  ('byeoksigye','벽시계','{"시계","탁상시계","알람시계","뻐꾸기시계","추시계"}','조건부',
   '건전지를 빼고 나면 가전이 아닙니다. 몸통은 종량제봉투입니다.',
   '생활용품',false,true,860,true,true),

  ('mikseogi','믹서기','{"녹즙기","블렌더","분쇄기","핸드블렌더","원액기"}','무상수거',
   '소형가전이라 값을 안 내는 곳이 있습니다. 유리 용기와 칼날은 따로 냅니다.',
   '폐전기전자제품',false,true,585,true,true),

  ('hangari','항아리','{"장독","옹기","김칫독","단지","질그릇"}','대형폐기물',
   '도자기라 재활용은 없습니다. 크면 마대가 아니라 신고입니다.',
   '도자기류',false,true,555,true,true),

  ('gyeranpan','계란판','{"달걀판","계란포장","에그트레이","계란트레이"}','조건부',
   '종이면 종이류, 아니면 플라스틱류입니다. 투명해도 페트병 통은 아닙니다.',
   '종이류',false,false,495,true,true)
on conflict (slug) do update set
  name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict,
  verdict_line=excluded.verdict_line, category=excluded.category,
  housing_split=excluded.housing_split, region_varies=excluded.region_varies,
  monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has,
  published=true, updated_at=now();

-- 양말(765)은 페이지를 안 낸다. 답이 속옷과 같은 선(재사용 여부)이고
-- 속옷(1,550)이 이미 두 배라 순위가 안 바뀐다(판단 14번).
-- 대신 별칭으로 받고 속옷 본문에 양말 절을 세웠다.
update items set
  aliases = array['팬티', '브래지어', '브라', '내복', '런닝셔츠', '양말', '스타킹'],
  updated_at = now()
where slug = 'sogot';

-- 커튼: 블라인드가 별도 페이지가 됐다. 본문의 블라인드 문단은 링크로 넘긴다.
-- 별칭에는 원래 블라인드가 없었으므로 여기서는 바꿀 게 없다.
