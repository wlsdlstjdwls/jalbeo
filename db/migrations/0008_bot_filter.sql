-- 봇을 방문자 집계에서 뺀다. 그리고 이미 오염된 구간을 통계에서 끊는다.
--
-- 0004는 "스크립트 도배에는 열려 있지만 통계 왜곡 말고는 피해가 없다"고 적고
-- 넘어갔다. 그 왜곡이 실제로 왔다. 도메인을 붙이고 색인을 요청한 다음 날
-- (2026-09-07) 조회 65건에 방문자 37명이 찍혔는데, 그중 35명이 조회 1건짜리에
-- 리퍼러가 전부 없었다. 사람이 아니라 크롤러다.
--
-- **왜 방문자 수까지 부푸나.** 방문자 구분은 localStorage의 UUID인데,
-- 검색엔진 렌더러는 페이지를 그릴 때마다 저장소가 비어 있다. 그래서 한 봇이
-- 100페이지를 돌면 방문자 100명이 된다. 조회수보다 방문자 수가 더 크게 틀린다.
--
-- 방어는 두 겹이다. 클라이언트(Base.astro)가 UA와 체류로 거르고, 여기서
-- 한 번 더 UA를 본다. 0004의 '/admin%' 처리와 같은 이중 방어다.
-- 서버 쪽이 필요한 이유는 클라이언트 코드가 낡은 캐시로 돌 수 있어서다.

-- 통계 집계 시작점. 이 앞의 데이터는 필터가 없던 때라 사람과 봇이 섞여 있다.
-- 지우지 않고 통계에서만 끊는다 - 원본은 남겨야 나중에 봇 비율을 되짚는다.
create or replace function public.stats_since()
returns timestamptz
language sql
immutable
as $$
  select '2026-09-08 00:00:00+09'::timestamptz;
$$;

grant execute on function public.stats_since() to anon, authenticated;

-- UA로 봇을 판정한다. 헤더가 없으면(서버 호출 등) 봇으로 안 본다.
create or replace function public.is_bot_ua()
returns boolean
language plpgsql
stable
security definer
set search_path = public
as $$
declare
  ua text;
begin
  begin
    ua := lower(coalesce(current_setting('request.headers', true)::json ->> 'user-agent', ''));
  exception when others then
    return false;
  end;
  if ua = '' then
    return false;
  end if;
  return ua ~ '(bot|crawl|spider|slurp|headless|preview|monitor|lighthouse|curl|wget|python-requests|axios|node-fetch|facebookexternalhit|embedly|yeti|daum)';
end;
$$;

-- 페이지뷰 기록에 봇 판정을 붙인다. 나머지는 0004와 같다.
create or replace function public.track_page_view(
  p_visitor_id uuid,
  p_path text,
  p_referrer_host text default null
)
returns void
language plpgsql
security definer
set search_path = public
as $$
begin
  if p_path is null or char_length(p_path) = 0 then
    return;
  end if;
  if p_path like '/admin%' then
    return;
  end if;
  if is_bot_ua() then
    return;
  end if;
  insert into page_views (visitor_id, path, referrer_host)
  values (p_visitor_id, left(p_path, 200), left(nullif(p_referrer_host, ''), 100));
end;
$$;

-- 검색어 로그도 같이 막는다. 봇은 검색창에 타이핑을 안 하지만, 로그를
-- 쏘는 쪽은 우리 스크립트라서 렌더러가 자동완성을 건드리면 들어올 수 있다.
create or replace function public.track_search_query(
  p_term text,
  p_hit_count int,
  p_visitor_id uuid default null
)
returns void
language plpgsql
security definer
set search_path = public
as $$
begin
  if p_term is null or char_length(trim(p_term)) < 2 then
    return;
  end if;
  if is_bot_ua() then
    return;
  end if;
  insert into search_queries (term, hit_count, visitor_id)
  values (left(trim(p_term), 60), greatest(coalesce(p_hit_count, 0), 0), p_visitor_id);
end;
$$;

-- 읽는 쪽 넷은 stats_since() 아래를 통째로 안 본다.
--
-- stats_since를 반환값에 넣는다. 화면이 "누적 0"을 보여줄 때 그게 트래픽이
-- 없어서인지 집계를 끊어서인지 구분해야 하는데, 날짜를 클라이언트에 또
-- 적으면 둘이 어긋난다. 반환 열이 하나 느니 create or replace가 안 되고
-- drop이 필요하다.
drop function if exists public.admin_visitor_stats();
create function public.admin_visitor_stats()
returns table (
  concurrent_visitors bigint,
  today_visitors bigint,
  total_visitors bigint,
  today_views bigint,
  total_views bigint,
  first_view_at timestamptz,
  since_at timestamptz
)
language plpgsql
security definer
set search_path = public
as $$
declare
  kst_midnight timestamptz;
  floor_at timestamptz := stats_since();
begin
  if not is_admin() then
    raise exception 'not authorized';
  end if;

  kst_midnight := greatest(
    date_trunc('day', now() at time zone 'Asia/Seoul') at time zone 'Asia/Seoul',
    floor_at);

  return query select
    (select count(distinct pv.visitor_id) from page_views pv
      where pv.created_at > now() - interval '5 minutes' and pv.created_at >= floor_at),
    (select count(distinct pv.visitor_id) from page_views pv
      where pv.created_at >= kst_midnight),
    (select count(distinct pv.visitor_id) from page_views pv
      where pv.created_at >= floor_at),
    (select count(*) from page_views pv where pv.created_at >= kst_midnight),
    (select count(*) from page_views pv where pv.created_at >= floor_at),
    (select min(pv.created_at) from page_views pv where pv.created_at >= floor_at),
    floor_at;
end;
$$;

grant execute on function public.admin_visitor_stats() to authenticated;

create or replace function public.admin_visitor_daily(p_days int default 14)
returns table (day date, visitors bigint, views bigint)
language plpgsql
security definer
set search_path = public
as $$
declare
  floor_at timestamptz := stats_since();
begin
  if not is_admin() then
    raise exception 'not authorized';
  end if;

  return query
  with span as (
    select generate_series(
      greatest(
        (now() at time zone 'Asia/Seoul')::date - (greatest(least(p_days, 90), 1) - 1),
        (floor_at at time zone 'Asia/Seoul')::date),
      (now() at time zone 'Asia/Seoul')::date,
      interval '1 day'
    )::date as day
  ),
  agg as (
    select (pv.created_at at time zone 'Asia/Seoul')::date as day,
           count(distinct pv.visitor_id) as visitors,
           count(*) as views
    from page_views pv
    where pv.created_at >= floor_at
    group by 1
  )
  select s.day, coalesce(a.visitors, 0), coalesce(a.views, 0)
  from span s left join agg a on a.day = s.day
  order by s.day;
end;
$$;

create or replace function public.admin_visitor_breakdown(p_since_days int default 7)
returns table (kind text, label text, visitors bigint, views bigint)
language plpgsql
security definer
set search_path = public
as $$
declare
  since timestamptz;
begin
  if not is_admin() then
    raise exception 'not authorized';
  end if;

  since := case when p_since_days is null
                then '-infinity'::timestamptz
                else now() - make_interval(days => greatest(least(p_since_days, 365), 1)) end;
  since := greatest(since, stats_since());

  return query
  (select 'path'::text, pv.path,
          count(distinct pv.visitor_id), count(*)
     from page_views pv where pv.created_at >= since
     group by pv.path order by count(*) desc limit 20)
  union all
  (select 'referrer'::text, coalesce(pv.referrer_host, '(직접 유입)'),
          count(distinct pv.visitor_id), count(*)
     from page_views pv where pv.created_at >= since
     group by 2 order by count(*) desc limit 20);
end;
$$;

create or replace function public.admin_visitor_breakdown_page(
  p_kind text,
  p_since_days int default 7,
  p_limit int default 30,
  p_offset int default 0
)
returns table (label text, visitors bigint, views bigint, total_rows bigint)
language plpgsql
security definer
set search_path = public
as $$
declare
  since timestamptz;
begin
  if not is_admin() then
    raise exception 'not authorized';
  end if;

  if p_kind is null or p_kind not in ('path', 'referrer') then
    raise exception 'unknown kind: %', p_kind;
  end if;

  since := case when p_since_days is null
                then '-infinity'::timestamptz
                else now() - make_interval(days => greatest(least(p_since_days, 365), 1)) end;
  since := greatest(since, stats_since());

  return query
  with base as (
    select case when p_kind = 'path'
                then pv.path
                else coalesce(pv.referrer_host, '(직접 유입)') end as label,
           pv.visitor_id
      from page_views pv
     where pv.created_at >= since
  ),
  agg as (
    select b.label, count(distinct b.visitor_id) as visitors, count(*) as views
      from base b
     group by b.label
  )
  select a.label, a.visitors, a.views, count(*) over () as total_rows
    from agg a
   order by a.views desc, a.label
   limit greatest(least(p_limit, 100), 1)
  offset greatest(coalesce(p_offset, 0), 0);
end;
$$;
