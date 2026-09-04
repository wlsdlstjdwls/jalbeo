-- 5차 확장 (89 -> 149). 미측정 시드 220개를 신규 60 + 별칭 160으로 가름.
-- monthly_volume은 null이다. 0이 아니라 '모름'이다 (docs/09).
-- 생성: scripts/expand_items.py

-- 1) 중복 페이지 정리. 쇼파는 소파로, 장농은 장롱으로 흡수한다.
delete from items where slug in ('syopa','jangnong');

-- 2) 가운뎃점 정리 (CLAUDE.md 작업 규칙)
update items set category = replace(category, '·', '') where category like '%·%';

-- 3) 기존 품목 별칭 확장
update items set aliases = array(select distinct unnest(aliases || '{"쇼파","리클라이너","오토만"}'::text[])), updated_at=now() where slug='sopa';
update items set aliases = array(select distinct unnest(aliases || '{"장농","붙박이장"}'::text[])), updated_at=now() where slug='jangrong';
update items set aliases = array(select distinct unnest(aliases || '{"스텐냄비","양은냄비","법랑냄비","유리냄비","코팅냄비","탄 냄비","압력솥"}'::text[])), updated_at=now() where slug='naembi';
update items set aliases = array(select distinct unnest(aliases || '{"차렵이불","겨울이불","극세사 이불","여름이불","패드"}'::text[])), updated_at=now() where slug='ibul';
update items set aliases = array(select distinct unnest(aliases || '{"배게","솜베개","큰 베개","메모리폼 베개"}'::text[])), updated_at=now() where slug='begae';
update items set aliases = array(select distinct unnest(aliases || '{"식탁의자","책상의자","컴퓨터의자","좌식의자","캠핑의자","사무용의자"}'::text[])), updated_at=now() where slug='uija';
update items set aliases = array(select distinct unnest(aliases || '{"유리그릇","유리컵","머그컵","사기그릇","도자기 그릇","깨진그릇","깨진 접시","나무그릇","도기 그릇","햇반 그릇","접시","유리 접시"}'::text[])), updated_at=now() where slug='geureut';
update items set aliases = array(select distinct unnest(aliases || '{"도자기 화분","깨진 화분","작은 화분","화분 흙","플라스틱 화분"}'::text[])), updated_at=now() where slug='hwabun';
update items set aliases = array(select distinct unnest(aliases || '{"나무액자","아크릴액자","대형 액자","큰 액자","결혼액자"}'::text[])), updated_at=now() where slug='aekja';
update items set aliases = array(select distinct unnest(aliases || '{"봉제인형","솜인형","대형인형","큰 인형","애착인형"}'::text[])), updated_at=now() where slug='inhyeong';
update items set aliases = array(select distinct unnest(aliases || '{"나무장난감","플라스틱 장난감","아이 장난감","블록"}'::text[])), updated_at=now() where slug='jangnangam';
update items set aliases = array(select distinct unnest(aliases || '{"세탁소 옷걸이","플라스틱 옷걸이","나무 옷걸이","철사 옷걸이","철제 옷걸이"}'::text[])), updated_at=now() where slug='otgeoli';
update items set aliases = array(select distinct unnest(aliases || '{"침대 매트리스","접이식 매트리스","토퍼","토퍼 매트리스"}'::text[])), updated_at=now() where slug='maeteuriseu';
update items set aliases = array(select distinct unnest(aliases || '{"천가방","부직포가방","가죽가방","에코백","크로스백"}'::text[])), updated_at=now() where slug='gabang';
update items set aliases = array(select distinct unnest(aliases || '{"헌신발","크록스 신발","구두","슬리퍼","부츠"}'::text[])), updated_at=now() where slug='sinbal';
update items set aliases = array(select distinct unnest(aliases || '{"무선청소기","유선청소기","진공청소기","로봇청소기"}'::text[])), updated_at=now() where slug='cheongsogi';
update items set aliases = array(select distinct unnest(aliases || '{"전기밥솥","압력밥솥","쿠쿠"}'::text[])), updated_at=now() where slug='bapsot';
update items set aliases = array(select distinct unnest(aliases || '{"전신거울","깨진거울","손거울"}'::text[])), updated_at=now() where slug='geoul';
update items set aliases = array(select distinct unnest(aliases || '{"깨진유리","강화유리","식탁유리","판유리","깨진 유리컵","깨진 유리병"}'::text[])), updated_at=now() where slug='yuri';
update items set aliases = array(select distinct unnest(aliases || '{"스탠드 선풍기","서큘레이터"}'::text[])), updated_at=now() where slug='seonpunggi';
update items set aliases = array(select distinct unnest(aliases || '{"카펫","카페트","매트","발매트"}'::text[])), updated_at=now() where slug='reogeu';
update items set aliases = array(select distinct unnest(aliases || '{"시스템행거","왕자행거","옷걸이 행거"}'::text[])), updated_at=now() where slug='haenggeo';
update items set aliases = array(select distinct unnest(aliases || '{"철제선반","앵글선반","수납선반"}'::text[])), updated_at=now() where slug='seonban';
update items set aliases = array(select distinct unnest(aliases || '{"노트","스프링노트","잡지","신문","상장","명함","책","교과서"}'::text[])), updated_at=now() where slug='jongi';
update items set aliases = array(select distinct unnest(aliases || '{"멸균우유팩","종이팩","주스팩"}'::text[])), updated_at=now() where slug='uyupaek';
update items set aliases = array(select distinct unnest(aliases || '{"리튬배터리","노트북 배터리","휴대폰 배터리","핸드폰 배터리","충전지"}'::text[])), updated_at=now() where slug='baeteori';
update items set aliases = array(select distinct unnest(aliases || '{"남은 식용유","튀김 기름","돼지기름","오리기름","고기 기름"}'::text[])), updated_at=now() where slug='sikyongyu';
update items set aliases = array(select distinct unnest(aliases || '{"쿠팡 비닐","양파망","비닐봉투","택배봉투"}'::text[])), updated_at=now() where slug='binil';
update items set aliases = array(select distinct unnest(aliases || '{"과일 스티로폼","완충 스티로폼"}'::text[])), updated_at=now() where slug='seutiropom';
update items set aliases = array(select distinct unnest(aliases || '{"나무도마","실리콘도마","플라스틱 도마"}'::text[])), updated_at=now() where slug='doma';
update items set aliases = array(select distinct unnest(aliases || '{"쓰던수건","목욕타월","행주"}'::text[])), updated_at=now() where slug='sugeon';
update items set aliases = array(select distinct unnest(aliases || '{"여행용 캐리어","트렁크"}'::text[])), updated_at=now() where slug='kaerieo';
update items set aliases = array(select distinct unnest(aliases || '{"컴퓨터 모니터","lcd 모니터"}'::text[])), updated_at=now() where slug='moniteo';
update items set aliases = array(select distinct unnest(aliases || '{"달걀 껍질","달걀껍데기","메추리알 껍질"}'::text[])), updated_at=now() where slug='gyerankkeopjil';
update items set aliases = array(select distinct unnest(aliases || '{"과일 껍질","귤껍질","사과껍질"}'::text[])), updated_at=now() where slug='gwailkkeopjil';
update items set aliases = array(select distinct unnest(aliases || '{"바나나 껍질"}'::text[])), updated_at=now() where slug='bananakkeopjil';
update items set aliases = array(select distinct unnest(aliases || '{"대리석 식탁","교자상","밥상"}'::text[])), updated_at=now() where slug='siktak';
update items set aliases = array(select distinct unnest(aliases || '{"남은 화장품","화장품 공병","선크림"}'::text[])), updated_at=now() where slug='hwajangpum';
update items set aliases = array(select distinct unnest(aliases || '{"고장난 우산","양산","장우산"}'::text[])), updated_at=now() where slug='usan';
update items set aliases = array(select distinct unnest(aliases || '{"데코타일","바닥타일"}'::text[])), updated_at=now() where slug='tail';
update items set aliases = array(select distinct unnest(aliases || '{"장판 조각","바닥재"}'::text[])), updated_at=now() where slug='jangpan';
update items set aliases = array(select distinct unnest(aliases || '{"공기계","폴더폰"}'::text[])), updated_at=now() where slug='hyudaepon';
update items set aliases = array(select distinct unnest(aliases || '{"전기요","히터","전기히터"}'::text[])), updated_at=now() where slug='jeongijangpan';

-- 4) 신규 품목 59개

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('bojobaeteori','보조배터리','{"파워뱅크"}','전용수거함','종량제봉투와 재활용 어느 쪽도 아닙니다. 부풀었으면 더 급합니다.','유해폐기물',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('tibeu','TV','{"티비","텔레비전"}','무상수거','훈령이 지정한 대형 전기전자제품입니다. 무상방문수거 대상입니다.','폐전기전자제품',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('meoltitaep','멀티탭','{"콘센트","전기콘센트"}','전용수거함','고철도 플라스틱도 아닙니다. 소형 전기전자제품 수거함으로 갑니다.','폐전기전자제품',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('chungjeongi','충전기','{"충전케이블","무선충전기","어댑터"}','전용수거함','선만 따로 잘라 고철로 내지 마세요. 통째로 소형가전 수거함입니다.','폐전기전자제품',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('eeopeuraieo','에어프라이어','{"에어프라이기","튀김기"}','무상수거','중소형이라 단독 신청은 안 됩니다. 5개 이상 모으거나 전용수거함입니다.','폐전기전자제품',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('gaseupgi','가습기','{}','전용수거함','훈령이 소형 전기전자제품으로 이름을 박아 둔 품목입니다.','폐전기전자제품',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('geonjogi','건조기','{"의류건조기"}','무상수거','2026년 훈령에 대형 전기전자제품으로 명시됐습니다. 무상수거 대상입니다.','폐전기전자제품',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('jeseupgi','제습기','{}','무상수거','크기에 따라 단독 신청이 갈립니다. 소형은 5개 이상부터입니다.','폐전기전자제품',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('darimi','다리미','{"스팀다리미"}','전용수거함','소형가전입니다. 종량제봉투에 넣으면 안 됩니다.','폐전기전자제품',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('sonseonpunggi','손선풍기','{"미니선풍기","휴대용 선풍기"}','전용수거함','리튬배터리가 들어 있습니다. 선풍기와 경로가 완전히 다릅니다.','유해폐기물',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('myeondogi','면도기','{"전기면도기","일회용 면도기"}','조건부','전기식과 일회용은 경로가 다릅니다. 날은 따로 싸야 합니다.','폐전기전자제품',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('ledjeongu','LED 전구','{"led","led등","엘이디 전구"}','전용수거함','2026년 훈령부터 형광등 수거함 대상입니다. 일반쓰레기가 아닙니다.','유해폐기물',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('jaebongteul','재봉틀','{"미싱"}','조건부','가정용 소형과 공업용 받침대형은 신고 품목이 다릅니다.','폐전기전자제품',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('yuribyeong','유리병','{"소주병","맥주병","잼병"}','재활용','빈용기보증금 대상이면 돈을 돌려받습니다. 깨졌으면 얘기가 달라집니다.','유리류',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('semyeondae','세면대','{"세면기"}','대형폐기물','도기라 재활용 경로가 없습니다. 변기와 같은 취급입니다.','도자기류',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('hwabyeong','화병','{"꽃병"}','일반쓰레기','유리병으로 착각하기 쉽습니다. 두꺼운 장식 유리는 재활용이 안 됩니다.','유리류',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('suje','수저','{"숟가락","젓가락","포크"}','재활용','스테인리스는 고철입니다. 나무와 플라스틱은 종량제입니다.','금속류',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('chamchikaen','참치캔','{"통조림","캔"}','재활용','기름을 안 닦으면 재활용에서 빠집니다. 뚜껑 처리가 관건입니다.','금속류',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('hoil','호일','{"은박지","알루미늄 호일","쿠킹호일"}','일반쓰레기','알루미늄인데 캔이 아닙니다. 훈령이 종량제봉투로 지정합니다.','금속류',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('angyeong','안경','{"선글라스","안경테"}','일반쓰레기','렌즈와 테가 붙어 있어 분리가 안 됩니다. 기부 경로는 따로 있습니다.','복합재질',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('chitsol','칫솔','{"전동칫솔"}','일반쓰레기','훈령이 합성수지 재활용에서 명시적으로 뺀 품목입니다.','플라스틱류',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('chiyak','치약','{"치약 튜브"}','조건부','다 쓴 튜브는 헹굴 수 없는 용기라 규정이 따로 있습니다.','플라스틱류',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('ppaldae','빨대','{"플라스틱 빨대","종이빨대"}','일반쓰레기','너무 작아 선별기를 통과합니다. 종이빨대도 마찬가지입니다.','플라스틱류',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('maseukeu','마스크','{"kf94","덴탈마스크"}','일반쓰레기','부직포는 재활용이 안 됩니다. 끈과 코철사도 떼지 마세요.','섬유류',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('multisyu','물티슈','{"아기물티슈"}','일반쓰레기','휴지가 아닙니다. 변기에 내리면 막힙니다.','플라스틱류',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('hyujisim','휴지심','{"화장지심","키친타올심"}','재활용','종이류가 맞습니다. 다만 젖었으면 종량제로 갑니다.','종이류',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('keoteokal','커터칼','{"문구칼","주방칼","가위"}','일반쓰레기','그냥 넣으면 수거원이 다칩니다. 표시 의무가 있습니다.','금속류',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('belteu','벨트','{"허리띠"}','일반쓰레기','의류수거함 대상이 아닙니다. 버클 때문입니다.','복합재질',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('moja','모자','{"볼캡","야구모자"}','조건부','상태가 좋으면 의류수거함, 낡았으면 종량제입니다.','섬유류',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('boonbyeong','보온병','{"텀블러","스텐텀블러"}','조건부','진공 이중구조라 통째로는 고철이 안 됩니다.','금속류',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('renjeu','렌즈','{"콘택트렌즈","일회용 렌즈"}','일반쓰레기','변기나 세면대에 흘리면 미세플라스틱이 됩니다.','플라스틱류',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('yeongyangje','영양제','{"폐의약품","약","조제약"}','전용수거함','종량제봉투와 변기 둘 다 안 됩니다. 약국이나 주민센터로 갑니다.','유해폐기물',false,true,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('maenikyueo','매니큐어','{"네일","리무버"}','일반쓰레기','인화성이라 유해폐기물로 받는 지자체가 있습니다.','유해폐기물',false,true,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('yeomsaegyak','염색약','{"탈색약","염색약 통"}','조건부','내용물이 남았는지로 갈립니다. 튜브와 통은 따로입니다.','유해폐기물',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('gijeogwi','기저귀','{"성인기저귀","생리대"}','일반쓰레기','흡수체가 고분자라 재활용이 안 됩니다. 오물은 털어내세요.','위생용품',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('yumocha','유모차','{"보행기","웨건"}','대형폐기물','훈령이 합성수지 재활용에서 이름 박아 뺀 품목입니다.','복합재질',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('silnaejajeongeo','실내자전거','{"헬스자전거","스피닝"}','대형폐기물','전기를 쓰지 않는 기구라 무상수거가 안 됩니다.','생활용품',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('beompeochimdae','범퍼침대','{"범퍼매트","놀이방매트"}','대형폐기물','침대가 아니라 매트류입니다. 의류수거함에 절대 못 넣습니다.','발포수지류',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('keoteun','커튼','{"암막커튼","커튼봉"}','조건부','천은 의류수거함이 될 수도 있습니다. 봉과 레일은 고철입니다.','섬유류',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('byeokji','벽지','{"도배지","실크벽지"}','일반쓰레기','종이처럼 보여도 재활용이 안 됩니다. 양이 많으면 신고 대상입니다.','건축폐자재',false,true,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('bangchungmang','방충망','{"모기장","방충망 틀"}','조건부','망과 알루미늄 틀을 분리하면 절반이 고철로 빠집니다.','복합재질',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('ppokppogi','뽁뽁이','{"에어캡","완충재","단열 뽁뽁이"}','조건부','포장용과 창문 단열용은 재질이 달라 경로가 갈립니다.','플라스틱류',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('aiseupaek','아이스팩','{"젤 아이스팩","곡물 아이스팩","보냉팩"}','조건부','안에 든 것이 젤인지 물인지로 완전히 갈립니다.','복합재질',false,true,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('bonaenggabang','보냉가방','{"보냉백","아이스박스"}','일반쓰레기','은박과 부직포가 붙어 있어 분리가 안 됩니다.','복합재질',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('johwa','조화','{"인조화","조화 화분"}','일반쓰레기','플라스틱과 철사와 천이 붙어 있습니다. 화분과 따로 버리세요.','복합재질',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('sajin','사진','{"인화사진","사진액자"}','일반쓰레기','훈령이 사진용지를 종이류에서 뺐습니다. 종량제봉투입니다.','종이류',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('aelbeom','앨범','{"졸업앨범","결혼앨범","포토북"}','조건부','표지와 속지 재질이 달라 통째로는 재활용이 안 됩니다.','종이류',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('cd','CD','{"dvd","시디","블루레이"}','일반쓰레기','훈령이 합성수지 재활용에서 명시적으로 뺀 품목입니다.','플라스틱류',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('kotingjongi','코팅종이','{"코팅지","전단지","영수증"}','일반쓰레기','감열지와 코팅지는 종이류가 아닙니다. 훈령에 적혀 있습니다.','종이류',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('pasoejongi','파쇄종이','{"문서 파쇄","세절지"}','조건부','잘게 잘랐다고 종이류가 아닙니다. 담는 방법이 따로 있습니다.','종이류',false,true,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('jogaekkeopjil','조개껍질','{"굴껍질","소라껍질","홍합껍데기"}','일반쓰레기','음식물이 아닙니다. 사료로 못 만드는 딱딱한 껍데기입니다.','음식물',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('saengseonppyeo','생선뼈','{"생선가시","생선내장"}','일반쓰레기','뼈는 일반쓰레기, 내장은 음식물입니다. 같이 담지 마세요.','음식물',false,true,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('oksusudae','옥수수대','{"옥수수심","옥수수 껍질"}','일반쓰레기','알맹이는 음식물이지만 심과 껍질은 아닙니다.','음식물',false,true,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('keopijjikkeogi','커피찌꺼기','{"커피박","원두찌꺼기"}','조건부','음식물로 받는 곳과 안 받는 곳이 갈립니다. 별도 수거도 있습니다.','음식물',false,true,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('tibaek','티백','{"녹차티백","찻잎"}','조건부','찻잎은 음식물, 티백 주머니와 실은 아닙니다.','음식물',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('doenjang','된장 고추장','{"고추장","장류","남은 장"}','조건부','염분이 높아 사료로 못 씁니다. 음식물이 아닌 지자체가 많습니다.','음식물',false,true,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('keopramyeon','컵라면','{"컵라면 용기","라면국물"}','조건부','용기 재질과 국물 처리가 따로입니다. 씻어야 재활용됩니다.','발포수지류',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('namutgaji','나뭇가지','{"가지치기","전지목"}','조건부','소량은 종량제, 많으면 대형폐기물 신고 대상입니다.','생활용품',false,true,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('topbap','톱밥','{"게 톱밥","펫 톱밥"}','일반쓰레기','음식물처럼 보여도 아닙니다. 게를 싸 온 톱밥도 마찬가지입니다.','생활용품',false,false,null,false,true)
on conflict (slug) do update set name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict, verdict_line=excluded.verdict_line, category=excluded.category, region_varies=excluded.region_varies, published=true, updated_at=now();

