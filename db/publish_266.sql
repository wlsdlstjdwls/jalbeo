-- 26차 확장 (263 -> 266). 근거는 실측 20차 (`docs/51`).
--
-- 65주제 130키워드 중 127개를 측정했고 합계 6,280이다. 19차(지식iN 1회차)
-- 8,375의 0.75배다. Q&A가 두 회차에 0.15배로 마른 것과 다르다 - 판단 64의
-- '깊이 탐침'이 맞았다.
--
-- **1위가 발행이 아니었다.** 정수기필터 1,140은 이미 공기청정기 필터(1,230)
-- 페이지의 별칭이고 그 페이지 본문이 품목사전 연수필터까지 인용해 답하고
-- 있었다. 20차 주제 65개 중 9개가 어휘에 이미 있었다 (판단 72).
--
-- 3 발행, 25개 페이지에 별칭, 나머지는 보류.

-- 1) 신규 3개
insert into items (slug,name,aliases,verdict,verdict_line,category,housing_split,region_varies,monthly_volume,competitor_has,published) values
  -- 1,080. 이 회차에서 제일 큰 신규다. 품목사전에 '수세미'(일반폐기물)는
  -- 있는데 스펀지는 표제어가 없다 - 판단 34대로 기준으로 답한다. 수세미
  -- 설명이 "아크릴, 부직포, 스펀지 등 복합재질 제품으로 재활용이 어려워"라
  -- 스펀지 자체를 이유로 적고 있다. 포장 완충재(PU 폼, EPE)를 스티로폼
  -- 수거함에 넣는 것이 제일 흔한 실수다 - 과일망 페이지의 EPE 갈림과 같다.
  -- 철수세미만 금속이라 고철로 갈린다.
  ('seupeonji','스펀지','{"수세미","주방 수세미","멜라민 스펀지","매직블럭","세차 스펀지","목욕 스펀지","포장 완충재","완충재","스폰지","스펀지 퍼프"}','일반쓰레기',
   '수세미도 포장 완충재도 종량제봉투입니다. 철수세미만 고철입니다.',
   '생활용품',false,false,1080,false,true),

  -- 395. 한 이름이 두 물건이라 검색이 몰리는 자리다 (판단 38, 63).
  -- 고무컵이 달린 압축기와 배수구에 붓는 액체 세정제가 같은 말로 불린다.
  -- 락스 페이지 첫 문단은 액체를, 고무 페이지 첫 문단은 고무를 답하는데
  -- 어느 쪽도 '뚫어뻥'이라는 말을 안 쓴다. 스프링식 관통기는 금속이라
  -- 세 번째 갈래가 된다.
  ('ttureoppeong','뚫어뻥','{"뚫어펑","변기압축기","압축기","변기 뚫어뻥","배수구 세정제","관통기","스프링 뚫어뻥","펌프 뚫어뻥"}','조건부',
   '같은 이름이 두 물건입니다. 압축기와 액체 세정제가 답이 다릅니다.',
   '생활용품',false,false,395,false,true),

  -- 205. 폴리에스터라 의류수거함도 비닐류도 안 받는다. 그런데 종량제봉투로
  -- 끝나지 않는다 - 성남시는 50개 동 행정복지센터에 폐현수막 수거함을 두고
  -- 연간 3,000~6,000장을 환경 정비용 마대로 만든다. 지자체가 따로 회수하는
  -- 축이라 답이 지역으로 갈린다.
  ('hyeonsumak','현수막','{"폐현수막","배너","현수막 천","행사 현수막","선거 현수막"}','조건부',
   '종량제봉투인데, 동 주민센터가 따로 수거하는 곳이 있습니다.',
   '생활용품',false,true,205,false,true);

-- 2) 별칭 25개 페이지
update items set aliases = array['작은 화분','도자기 화분','화분 흙','깨진 화분','플라스틱 화분','흙','분갈이 흙','정원 흙','화단 흙'], updated_at = now() where slug = 'hwabun';  -- 화분
update items set aliases = array['가스렌지','인덕션','하이라이트','전기레인지'], updated_at = now() where slug = 'gaseureinji';  -- 가스레인지
update items set aliases = array['책꽂이','독서대'], updated_at = now() where slug = 'chaekjang';  -- 책장
update items set aliases = array['폐통장','예금통장','은행 통장','적금통장','통장 정리','우편물','고지서','등기우편'], updated_at = now() where slug = 'tongjang';  -- 통장
update items set aliases = array['공기계','폴더폰','핸드폰','폰케이스','휴대폰 케이스','핸드폰 케이스','그립톡','강화필름'], updated_at = now() where slug = 'hyudaepon';  -- 휴대폰
update items set aliases = array['고춧가루','고추가루','설탕','부침가루','튀김가루','미숫가루','카레가루','후추','분유가루','밀가루 반죽','반죽','녹차가루','호떡','만두','냉동만두','빵','식빵','곰팡이 핀 빵'], updated_at = now() where slug = 'milgaru';  -- 밀가루
update items set aliases = array['도배지','실크벽지','시트지','접착 시트지'], updated_at = now() where slug = 'byeokji';  -- 벽지
update items set aliases = array['먹던 과자','안 먹은 과자','유통기한 지난 과자','눅눅한 과자','초콜릿','초콜렛','사탕','젤리','시리얼','스낵','유통기한 지난 음식','유통기한 지난 음식물','상한 음식','탄 음식','유통기한 지난 라면','칼국수면','팝콘'], updated_at = now() where slug = 'gwaja';  -- 과자
update items set aliases = array['생 크림','휘핑크림','상한 우유','남은 우유','요구르트','유제품','크림치즈','상한 두유','케이크','남은 케이크','아이스크림','녹은 아이스크림'], updated_at = now() where slug = 'saengkeurim';  -- 생크림
update items set aliases = array['세탁세제','주방세제','가루세제','액체세제','섬유유연제','세탁조 세정제','캡슐세제','세정제','빨래세제','비누','고체 비누'], updated_at = now() where slug = 'seje';  -- 세제
update items set aliases = array['배드민턴채','라켓','테니스채'], updated_at = now() where slug = 'golpeuchae';  -- 골프채
update items set aliases = array['펜','샤프','샤프펜슬','형광펜','사인펜','볼펜심','보드마카','화이트보드마카','유성매직','연필깎이'], updated_at = now() where slug = 'bolpen';  -- 볼펜
update items set aliases = array['고철류','쇠','철','스테인리스','스텐','알루미늄','비철금속','금속','쇠붙이','휴대용 가스버너','가스버너','부루스타','버너','삼각대','카메라 삼각대','문고리','클립','헤어핀'], updated_at = now() where slug = 'gocheol';  -- 고철
update items set aliases = array['헌 옷','한복','가죽옷','가죽자켓','가죽재킷','원단','자투리 천','털실','뜨개실'], updated_at = now() where slug = 'heonot';  -- 헌옷
update items set aliases = array['바닥타일','데코타일','벽돌','시멘트 벽돌','블록','콘크리트 조각','석고보드','석고 보드','석고상','벼루'], updated_at = now() where slug = 'tail';  -- 타일
update items set aliases = array['닭뼈','돼지뼈','돼지 뼈','감자탕뼈','등뼈','족발뼈','갈비뼈','소뼈','사골뼈','닭발뼈','뼈다귀','치킨','남은 치킨','닭고기','닭껍질','고기','남은 고기'], updated_at = now() where slug = 'chikinppyeo';  -- 치킨뼈
update items set aliases = array['옥수수심','옥수수 껍질','죽순','버섯','버섯 밑동'], updated_at = now() where slug = 'oksusudae';  -- 옥수수대
update items set aliases = array['배달 용기','배달 플라스틱','배달음식 용기','일회용 용기','검은색 플라스틱','배달 그릇','플라스틱 용기','배달 도시락','플라스틱컵','플라스틱 컵','일회용 플라스틱컵','투명컵','테이크아웃컵','도시락','남은 도시락'], updated_at = now() where slug = 'baedalyonggi';  -- 배달용기
update items set aliases = array['진공청소기','유선청소기','무선청소기','로봇청소기','머리카락','배수구 머리카락','빠진 머리','잘린 머리카락','먼지봉투','청소기 먼지봉투','강아지털','동물 털'], updated_at = now() where slug = 'cheongsogi';  -- 청소기
update items set aliases = array['포장끈','박스끈','비닐끈','플라스틱 노끈','PP밴딩끈','밴딩끈','노끈 뭉치','빵끈','칼라타이','케이블타이','머리끈','낚시줄'], updated_at = now() where slug = 'nokkeun';  -- 노끈
update items set aliases = array['앵글선반','수납선반','철제선반','조립식 앵글','앵글'], updated_at = now() where slug = 'seonban';  -- 선반
update items set aliases = array['화장품 공병','남은 화장품','선크림','썬크림','화장품 용기','클렌징오일','클렌징 오일','바디오일','마사지오일','페이스오일','립밤','클렌징폼','속눈썹','인조속눈썹'], updated_at = now() where slug = 'hwajangpum';  -- 화장품
update items set aliases = array['인슐린주사기','주사바늘','펜니들','자가주사','위고비주사기','란셋','임신테스트기','임테기','자가진단키트','자가검사키트'], updated_at = now() where slug = 'jusagi';  -- 주사기
update items set aliases = array['복숭아 씨','과일씨','망고씨','아보카도씨','살구씨','자두씨','감씨','체리씨','대추씨','씨앗','아보카도','아보카도 씨','아보카도 과육','수박씨','단호박씨','해바라기씨','포도씨','호박씨','견과류','견과류 껍데기'], updated_at = now() where slug = 'boksungassi';  -- 복숭아씨
update items set aliases = array['신문','잡지','노트','스프링노트','상장','교과서','명함','쇼핑백','종이 쇼핑백','종이가방','종이봉투','스티커','이형지','마스킹테이프','마스킹 테이프','종이테이프','택배 송장','송장 스티커','아트지 스티커','포스트잇','테이프','접착테이프'], updated_at = now() where slug = 'jongi';  -- 종이
