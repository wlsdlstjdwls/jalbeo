-- 2차 확장 24개 발행 (batch5~8). scripts/publish_items.py 판정표 기준.

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('gabang','가방','{"백팩"}','조건부','바퀴가 달렸는지, 크기가 얼마나 되는지로 경로가 갈립니다.','섬유류',false,false,2460,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('keompyuteo','컴퓨터','{"데스크톱"}','무상수거','폐가전 무상수거 대상입니다. 저장장치부터 처리하세요.','폐전기·전자제품',false,false,2375,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('gireum','기름','{"폐유"}','전용수거함','튀김 기름과 엔진오일은 경로가 완전히 다릅니다.','유해폐기물',false,false,2230,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('seutiropom','스티로폼','{}','조건부','흰색이고 깨끗한 것만 재활용됩니다. 하나라도 어긋나면 종량제입니다.','발포수지류',false,false,2120,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('sopa','소파','{"쇼파"}','대형폐기물','인승 수만큼 수수료가 붙습니다. 버리기 전에 값이 붙는지 보세요.','가구류',false,false,1985,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('jangnangam','장난감','{"완구"}','조건부','플라스틱 완구는 2026년부터 재활용 대상입니다. 봉제·복합재질은 종량제입니다.','플라스틱류',false,false,1965,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('naengjanggo','냉장고','{}','무상수거','대형가전이라 한 대만으로도 무상방문수거가 됩니다.','폐전기·전자제품',false,false,1910,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('heonot','헌옷','{"헌 옷"}','재활용','의류수거함으로 갑니다. 다만 아무 섬유나 받지는 않습니다.','섬유류',false,false,1765,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('geoul','거울','{}','일반쓰레기','뒷면에 금속을 입힌 판유리라 유리병 수거함에 넣으면 안 됩니다.','유리류',false,false,1690,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('chaeksang','책상','{}','대형폐기물','지자체마다 나누는 축이 달라 항목 고르기가 더 어렵습니다.','가구류',false,false,1455,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('hwajangpum','화장품','{"화장품 용기"}','조건부','한 용기가 서너 재질입니다. 뜯어야 재활용됩니다.','복합재질',false,false,1310,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('hyangsu','향수','{"향수병"}','조건부','두꺼운 유리·금속 펌프·남은 알코올이 각각 다른 곳으로 갑니다.','복합재질',false,false,1280,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('gimchi','김치','{}','음식물','음식물쓰레기가 맞습니다. 헹구라는 안내는 지자체마다 갈립니다.','음식물',false,false,1040,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('chikinppyeo','치킨뼈','{"닭뼈"}','일반쓰레기','음식물쓰레기가 아닙니다. 뼈는 기준에서 빠져 종량제봉투로 갑니다.','음식물',false,false,960,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('jangpan','장판','{}','대형폐기물','값을 개수가 아니라 면적이나 길이로 매깁니다.','생활용품',false,false,930,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('moniteo','모니터','{}','조건부','크기에 따라 갈립니다. 작은 모니터 한 대만으로는 안 됩니다.','폐전기·전자제품',false,false,750,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('onsumaeteu','온수매트','{}','대형폐기물','본체와 매트가 한 벌이라 대형폐기물로 신고하는 쪽이 빠릅니다.','폐전기·전자제품',false,false,630,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('otjang','옷장','{}','대형폐기물','신고 화면에서는 대개 ''장롱'' 항목으로 접수합니다. 쪽수로 값이 갈립니다.','가구류',false,false,460,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('jangnong','장농','{}','대형폐기물','''장롱''의 흔한 오기지만 지자체 요금표에 이 표기가 실제로 쓰입니다.','가구류',false,false,455,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('otgeoli','옷걸이','{}','조건부','철사는 고철, 플라스틱은 종량제입니다. 훈령이 재활용에서 뺀 품목입니다.','복합재질',false,false,390,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('jeongijangpan','전기장판','{}','대형폐기물','폐가전 수거품목에 없습니다. 대형폐기물 경로가 확실합니다.','폐전기·전자제품',false,true,380,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('setakgi','세탁기','{}','무상수거','대형이라 한 대만 있어도 무상방문수거 신청이 됩니다.','폐전기·전자제품',false,false,340,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('hyudaepon','휴대폰','{"핸드폰"}','전용수거함','대형폐기물이 아닙니다. 전용 수거함에 넣으면 끝입니다.','폐전기·전자제품',false,false,300,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('byeongi','변기','{"양변기"}','대형폐기물','도기라 재활용 경로가 없습니다. 대형폐기물 신고뿐입니다.','도자기류',false,false,240,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();
