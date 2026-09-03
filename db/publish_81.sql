-- 3차 확장 13개 발행 (68 -> 81). 92개 실측 수요 풀 중 volume>=55 잔여 백로그.
-- 가스렌지(gaseurenji)는 이미 가스레인지(gaseureinji) alias로 병합됐고,
-- 다이소(daiso)는 매장명이라 품목에서 제외했다 (docs/11 판단 그대로 적용).

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('chaekjang','책장','{}','대형폐기물','칸 수·재질과 상관없이 가구류라 대형폐기물 신고 대상입니다.','가구류',false,false,220,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('gimchinaengjanggo','김치냉장고','{}','무상수거','냉장고와 같은 대형가전 등급이라 1대만 있어도 무상방문수거가 됩니다.','폐전기·전자제품',false,false,170,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('hyeonggwangdeung','형광등','{}','전용수거함','수은이 소량 들어 있어 종량제봉투가 아니라 전용수거함으로 갑니다.','유해폐기물',false,false,160,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('heukchimdae','흙침대','{"돌침대","황토침대"}','대형폐기물','신고 화면에서는 대개 돌침대로 검색해야 나옵니다. 무게가 100kg을 넘습니다.','가구류',false,false,145,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('geumgo','금고','{}','대형폐기물','잠금장치와 전자부품이 있어 고철이 아니라 대형폐기물로 신고해야 합니다.','금속류',false,false,105,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('golpeugabang','골프가방','{}','조건부','클럽 포함 풀세트는 대형폐기물, 가방만 남았으면 종량제봉투도 가능합니다.','섬유류',false,false,100,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('jongikeop','종이컵','{}','일반쓰레기','양면 코팅 때문에 종이류 재활용 대상이 아닙니다. 종이팩과 다릅니다.','종이류',false,true,100,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('jongi','종이','{}','재활용','신문지·책·상자는 재활용입니다. 코팅·오염된 종이는 걸러야 합니다.','종이류',false,false,95,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('tail','타일','{}','조건부','대형폐기물이 아니라 공사장 생활폐기물입니다. 신고 경로 자체가 다릅니다.','건축폐자재',false,false,95,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('peteubyeong','페트병','{}','재활용','무색 투명 페트병만 별도 수거함입니다. 라벨을 떼고 압착해야 합니다.','플라스틱류',false,false,70,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('yangpakkeopjil','양파껍질','{}','일반쓰레기','섬유질이 질겨 사료화가 안 됩니다. 음식물쓰레기가 아닙니다.','음식물',false,false,65,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('eohang','어항','{"수족관"}','조건부','종량제봉투에 들어가는 소형은 일반쓰레기, 크면 대형폐기물입니다.','유리류',false,false,60,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('uyupaek','우유팩','{"두유팩"}','재활용','종이컵과 달리 종이팩(살균팩)으로 별도 분리배출 대상입니다.','종이류',false,false,55,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();
