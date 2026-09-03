-- 잘버려 초기화 — Supabase SQL Editor에 통째로 붙여넣고 실행
-- 생성: scripts/build_db_sql.py (재실행 안전 — upsert)

-- 잘버려 초기 스키마
-- 원칙: DB는 저작(authoring) 저장소다. 사용자 요청 경로에는 들어가지 않는다.
--       빌드할 때 1회 읽어 정적 JSON으로 내보내고, 페이지는 그 JSON만 본다.

create extension if not exists "uuid-ossp";

-- ── 품목 마스터 ────────────────────────────────────────────────
-- 본문(마크다운)은 git에 둔다. 여기엔 판정·메타데이터만.
create table if not exists items (
  slug            text primary key,                 -- URL. 예: 'seonpunggi'
  name            text not null,                    -- 표시명. 예: '선풍기'
  aliases         text[] not null default '{}',     -- 표기 변종. 예: {'쇼파','소파'}
  -- 집필 전 품목도 대기열로 담아둔다. 발행(published) 시점에만 판정이 필수다.
  verdict         text
                  check (verdict in ('재활용','일반쓰레기','대형폐기물','전용수거함','조건부')),
  verdict_line    text,                             -- 판정 한 줄 요약
  category        text,                             -- 재활용일 때 분류
  housing_split   boolean not null default false,   -- 아파트/단독 분기 필요 (docs/07 수식어 1위)
  region_varies   boolean not null default false,   -- 지자체마다 답이 갈림
  monthly_volume  integer,                          -- 게이트 1 실측 (docs/09)
  competitor_has  boolean not null default false,   -- 블리스고 보유 여부 (docs/10)
  published       boolean not null default false,   -- 본문 집필 완료 후 true
  updated_at      timestamptz not null default now(),
  constraint items_published_needs_verdict
    check (not published or (verdict is not null and verdict_line is not null))
);
create index if not exists items_volume_idx on items (monthly_volume desc nulls last);

-- ── 지자체 ────────────────────────────────────────────────────
create table if not exists regions (
  code      text primary key,          -- 행정표준코드
  sido      text not null,             -- 서울특별시
  sigungu   text,                      -- 용산구 (광역시도 자체면 null)
  name      text not null              -- 표시명
);
create index if not exists regions_sido_idx on regions (sido);

-- ── 품목 × 지역 판정 ───────────────────────────────────────────
-- 핵심 표. 음식물 판정처럼 지자체마다 답이 갈리는 경우를 담는다.
-- 국가 기준이 없어 조례·문의로 하나씩 채워야 한다 (docs/08).
create table if not exists item_region_rules (
  id           uuid primary key default uuid_generate_v4(),
  item_slug    text not null references items(slug) on delete cascade,
  region_code  text not null references regions(code) on delete cascade,
  verdict      text not null,
  note         text,
  source_url   text not null,
  as_of        date not null,           -- 기준일자. CLAUDE.md 작업 규칙
  updated_at   timestamptz not null default now(),
  unique (item_slug, region_code)
);
create index if not exists irr_item_idx on item_region_rules (item_slug);

-- ── 대형폐기물 수수료 ──────────────────────────────────────────
-- 공공데이터포털 78건 임포트 대상 (docs/03). 지자체마다 컬럼명이 달라 정규화 필요.
create table if not exists bulky_fees (
  id           uuid primary key default uuid_generate_v4(),
  region_code  text not null references regions(code) on delete cascade,
  item_name    text not null,           -- 원본 품목명 (정규화 전)
  item_slug    text references items(slug) on delete set null,
  spec         text,                    -- 규격
  fee          integer not null,        -- 원
  source_url   text not null,
  as_of        date not null,
  unique (region_code, item_name, spec)
);
create index if not exists bulky_region_idx on bulky_fees (region_code);
create index if not exists bulky_slug_idx on bulky_fees (item_slug);

-- ── 환경부 근거 판정 ───────────────────────────────────────────
-- 훈령 별표1에서 뽑은 해당/비해당 품목 (docs/08). 전국 공통.
create table if not exists guideline_verdicts (
  id          uuid primary key default uuid_generate_v4(),
  item_name   text not null,
  verdict     text not null check (verdict in ('O','X')),
  category    text,
  subitem     text,
  basis       text,                     -- '해당품목' | '비해당품목'
  source_url  text not null,
  as_of       date not null,
  unique (item_name, category, subitem, verdict)
);

-- ── 읽기 전용 공개 ─────────────────────────────────────────────
-- 빌드 때 anon 키로 select만 한다. 쓰기는 대시보드/서비스 키로만.
alter table items               enable row level security;
alter table regions             enable row level security;
alter table item_region_rules   enable row level security;
alter table bulky_fees          enable row level security;
alter table guideline_verdicts  enable row level security;

do $$
declare t text;
begin
  foreach t in array array['items','regions','item_region_rules','bulky_fees','guideline_verdicts']
  loop
    execute format('drop policy if exists %I on %I', t || '_read', t);
    execute format(
      'create policy %I on %I for select to anon, authenticated using (true)',
      t || '_read', t);
  end loop;
end $$;


-- 품목 92개 (게이트 1 실측 검색량 있는 것만, 집필 전이라 published=false)
insert into items (slug, name, monthly_volume, region_varies, competitor_has, housing_split, published) values
  ('ibul', '이불', 26905, false, true, false, false),
  ('seonpunggi', '선풍기', 12120, true, false, false, false),
  ('huraipaen', '후라이팬', 12100, true, true, false, false),
  ('yuri', '유리', 11395, false, true, false, false),
  ('baeteori', '배터리', 10345, false, true, false, false),
  ('usan', '우산', 9450, true, false, false, false),
  ('kaerieo', '캐리어', 8730, true, true, false, false),
  ('hwabun', '화분', 8635, false, true, false, false),
  ('geureut', '그릇', 7780, true, true, false, false),
  ('inhyeong', '인형', 7110, false, false, false, false),
  ('sinbal', '신발', 6595, false, true, false, false),
  ('chimdae', '침대', 6515, false, true, false, false),
  ('begae', '베개', 6290, true, true, false, false),
  ('naembi', '냄비', 5910, true, true, false, false),
  ('maeteuriseu', '매트리스', 5420, false, true, false, false),
  ('uija', '의자', 4270, false, true, false, false),
  ('subakkkeopjil', '수박껍질', 3850, true, true, false, false),
  ('sohwagi', '소화기', 3795, false, false, false, false),
  ('geonjeonji', '건전지', 3760, true, false, false, false),
  ('sugeon', '수건', 3700, false, true, false, false),
  ('sikyongyu', '식용유', 3430, false, true, false, false),
  ('anmauija', '안마의자', 3330, false, true, false, false),
  ('syopa', '쇼파', 3300, false, true, false, false),
  ('doma', '도마', 3120, false, true, false, false),
  ('somibul', '솜이불', 2980, true, true, false, false),
  ('noteubuk', '노트북', 2970, false, true, false, false),
  ('bananakkeopjil', '바나나껍질', 2710, true, true, false, false),
  ('cheongsogi', '청소기', 2600, false, false, false, false),
  ('gabang', '가방', 2460, false, true, false, false),
  ('ppalraegeonjodae', '빨래건조대', 2400, false, false, false, false),
  ('keompyuteo', '컴퓨터', 2375, false, true, false, false),
  ('gireum', '기름', 2230, false, true, false, false),
  ('seutiropom', '스티로폼', 2120, false, true, false, false),
  ('sopa', '소파', 1985, false, true, false, false),
  ('jangnangam', '장난감', 1965, false, true, false, false),
  ('naengjanggo', '냉장고', 1910, false, true, false, false),
  ('heonot', '헌옷', 1765, false, true, false, false),
  ('geoul', '거울', 1690, false, true, false, false),
  ('jeonjareinji', '전자레인지', 1550, false, false, false, false),
  ('reogeu', '러그', 1490, false, false, false, false),
  ('chaeksang', '책상', 1455, false, true, false, false),
  ('bapsot', '밥솥', 1320, false, false, false, false),
  ('hwajangpum', '화장품', 1310, false, true, false, false),
  ('hyangsu', '향수', 1280, false, true, false, false),
  ('jajeongeo', '자전거', 1230, false, false, false, false),
  ('piano', '피아노', 1160, false, false, false, false),
  ('gimchi', '김치', 1040, false, true, false, false),
  ('kasiteu', '카시트', 990, false, false, false, false),
  ('chikinppyeo', '치킨뼈', 960, false, true, false, false),
  ('jangpan', '장판', 930, false, true, false, false),
  ('moniteo', '모니터', 750, false, false, false, false),
  ('onsumaeteu', '온수매트', 630, false, true, false, false),
  ('otjang', '옷장', 460, false, true, false, false),
  ('jangnong', '장농', 455, false, false, false, false),
  ('siktak', '식탁', 440, false, false, false, false),
  ('gaseureinji', '가스레인지', 430, false, false, false, false),
  ('otgeoli', '옷걸이', 390, false, true, false, false),
  ('jeongijangpan', '전기장판', 380, true, true, false, false),
  ('setakgi', '세탁기', 340, false, true, false, false),
  ('hyudaepon', '휴대폰', 300, false, true, false, false),
  ('jeonjapiano', '전자피아노', 255, false, false, false, false),
  ('byeongi', '변기', 240, false, true, false, false),
  ('haenggeo', '행거', 230, false, false, false, false),
  ('chaekjang', '책장', 220, false, true, false, false),
  ('golpeuchae', '골프채', 210, false, false, false, false),
  ('gaseurenji', '가스렌지', 205, false, false, false, false),
  ('gimchinaengjanggo', '김치냉장고', 170, false, true, false, false),
  ('hyeonggwangdeung', '형광등', 160, false, true, false, false),
  ('heukchimdae', '흙침대', 145, false, true, false, false),
  ('gyerankkeopjil', '계란껍질', 130, false, false, false, false),
  ('hwajangdae', '화장대', 120, false, false, false, false),
  ('seorapjang', '서랍장', 110, false, false, false, false),
  ('geumgo', '금고', 105, false, false, false, false),
  ('golpeugabang', '골프가방', 100, false, true, false, false),
  ('jongikeop', '종이컵', 100, true, true, false, false),
  ('jongi', '종이', 95, false, true, false, false),
  ('tail', '타일', 95, false, false, false, false),
  ('peteubyeong', '페트병', 70, false, true, false, false),
  ('yangpakkeopjil', '양파껍질', 65, false, true, false, false),
  ('eohang', '어항', 60, false, false, false, false),
  ('uyupaek', '우유팩', 55, false, true, false, false),
  ('peurinteo', '프린터', 50, false, true, false, false),
  ('binil', '비닐', 45, true, true, false, false),
  ('munjjak', '문짝', 35, false, false, false, false),
  ('gwailkkeopjil', '과일껍질', 35, false, true, false, false),
  ('reoningmeosin', '러닝머신', 25, false, false, false, false),
  ('seonban', '선반', 25, false, false, false, false),
  ('aekja', '액자', 25, false, false, false, false),
  ('nakyeop', '낙엽', 10, false, false, false, false),
  ('daiso', '다이소', 10, false, false, false, false),
  ('boilreo', '보일러', 10, false, false, false, false),
  ('galbippyeo', '갈비뼈', 10, false, false, false, false)
on conflict (slug) do update set
  name = excluded.name,
  monthly_volume = excluded.monthly_volume,
  region_varies = excluded.region_varies,
  competitor_has = excluded.competitor_has,
  updated_at = now();

-- 환경부 훈령 별표1 판정 73건 (docs/08)
insert into guideline_verdicts (item_name, verdict, category, subitem, basis, source_url, as_of) values
  ('택배용보냉상자류등내부에알루미늄박', 'X', '골판지류', '골판지상자등', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('우유팩', 'O', '골판지류', '종이팩 (살균팩, 멸균팩)', '해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('두유팩', 'O', '골판지류', '종이팩 (살균팩, 멸균팩)', '해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('소주팩', 'O', '골판지류', '종이팩 (살균팩, 멸균팩)', '해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('쥬스팩', 'O', '골판지류', '종이팩 (살균팩, 멸균팩)', '해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('양면이코팅된종이컵', 'X', '골판지 외 종이류', '종이컵', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('알루미늄등금속이박힌복합소재종이', 'X', '골판지 외 종이류', '기타종이류', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('택배전표', 'X', '골판지 외 종이류', '기타종이류', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('영수증감열지', 'X', '골판지 외 종이류', '기타종이류', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('사진용지', 'X', '골판지 외 종이류', '기타종이류', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('종이호일', 'X', '골판지 외 종이류', '기타종이류', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('색지', 'X', '골판지 외 종이류', '기타종이류', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('방수가공포스터', 'X', '골판지 외 종이류', '기타종이류', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('깨진유리제품', 'X', '유리병', '음료수병, 기타병류', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('코팅및다양한색상이들어간유리제품', 'X', '유리병', '음료수병, 기타병류', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('내열유리제품', 'X', '유리병', '음료수병, 기타병류', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('크리스탈유리제품', 'X', '유리병', '음료수병, 기타병류', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('판유리', 'X', '유리병', '음료수병, 기타병류', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('조명기구용유리류', 'X', '유리병', '음료수병, 기타병류', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('음료수캔', 'O', '유리병', '음료·주류캔, 식료품캔', '해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('맥주캔', 'O', '유리병', '음료·주류캔, 식료품캔', '해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('통조림캔', 'O', '유리병', '음료·주류캔, 식료품캔', '해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('음료용기', 'O', '합성수지용기· 트레이류', '무색투명한먹는샘물, 음료 폴리에틸렌테레 프탈레이트(PET)병을 제외한PET 용기(병을 포함한다)ㆍ트레이류 · PVC, PE, PP, PS, PSP 재질등의용기· 트레이류', '해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('식품용기', 'O', '합성수지용기· 트레이류', '무색투명한먹는샘물, 음료 폴리에틸렌테레 프탈레이트(PET)병을 제외한PET 용기(병을 포함한다)ㆍ트레이류 · PVC, PE, PP, PS, PSP 재질등의용기· 트레이류', '해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('세정용기', 'O', '합성수지용기· 트레이류', '무색투명한먹는샘물, 음료 폴리에틸렌테레 프탈레이트(PET)병을 제외한PET 용기(병을 포함한다)ㆍ트레이류 · PVC, PE, PP, PS, PSP 재질등의용기· 트레이류', '해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('옷걸이', 'X', '합성수지용기· 트레이류', '무색투명한먹는샘물, 음료 폴리에틸렌테레 프탈레이트(PET)병을 제외한PET 용기(병을 포함한다)ㆍ트레이류 · PVC, PE, PP, PS, PSP 재질등의용기· 트레이류', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('칫솔', 'X', '합성수지용기· 트레이류', '무색투명한먹는샘물, 음료 폴리에틸렌테레 프탈레이트(PET)병을 제외한PET 용기(병을 포함한다)ㆍ트레이류 · PVC, PE, PP, PS, PSP 재질등의용기· 트레이류', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('파일철', 'X', '합성수지용기· 트레이류', '무색투명한먹는샘물, 음료 폴리에틸렌테레 프탈레이트(PET)병을 제외한PET 용기(병을 포함한다)ㆍ트레이류 · PVC, PE, PP, PS, PSP 재질등의용기· 트레이류', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('낚싯대', 'X', '합성수지용기· 트레이류', '무색투명한먹는샘물, 음료 폴리에틸렌테레 프탈레이트(PET)병을 제외한PET 용기(병을 포함한다)ㆍ트레이류 · PVC, PE, PP, PS, PSP 재질등의용기· 트레이류', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('유모차·보행기', 'X', '합성수지용기· 트레이류', '무색투명한먹는샘물, 음료 폴리에틸렌테레 프탈레이트(PET)병을 제외한PET 용기(병을 포함한다)ㆍ트레이류 · PVC, PE, PP, PS, PSP 재질등의용기· 트레이류', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('CD·DVD', 'X', '합성수지용기· 트레이류', '무색투명한먹는샘물, 음료 폴리에틸렌테레 프탈레이트(PET)병을 제외한PET 용기(병을 포함한다)ㆍ트레이류 · PVC, PE, PP, PS, PSP 재질등의용기· 트레이류', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('여행용트렁크', 'X', '합성수지용기· 트레이류', '무색투명한먹는샘물, 음료 폴리에틸렌테레 프탈레이트(PET)병을 제외한PET 용기(병을 포함한다)ㆍ트레이류 · PVC, PE, PP, PS, PSP 재질등의용기· 트레이류', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('파티완구', 'X', '합성수지용기· 트레이류', '완구류(전지나전기를 사용하여충전·작동하는 전기ㆍ전자완구제외)', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('봉제인형', 'X', '합성수지용기· 트레이류', '완구류(전지나전기를 사용하여충전·작동하는 전기ㆍ전자완구제외)', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('1회용봉투등각종비닐류', 'O', '합성수지 비닐류', '비닐포장재, 1회용비 닐봉투', '해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('식탁보', 'X', '합성수지 비닐류', '비닐포장재, 1회용비 닐봉투', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('고무장갑', 'X', '합성수지 비닐류', '비닐포장재, 1회용비 닐봉투', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('장판', 'X', '합성수지 비닐류', '비닐포장재, 1회용비 닐봉투', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('돗자리', 'X', '합성수지 비닐류', '비닐포장재, 1회용비 닐봉투', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('섬유류등은종량제봉투', 'X', '합성수지 비닐류', '비닐포장재, 1회용비 닐봉투', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('농ㆍ수ㆍ축산물포장용발포스티렌상자', 'O', '발포합성수지·', '스티로폼완충재', '해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('타재질과코팅또는접착된발포스티렌', 'X', '발포합성수지·', '스티로폼완충재', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('건축용내·외장재스티로폼', 'X', '발포합성수지·', '스티로폼완충재', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('이불', 'X', '의류', '의류, 잡화', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('베개', 'X', '의류', '의류, 잡화', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('방석', 'X', '의류', '의류, 잡화', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('인형', 'X', '의류', '의류, 잡화', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('골프가방', 'X', '의류', '의류, 잡화', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('매트류', 'X', '의류', '의류, 잡화', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('가죽부츠', 'X', '의류', '의류, 잡화', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('롱부츠', 'X', '의류', '의류, 잡화', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('바퀴달린가방', 'X', '의류', '의류, 잡화', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('인라인스케이트', 'X', '의류', '의류, 잡화', '비해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('TV', 'O', '전기·전자제품·', '대형전기·전자제품', '해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('냉장고', 'O', '전기·전자제품·', '대형전기·전자제품', '해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('세탁기', 'O', '전기·전자제품·', '대형전기·전자제품', '해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('건조기', 'O', '전기·전자제품·', '대형전기·전자제품', '해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('에어컨', 'O', '전기·전자제품·', '대형전기·전자제품', '해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('태양광패널', 'O', '전기·전자제품·', '대형전기·전자제품', '해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('전기오븐', 'O', '전기·전자제품·', '대형전기·전자제품', '해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('자동판매기', 'O', '전기·전자제품·', '대형전기·전자제품', '해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('가습기', 'O', '전기·전자제품·', '소형 전기·전자제품 (전지내장형 제품, 전기·전자완구, 기타 소형가전등)', '해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('비디오플레이어', 'O', '전기·전자제품·', '소형 전기·전자제품 (전지내장형 제품, 전기·전자완구, 기타 소형가전등)', '해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('스캐너', 'O', '전기·전자제품·', '소형 전기·전자제품 (전지내장형 제품, 전기·전자완구, 기타 소형가전등)', '해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('전기밥솥', 'O', '전기·전자제품·', '소형 전기·전자제품 (전지내장형 제품, 전기·전자완구, 기타 소형가전등)', '해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('청소기', 'O', '전기·전자제품·', '소형 전기·전자제품 (전지내장형 제품, 전기·전자완구, 기타 소형가전등)', '해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('전기주전자', 'O', '전기·전자제품·', '소형 전기·전자제품 (전지내장형 제품, 전기·전자완구, 기타 소형가전등)', '해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('토스트기', 'O', '전기·전자제품·', '소형 전기·전자제품 (전지내장형 제품, 전기·전자완구, 기타 소형가전등)', '해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('제빵기', 'O', '전기·전자제품·', '소형 전기·전자제품 (전지내장형 제품, 전기·전자완구, 기타 소형가전등)', '해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('헤어드라이어', 'O', '전기·전자제품·', '소형 전기·전자제품 (전지내장형 제품, 전기·전자완구, 기타 소형가전등)', '해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('전자담배', 'O', '전기·전자제품·', '소형 전기·전자제품 (전지내장형 제품, 전기·전자완구, 기타 소형가전등)', '해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('블루투스이어폰', 'O', '전기·전자제품·', '소형 전기·전자제품 (전지내장형 제품, 전기·전자완구, 기타 소형가전등)', '해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date),
  ('전기손난로', 'O', '전기·전자제품·', '소형 전기·전자제품 (전지내장형 제품, 전기·전자완구, 기타 소형가전등)', '해당품목', 'https://www.law.go.kr/DRF/lawService.do?OC=test&target=admrul&ID=2100000272746&type=JSON', '2026-01-01'::date)
on conflict do nothing;
