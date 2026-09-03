-- 신규 24개 품목 발행 (본문 집필 완료분). scripts/publish_items.py 판정표 기준.
-- 재실행 안전: slug 충돌 시 갱신한다.

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('ibul','이불','{}','대형폐기물','의류수거함에 넣으면 안 됩니다. 부피가 커서 대부분 대형폐기물입니다.','섬유류',false,false,26905,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('huraipaen','후라이팬','{"프라이팬"}','조건부','코팅 팬은 고철이 아닙니다. 통주물·스테인리스만 고철로 갑니다.','금속류',false,true,12100,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('yuri','유리','{}','일반쓰레기','판유리·거울·내열유리는 재활용이 안 됩니다. 불연성 마대로 갑니다.','유리류',false,false,11395,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('baeteori','배터리','{}','전용수거함','일반쓰레기에 넣으면 안 됩니다. 폐건전지 전용수거함으로 갑니다.','유해폐기물',false,false,10345,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('usan','우산','{}','조건부','살대는 고철, 천은 일반쓰레기입니다. 분해해야 재활용됩니다.','복합재질',false,true,9450,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('kaerieo','캐리어','{"여행가방"}','대형폐기물','크기와 상관없이 대부분 대형폐기물 신고 대상입니다.','생활용품',false,true,8730,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('hwabun','화분','{}','조건부','재질에 따라 갈립니다. 흙은 화분과 따로 버려야 합니다.','도자기류',false,false,8635,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('geureut','그릇','{"식기"}','일반쓰레기','도자기·유리 식기는 재활용이 안 됩니다. 불연성 마대로 갑니다.','도자기류',false,true,7780,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('sinbal','신발','{"운동화"}','조건부','상태가 좋으면 의류수거함, 낡았으면 일반쓰레기입니다.','섬유류',false,false,6595,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('chimdae','침대','{}','대형폐기물','프레임과 매트리스를 따로 신고해야 하는 지자체가 많습니다.','가구류',false,false,6515,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('begae','베개','{}','일반쓰레기','의류수거함에 넣으면 안 됩니다. 종량제 봉투로 갑니다.','섬유류',false,true,6290,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('naembi','냄비','{}','재활용','스테인리스·양은은 고철입니다. 뚜껑 유리는 분리하세요.','금속류',false,true,5910,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('maeteuriseu','매트리스','{}','대형폐기물','스프링이 있으면 처리비가 올라갑니다. 지자체별 금액 차가 큽니다.','가구류',false,false,5420,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('uija','의자','{}','대형폐기물','개수만큼 수수료가 붙습니다. 금속 프레임은 고철로 뺄 수 있습니다.','가구류',false,false,4270,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('subakkkeopjil','수박껍질','{}','음식물','음식물쓰레기가 맞습니다. 잘게 잘라 물기를 빼세요.','음식물',false,true,3850,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('geonjeonji','건전지','{"건전지"}','전용수거함','일반쓰레기에 넣으면 안 됩니다. 전용수거함이 따로 있습니다.','유해폐기물',false,true,3760,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('sugeon','수건','{}','조건부','깨끗하면 의류수거함, 오염됐으면 일반쓰레기입니다.','섬유류',false,false,3700,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('sikyongyu','식용유','{"폐식용유"}','전용수거함','하수구에 버리면 안 됩니다. 폐식용유 수거함으로 갑니다.','유해폐기물',false,false,3430,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('anmauija','안마의자','{}','무상수거','폐가전 무상수거 대상이지만 집밖으로 내놓아야 가져갑니다.','폐전기·전자제품',false,false,3330,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('syopa','쇼파','{"소파"}','대형폐기물','인승 수만큼 수수료가 매겨집니다. 소파와 같은 품목입니다.','가구류',false,false,3300,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('doma','도마','{}','일반쓰레기','재질과 상관없이 대부분 종량제 봉투로 갑니다.','생활용품',false,false,3120,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('somibul','솜이불','{}','대형폐기물','솜 충전재라 의류수거함에 못 넣습니다. 부피가 큽니다.','섬유류',false,true,2980,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('noteubuk','노트북','{}','조건부','중소형이라 1대만으로는 무상수거가 안 됩니다. 5개 이상부터입니다.','폐전기·전자제품',false,false,2970,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('bananakkeopjil','바나나껍질','{}','음식물','음식물쓰레기가 맞습니다. 스티커는 떼세요.','음식물',false,true,2710,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();
