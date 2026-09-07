-- 16차 확장 (197 -> 210). 근거는 docs/37, 실측 12차(분리의정석 품목사전 씨앗) 상위.
-- 72주제 중 200 이상 16주제를 조사해 13 발행, 3 별칭(냄비뚜껑, 뚝배기, 수영복).
-- 200 아래에서 별칭이 분명한 둘(지퍼백 -> 비닐, 침낭 -> 이불)도 같이 접었다.
-- 자르는 기준은 검색량이 아니라 답이 기존 페이지와 갈리는지다(판단 8번, 40번).
--
-- 라이터(5,740)가 이번 회차의 발견이다. 훈령에도 수수료표에도 없는데 12차 72주제
-- 합계 17,425의 3분의 1이다. 품목사전이 "가스를 완전히 제거한 후 종량제봉투"라고
-- 답하고 소방서는 "접수하기 곤란"이라 적는다. 답이 둘로 보이니 검색이 몰린다(판단 38).

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('raiteo','라이터','{"일회용라이터","가스라이터","지포라이터","토치라이터","라이터가스"}','일반쓰레기',
   '가스를 다 빼고 종량제봉투입니다. 소방서도 안 받습니다.',
   '복합재질',false,false,5740,true,true),

  ('waipeo','와이퍼','{"와이퍼블레이드","자동차와이퍼","와이퍼고무","와이퍼암"}','조건부',
   '고무는 봉투, 금속 프레임은 고철입니다. 안 갈리면 통째로 봉투입니다.',
   '복합재질',false,false,1240,true,true),

  ('jeonjadambae','전자담배','{"일회용전자담배","궐련형전자담배","액상전자담배","전담기기","전자담배액상","전자담배카트리지"}','전용수거함',
   '훈령 해당품목입니다. 전지째 소형가전 수거함이나 전지수거함입니다.',
   '폐전기전자제품',false,false,1215,true,true),

  ('aryeong','아령','{"덤벨","바벨","케틀벨","원판","바벨원판","역기"}','조건부',
   '고철입니다. 무거우면 대형폐기물로 kg당 값을 받는 곳이 있습니다.',
   '금속류',false,true,980,true,true),

  ('seullipeo','슬리퍼','{"실내화","욕실화","삼선슬리퍼","쪼리","샌들","크록스"}','일반쓰레기',
   '종량제봉투입니다. 의류수거함이 안 받는 신발입니다.',
   '생활용품',false,false,700,true,true),

  ('goyangimorae','고양이모래','{"고양이 모래","벤토나이트","두부모래","카사바모래","응고형모래","고양이화장실모래"}','조건부',
   '두부모래는 종량제봉투, 벤토나이트는 불연성 마대입니다. 변기는 안 됩니다.',
   '생활용품',false,true,695,true,true),

  ('mauseu','마우스','{"키보드","무선마우스","마우스패드","게이밍마우스","트랙볼"}','전용수거함',
   '소형가전 수거함입니다. 무선은 건전지를 뺍니다.',
   '폐전기전자제품',false,false,590,true,true),

  ('rakseu','락스','{"유한락스","표백제","염소계표백제","락스통","곰팡이제거제"}','조건부',
   '남은 락스는 물과 함께 하수구, 용기는 헹궈서 플라스틱입니다.',
   '플라스틱류',false,false,420,true,true),

  ('syawogi','샤워기','{"샤워헤드","샤워호스","필터샤워기","샤워기필터","수전"}','일반쓰레기',
   '복합재질이라 종량제봉투입니다. 호스는 감아서 묶습니다.',
   '복합재질',false,false,365,true,true),

  ('gumyeongjokki','구명조끼','{"라이프자켓","구명복","아동구명조끼","부력보조복","팽창식구명조끼"}','일반쓰레기',
   '종량제봉투입니다. 부력재를 빼면 봉투에 들어갑니다.',
   '복합재질',false,false,295,true,true),

  ('kaenbeoseu','캔버스','{"유화","캔버스액자","캔버스천","아크릴화","그림"}','조건부',
   '종량제봉투입니다. 크면 대형폐기물입니다.',
   '복합재질',false,false,245,true,true),

  ('jusagi','주사기','{"인슐린주사기","주사바늘","펜니들","자가주사","위고비주사기","란셋"}','일반쓰레기',
   '바늘을 감싸 종량제봉투입니다. 의료폐기물이 아닙니다.',
   '유해폐기물',false,true,225,true,true),

  ('chukgugong','축구공','{"공","농구공","배구공","야구공","테니스공","골프공"}','일반쓰레기',
   '바람을 빼고 종량제봉투입니다.',
   '복합재질',false,false,210,true,true)
on conflict (slug) do update set
  name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict,
  verdict_line=excluded.verdict_line, category=excluded.category,
  housing_split=excluded.housing_split, region_varies=excluded.region_varies,
  monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has,
  published=true, updated_at=now();

-- 별칭 다섯. 본체의 첫 문단이 이 질문에 답하고, 수수료 통계가 안 움직인다(판단 39, 42).
-- 냄비뚜껑(540) -> 냄비: 첫 문단이 "뚜껑과 손잡이가 다른 재질이라 그것만 떼면 된다"
update items set aliases = array['압력솥', '유리냄비', '양은냄비', '코팅냄비', '탄 냄비', '법랑냄비', '스텐냄비', '냄비뚜껑', '유리뚜껑'], updated_at = now() where slug = 'naembi';
-- 뚝배기(645) -> 그릇: 도자기라 불연성 마대. 그릇 본문에 뚝배기 절
update items set aliases = array['유리컵', '접시', '깨진 접시', '햇반 그릇', '나무그릇', '유리 접시', '사기그릇', '머그컵', '도기 그릇', '도자기 그릇', '깨진그릇', '식기', '유리그릇', '뚝배기', '내열냄비'], updated_at = now() where slug = 'geureut';
-- 수영복(230) -> 속옷: 품목사전 유사품목이 속옷, 스타킹. 수거 업체 불가 품목. 속옷 본문에 절
update items set aliases = array['팬티', '브래지어', '브라', '내복', '런닝셔츠', '양말', '스타킹', '수영복', '래시가드'], updated_at = now() where slug = 'sogot';
-- 지퍼백(135) -> 비닐: 품목사전 "비닐류 수거함". 비닐 첫 문단(깨끗한 포장재만)이 답한다
update items set aliases = array['양파망', '쿠팡 비닐', '택배봉투', '비닐봉투', '은박비닐', '지퍼백', '위생팩'], updated_at = now() where slug = 'binil';
-- 침낭(160) -> 이불: 품목사전 "의류 수거함에 배출 불가능". 이불 첫 문단과 같다
update items set aliases = array['여름이불', '패드', '극세사 이불', '겨울이불', '차렵이불', '침대커버', '이불커버', '침대시트', '침낭'], updated_at = now() where slug = 'ibul';
