-- 19차 확장 (230 -> 235). 근거는 실측 13차, 14차의 100~199 구간 12주제 판정.
-- 5 발행, 7 별칭. 합계 1,780이고 최대가 자석 190이라 이 구간은 검색량이 아니라
-- 답의 성질로만 갈랐다(docs/40).
--
-- 발행 다섯은 전부 기존 페이지의 첫 문단이 그 질문에 답하지 않는 것들이다(판단 40).
-- 자석은 고철 페이지가 "자석에 안 붙는 것도 고철"이라고만 하고 자석 자체를 안 다뤘다.
-- 배달용기는 즉석밥 용기, 컵라면이 있지만 검은색과 국물 자국이라는 질문이 다르다.
-- 바이올린은 피아노 페이지가 무게 절차만 말한다. 폭죽은 물에 적시라는 절차가 어느
-- 페이지에도 없다. 반찬통은 그릇 페이지가 "재활용 안 됨"으로 시작하는데 플라스틱
-- 반찬통은 재활용이라 답이 반대다.
--
-- 별칭 일곱은 본체 첫 문단이 그대로 답이거나(게껍데기 -> 조개껍질 표에 이미 있음,
-- 토스트기 -> 에어프라이어 본문이 같은 계열로 적음) 본체에 절을 붙여 답을 채웠다
-- (카세트테이프 -> CD, 분유통 -> 참치캔, 기름병 -> 유리병, 쇼핑백 -> 종이,
-- 나무쟁반 -> 도마). 본체 검색량은 전부 별칭의 1.5배 이상이다(판단 14).

-- 1) 신규 5개
insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('jaseok','자석','{"냉장고 자석","냉장고자석","마그넷","네오디뮴 자석","자석 교구","고무자석","강력자석","자석 블록"}','일반쓰레기',
   '쇠에 붙지만 고철이 아닙니다. 종량제봉투에 넣습니다. 강력 자석은 종이로 감싸세요.',
   '복합재질',false,false,190,true,true),

  ('baedalyonggi','배달용기','{"배달 용기","배달 플라스틱","배달음식 용기","일회용 용기","검은색 플라스틱","배달 그릇","플라스틱 용기","배달 도시락"}','조건부',
   '음식 찌꺼기만 씻어 내면 플라스틱류입니다. 국물 자국과 검은색은 상관없습니다.',
   '플라스틱류',false,false,175,true,true),

  ('baiollin','바이올린','{"비올라","첼로","통기타","우쿨렐레","현악기","악기","기타 악기","바이올린 케이스"}','조건부',
   '종량제봉투에 들어가면 종량제봉투, 기타와 첼로처럼 크면 대형폐기물입니다.',
   '복합재질',false,true,155,false,true),

  ('pokjuk','폭죽','{"불꽃놀이","스파클라","파티 폭죽","꽃불","안 쓴 폭죽","폭죽 처리"}','일반쓰레기',
   '물에 담가 적신 뒤 종량제봉투입니다. 유해폐기물이 아닙니다.',
   '복합재질',false,false,145,false,true),

  ('banchantong','반찬통','{"김치통","밀폐용기","락앤락","글라스락","유리 반찬통","플라스틱 반찬통","스텐 반찬통","반찬 용기"}','조건부',
   '플라스틱은 플라스틱류, 스테인리스는 고철, 패킹은 종량제봉투. 유리 반찬통은 종량제봉투입니다.',
   '플라스틱류',false,false,140,true,true)
on conflict (slug) do update set
  name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict,
  verdict_line=excluded.verdict_line, category=excluded.category,
  housing_split=excluded.housing_split, region_varies=excluded.region_varies,
  monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has,
  published=true, updated_at=now();

-- 2) 별칭 7건
-- 카세트테이프(165) -> CD(2,270). 훈령에 이름은 없지만 복합재질이라 답이 같다. CD 본문에 절 추가.
update items set aliases = array['dvd','시디','블루레이','카세트테이프','카세트 테이프','비디오테이프','비디오 테이프','카세트','VHS','캠코더 테이프'], updated_at = now() where slug = 'cd';
-- 분유통(150) -> 참치캔(225). 품목사전이 분유통을 금속캔 유사품목으로 둔다. 참치캔 본문에 절 추가. 수수료 등재 0.
update items set aliases = array['통조림','캔','분유통','분유캔','분유 통'], updated_at = now() where slug = 'chamchikaen';
-- 토스트기(140) -> 에어프라이어(1,240). 훈령 소형가전 예시에 토스트기가 이름으로 있고 본문이 이미 같은 계열로 적는다. 수수료 2곳뿐이라 통계 불변.
update items set aliases = array['에어프라이기','튀김기','토스트기','토스터','토스터기','토스트 기계'], updated_at = now() where slug = 'eeopeuraieo';
-- 기름병(120) -> 유리병(930). 본문에 이미 기름병 절이 있었고 품목사전 베이킹소다 문장을 보탰다.
update items set aliases = array['소주병','맥주병','잼병','기름병','참기름병','들기름병','올리브유병'], updated_at = now() where slug = 'yuribyeong';
-- 쇼핑백(110) -> 종이(300). 종이 쇼핑백이 기본 뜻이고 코팅, 비닐, 부직포는 표로 갈라 절 추가.
update items set aliases = array['신문','책','잡지','노트','스프링노트','상장','교과서','명함','쇼핑백','종이 쇼핑백','종이가방','종이봉투'], updated_at = now() where slug = 'jongi';
-- 나무쟁반(110) -> 도마(665). 품목사전이 나무 쟁반을 원목도마와 같은 배출방법으로 묶는다. 도마 본문에 절 추가. 나무그릇은 그릇 별칭에 이미 있어 안 넣었다.
update items set aliases = array['실리콘도마','플라스틱 도마','나무도마','나무쟁반','나무 쟁반','원목쟁반','원목 트레이'], updated_at = now() where slug = 'doma';
-- 게껍데기(100) -> 조개껍질(1,595). 본문 표에 "게, 새우, 랍스터 껍데기 | 종량제봉투"가 이미 있다. 품목사전 '게 껍데기'도 일반폐기물.
update items set aliases = array['굴껍질','소라껍질','홍합껍데기','게껍데기','게 껍데기','꽃게 껍데기','새우껍질','갑각류 껍데기','랍스터 껍데기'], updated_at = now() where slug = 'jogaekkeopjil';
