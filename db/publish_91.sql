-- 4차 확장 10개 발행 (81 -> 91). 92개 실측 수요 풀 완전 소진.
-- 다이소(daiso)는 매장명이라 마지막까지 제외했다 (docs/11 판단 그대로).

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('peurinteo','프린터','{}','조건부','소형가전이라 1대만으로는 무상수거가 안 됩니다. 5개 이상부터입니다.','폐전기·전자제품',false,false,50,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('binil','비닐','{}','조건부','깨끗한 포장 비닐만 재활용됩니다. 식탁보·장판 같은 복합재질은 종량제입니다.','플라스틱류',false,true,45,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('munjjak','문짝','{}','대형폐기물','타일과 달리 대부분 지자체 품목표에 정식으로 올라 있는 대형폐기물입니다.','가구류',false,false,35,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('gwailkkeopjil','과일껍질','{}','조건부','수박·바나나는 음식물, 파인애플·코코넛처럼 딱딱한 껍질은 일반쓰레기입니다.','음식물',false,false,35,true,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('reoningmeosin','러닝머신','{}','조건부','무상수거 가능 지역이 따로 있습니다. 안 되면 대형폐기물로 신고합니다.','폐전기·전자제품',false,true,25,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('seonban','선반','{}','조건부','벽걸이 소형은 종량제, 바닥에 세우는 대형 수납 선반은 대형폐기물입니다.','가구류',false,false,25,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('aekja','액자','{}','조건부','종량제봉투에 들어가는 소형은 일반쓰레기, 큰 액자는 대형폐기물입니다.','복합재질',false,false,25,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('nakyeop','낙엽','{}','일반쓰레기','사료·퇴비 대상이 아니라 음식물쓰레기가 아닙니다. 소량은 종량제봉투로 갑니다.','생활용품',false,false,10,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('boilreo','보일러','{}','조건부','가스·급수 배관이 있어 전문업체 철거가 먼저입니다. 직접 떼면 위험합니다.','폐전기·전자제품',false,false,10,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('galbippyeo','갈비뼈','{}','일반쓰레기','닭뼈와 같은 이유로 사료화가 안 돼 음식물쓰레기가 아닙니다.','음식물',false,false,10,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, housing_split=excluded.housing_split, region_varies=excluded.region_varies, monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has, published=true, updated_at=now();
