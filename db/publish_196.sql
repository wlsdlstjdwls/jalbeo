-- 15차 확장 (188 -> 197). 근거는 docs/36, 실측 11차 하위 구간 나머지 36주제.
-- 자르는 기준은 검색량이 아니라 답이 기존 페이지와 갈리는지다(판단 8번, 40번).
-- 36 중 9 발행, 3 별칭(한복, 페트병 뚜껑, 책꽂이), 24 보류.
-- 파라솔은 우산 별칭으로 넣었다가 뺐다. 등재 수는 15 대 14로 같은데 값이 2,000~5,500
-- 대 750~1,000이라 우산 중앙값이 1,000에서 2,000으로 뛰었다. 판단 39번의 둘째 기준.
-- 보류 24는 대부분 가구, 대형가전이라 답이 스티커 하나다(판단 37번).
--
-- 식기건조기 페이지는 식기세척기를 별칭으로 받는다. 둘 다 훈령 대형가전 예시에
-- 이름이 있고 답(무상방문수거)이 같다. 다만 수수료 축은 다르다(건조기 0~2,000,
-- 세척기 4,000~14,000). build_fee_stats의 EXTRA_ALIAS에서 식기세척기를 None으로
-- 막아 건조기 통계만 화면에 낸다(판단 39번). 전화기의 팩스도 같은 이유로 막는다.

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('jeonhwagi','전화기','{"유선전화기","무선전화기","집전화","팩스","팩시밀리","인터폰"}','전용수거함',
   '소형가전 수거함입니다. 무선전화기는 배터리를 뺍니다.',
   '폐전기전자제품',false,true,120,true,true),

  ('hwanpunggi','환풍기','{"렌지후드","레인지후드","배기후드","후드","욕실환풍기","배기팬"}','조건부',
   '떼어 낸 환풍기는 소형가전입니다. 후드는 크기에 따라 대형폐기물입니다.',
   '폐전기전자제품',false,true,110,true,true),

  ('taieo','타이어','{"폐타이어","자동차타이어","자전거타이어","휠","알루미늄휠"}','조건부',
   '타이어 가게가 받습니다. 못 돌려주면 대형폐기물입니다.',
   '고무류',false,true,105,true,true),

  ('hatpaek','핫팩','{"손난로","일회용핫팩","전기손난로","충전식손난로","발열팩"}','조건부',
   '일회용은 종량제봉투, 충전식은 소형가전입니다. 뜯지 마세요.',
   '복합재질',false,false,70,true,true),

  ('sikgigeonjogi','식기건조기','{"식기세척기","식기살균기","살균건조기","식기살균건조기","식기세척건조기"}','무상수거',
   '훈령이 대형가전으로 이름을 적어 둔 품목입니다. 무상방문수거입니다.',
   '폐전기전자제품',false,true,70,true,true),

  ('jeukseokbapyonggi','즉석밥 용기','{"햇반용기","햇반그릇","즉석밥그릇","컵밥용기","오뚜기밥용기"}','재활용',
   '플라스틱 수거함입니다. 다만 선별장에서 걸러지는 일이 많습니다.',
   '플라스틱류',false,false,55,true,true),

  ('heeodeuraieo','헤어드라이어','{"드라이기","헤어드라이기","고데기","매직기","에어랩"}','전용수거함',
   '훈령이 소형가전으로 이름을 적어 둔 품목입니다. 종량제봉투가 아닙니다.',
   '폐전기전자제품',false,false,55,true,true),

  ('parasol','파라솔','{"야외파라솔","캠핑파라솔","비치파라솔","그늘막파라솔","파라솔받침대"}','조건부',
   '살대는 고철, 천은 종량제봉투입니다. 통째로면 대형폐기물입니다.',
   '복합재질',false,true,75,true,true),

  ('hwilcheeo','휠체어','{"전동휠체어","수동휠체어","보행기","보행보조기","전동스쿠터"}','조건부',
   '쓸 수 있으면 보조기기센터가 받습니다. 못 쓰면 대형폐기물입니다.',
   '생활용품',false,true,55,true,true)
on conflict (slug) do update set
  name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict,
  verdict_line=excluded.verdict_line, category=excluded.category,
  housing_split=excluded.housing_split, region_varies=excluded.region_varies,
  monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has,
  published=true, updated_at=now();

-- 별칭 넷. 답이 본체와 같고 수수료 등재 수가 같은 자릿수다(판단 39번).
-- 한복(115) -> 헌옷: 훈령 의류 항목이 긋는 선(재사용 여부)이 같다. 본문에 한복 절
update items set aliases = array['헌 옷', '한복'], updated_at = now()
where slug = 'heonot';
-- 페트병 뚜껑(80) -> 페트병: 훈령이 "뚜껑을 닫아 배출"이라 답한다. 본문에 뚜껑 절
update items set aliases = array['페트병 뚜껑', '페트병 고리'], updated_at = now()
where slug = 'peteubyeong';
-- 우산은 원래대로 되돌린다(파라솔 별칭 철회).
update items set aliases = array['장우산', '고장난 우산', '양산'], updated_at = now()
where slug = 'usan';
-- 책꽂이(50) -> 책장: 같은 물건이다. 등재 34곳 대 38곳
update items set aliases = array['책꽂이'], updated_at = now()
where slug = 'chaekjang';
