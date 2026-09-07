-- 14차 확장 (182 -> 188). 근거는 docs/35, 실측 11차 하위 구간(390 이하) 상위 여섯.
-- 자르는 기준은 검색량이 아니라 답이 기존 페이지와 갈리는지다(판단 8번, 40번).
-- 여섯 다 냈다. 넷(볼펜, 양초, 신용카드, 헬멧)은 답이 종량제봉투로 같아 보이지만
-- 첫 문단의 질문이 다르다 -- 볼펜은 "플라스틱인데 왜", 양초는 "유리 용기는",
-- 카드는 "개인정보", 헬멧은 "봉투에 안 들어가면". 같은 답이 아니라 같은 목적지다.
--
-- 이어폰은 사이트 안에 모순이 있었다. 전선 페이지가 '이어폰 줄'을 종량제봉투로
-- 적고 있었는데 훈령 해당품목에 블루투스이어폰이 있고 분리의정석은 이어폰을
-- 소형전기전자제품으로 둔다. 전선 페이지를 같이 고쳤다(판단 18번).
--
-- 하드디스크는 컴퓨터 페이지 둘째 절이 이미 파기 방법을 말하지만 첫 문단은
-- 무상수거 조건이다. 하드만 든 사람의 질문("이걸 어떻게 없애나")이 아니다.
-- 구청 파쇄 서비스는 사이트 어디에도 없었다.

insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  ('bolpen','볼펜','{"펜","샤프","샤프펜슬","형광펜","사인펜","볼펜심"}','일반쓰레기',
   '플라스틱처럼 보여도 종량제봉투입니다. 훈령이 문구류를 재활용에서 뺐습니다.',
   '복합재질',false,false,390,true,true),

  ('yangcho','양초','{"캔들","향초","양키캔들","티라이트","소이캔들"}','조건부',
   '초는 종량제봉투입니다. 유리 용기는 왁스를 다 긁어낸 뒤에만 유리입니다.',
   '생활용품',false,false,305,true,true),

  ('ieopon','이어폰','{"무선이어폰","블루투스이어폰","에어팟","버즈","헤드폰","헤드셋"}','전용수거함',
   '유선이든 무선이든 소형가전 수거함입니다. 전선이 아닙니다.',
   '폐전기전자제품',false,false,270,true,true),

  ('sinyongkadeu','신용카드','{"체크카드","카드","플라스틱카드","교통카드","멤버십카드","기프트카드"}','일반쓰레기',
   '해지하고 자른 뒤 종량제봉투입니다. 플라스틱 통에 넣지 마세요.',
   '복합재질',false,false,195,true,true),

  ('helmet','헬멧','{"안전모","자전거헬멧","오토바이헬멧","킥보드헬멧","바이크헬멧"}','조건부',
   '봉투에 들어가면 종량제봉투, 안 들어가면 대형폐기물입니다. 재활용은 없습니다.',
   '복합재질',false,true,185,true,true),

  ('hadeudiseukeu','하드디스크','{"외장하드","HDD","SSD","USB메모리","저장장치","하드"}','조건부',
   '데이터 파기가 먼저입니다. 구청 파쇄 서비스를 쓰면 배출까지 끝납니다.',
   '폐전기전자제품',false,true,175,true,true)
on conflict (slug) do update set
  name=excluded.name, aliases=excluded.aliases, verdict=excluded.verdict,
  verdict_line=excluded.verdict_line, category=excluded.category,
  housing_split=excluded.housing_split, region_varies=excluded.region_varies,
  monthly_volume=excluded.monthly_volume, competitor_has=excluded.competitor_has,
  published=true, updated_at=now();
