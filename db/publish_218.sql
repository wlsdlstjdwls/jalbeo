-- 17차 확장 (210 -> 218). 근거는 실측 12차 100~199 구간 10주제 판정.
-- 8 발행(공유기, 전기모기채, 리모컨, 에어매트, 깁스, 주전자, 잉크카트리지, 우드락),
-- 2 별칭(장화 -> 신발, 샤워커튼 -> 커튼). 전부 수수료표 등재 0~2곳,
-- 재활용/일반 경계 물건이라 답이 갈리는 영역이다(판단 37).
--
-- 공유기, 전기모기채, 리모컨은 품목사전 배출방법이 마우스와 글자 그대로 같지만
-- (소형전기전자제품 전용수거함), 마우스가 이미 별도 발행된 전례를 따라 각각 발행했다.
-- 공유기는 통신사 임대장비 반납(위약금) 분기가 있어 마우스와 답이 다르다.
-- 주전자, 잉크카트리지는 재질/상태로 답이 완전히 갈려 options 필드를 썼다.
-- 장화, 샤워커튼은 각각 신발, 커튼의 첫 문단이 답하지 못하던 지점이라
-- 본문에 명시 문장을 추가하고 별칭으로만 등록했다(판단 40).

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('gongyugi','공유기','{"인터넷공유기","와이파이공유기","무선공유기","모뎀"}','조건부',
   '임대 장비면 반납해야 위약금이 안 붙습니다. 산 것이면 소형가전 수거함입니다.',
   '폐전기전자제품',false,false,175,true,true),

  ('jeongimogichae','전기모기채','{"모기채","전기파리채","충전식모기채"}','전용수거함',
   '소형가전 수거함입니다. 건전지식은 배터리를 먼저 뺍니다.',
   '폐전기전자제품',false,false,145,true,true),

  ('eeomaeteu','에어매트','{"에어풀장","비치매트리스","캠핑에어매트"}','조건부',
   '공기를 빼고 종량제봉투, 크기가 크면 대형폐기물입니다.',
   '복합재질',false,true,110,true,true),

  ('gibseu','깁스','{"석고깁스","캐스트","깁스붕대"}','조건부',
   '소량은 종량제봉투, 다량은 불연성 특수마대입니다.',
   '복합재질',false,true,110,true,true),

  ('rimokeon','리모컨','{"TV리모컨","에어컨리모컨","셋톱박스리모컨","만능리모컨"}','전용수거함',
   '소형가전 수거함입니다. 건전지부터 빼세요.',
   '폐전기전자제품',false,false,100,true,true),

  ('jujeonja','주전자','{"전기포트","커피포트","차주전자","법랑주전자","무쇠주전자"}','조건부',
   '전기주전자는 소형가전, 법랑이나 스테인리스 주전자는 고철입니다.',
   '복합재질',false,false,100,true,true),

  ('ingkeukateuriji','잉크카트리지','{"카트리지","토너","프린터카트리지","잉크통","레이저토너"}','조건부',
   '깨끗하면 플라스틱류나 제조사 회수, 남았으면 밀봉해 종량제봉투입니다.',
   '플라스틱류',false,false,100,true,true),

  ('udeurak','우드락','{"폼보드","우드락보드","전시보드"}','일반쓰레기',
   '흰색이어도 재활용이 안 됩니다. 종량제봉투입니다.',
   '복합재질',false,false,95,true,true)
on conflict (slug) do update set
  name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict,
  verdict_line=excluded.verdict_line, category=excluded.category,
  housing_split=excluded.housing_split, region_varies=excluded.region_varies,
  monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has,
  published=true, updated_at=now();

-- 별칭 둘. 본체의 첫 문단이 이 질문에 답하도록 본문을 먼저 고쳤다(판단 40).
-- 장화(120) -> 신발: 상태 무관 항상 종량제(재질 문제). 신발 표에 행 추가
update items set aliases = array['부츠', '슬리퍼', '구두', '크록스 신발', '헌신발', '운동화', '장화', '고무장화', '우비'], updated_at = now() where slug = 'sinbal';
-- 샤워커튼(100) -> 커튼: PVC/PEVA 방수재질이라 항상 종량제. 암막커튼과 같은 절에 추가
update items set aliases = array['암막커튼', '커튼봉', '샤워커튼'], updated_at = now() where slug = 'keoteun';
