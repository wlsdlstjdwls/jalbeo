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
