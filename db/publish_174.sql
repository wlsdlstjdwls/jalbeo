-- 12차 확장 (168 -> 174). 근거는 docs/33, 실측 11차.
-- 원천은 자동완성 고리 밖이다 -- 지자체 수수료표와 blisgo 품목 목록.
-- 여섯 주제 전부 재활용 축이고, 전부 기존 페이지가 한 글자도 안 답하고 있었다.
--
-- 식칼(1,415)만 성격이 다르다. 답은 커터칼 페이지에 이미 있었는데 그 페이지
-- 이름이 커터칼(195)이라 7.3배 큰 검색을 못 받고 있었다. 판단 12번대로
-- 답이 갈리는 부분(칼집, 다량 고철상, 세라믹)을 갈라 페이지를 냈고,
-- 커터칼 페이지는 커터칼 날 쪽만 남겼다.

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('butangaseu','부탄가스','{"가스용기","휴대용 부탄가스","이소부탄","가스통","스프레이 캔"}','조건부',
   '노즐을 눌러 비운 뒤 캔류입니다. 구멍은 뚫지 않습니다.',
   '금속류',false,false,5165,true,true),

  ('bide','비데','{"비데 시트","전자비데","렌탈비데"}','조건부',
   '철거가 먼저입니다. 한 대뿐이면 무상수거가 안 됩니다.',
   '폐전기전자제품',false,true,3080,true,true),

  ('myeolgyunpaek','멸균팩','{"아셉틱 카톤팩","두유팩","소주팩","벽돌팩"}','재활용',
   '종이류가 아니라 종이팩입니다. 섞으면 그 종이 더미가 같이 버려집니다.',
   '종이류',true,true,2825,true,true),

  ('chejunggye','체중계','{"저울","체지방계","전자저울","주방저울"}','조건부',
   '전자식이면 건전지를 빼고 소형가전, 기계식이면 고철입니다.',
   '폐전기전자제품',false,false,2460,true,true),

  ('seupgijegeoje','습기제거제','{"제습제","물먹는하마","방습제","실리카겔"}','조건부',
   '고인 물은 변기, 알갱이와 흡습지는 종량제봉투, 통은 플라스틱입니다.',
   '생활용품',false,false,1895,true,true),

  ('sikkal','식칼','{"주방칼","부엌칼","과도","중식도","칼"}','일반쓰레기',
   '스테인리스인데도 고철로 안 냅니다. 날을 감싸는 게 먼저입니다.',
   '금속류',false,true,1415,true,true)
on conflict (slug) do update set
  name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict,
  verdict_line=excluded.verdict_line, category=excluded.category,
  housing_split=excluded.housing_split, region_varies=excluded.region_varies,
  monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has,
  published=true, updated_at=now();

-- 커터칼: 주방칼을 별칭에서 뺀다. 이제 식칼 페이지가 받는다.
-- '가위'도 뺀다 -- 가위는 별도 페이지인데 별칭으로도 걸려 있었다.
update items set
  aliases = array['문구칼', '커터', '커터날', '칼날'],
  updated_at = now()
where slug = 'keoteokal';

-- 가위: 별칭 '칼'을 뺀다. 식칼 페이지가 생겼으므로 칼 검색이 가위로 가면 오답이다.
update items set
  aliases = array['부엌가위', '문구용 가위', '전정가위', '가위날'],
  updated_at = now()
where slug = 'gawi';

-- 우유팩: 별칭 '멸균우유팩'을 뺀다. 멸균팩이 별도 페이지가 됐다.
-- '종이팩'은 남긴다 -- 일반팩 쪽이 우유팩 페이지의 본체다.
update items set
  aliases = array['두유팩', '종이팩', '주스팩', '살균팩'],
  updated_at = now()
where slug = 'uyupaek';
