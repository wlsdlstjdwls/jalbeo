-- 사람 UA로 JS를 돌리는 예약 크롤러를 집계에서 뺀다 (docs/64).
--
-- 0008은 UA와 2초 체류로 걸렀다. 그런데 9/22부터 사흘 간격으로 정오(KST)마다
-- 32~36건이 2분 안에 몰려 들어온다 (9/22, 9/25, 9/28, 10/1, 10/4, 10/7, 10/10).
-- UA에 봇 표식이 없고 2초도 머문다. 남는 표식은 셋이다 - 저장소가 비어 건마다
-- 새 UUID(그래서 그 UUID의 조회는 평생 1건), 리퍼러 없음, 짧은 시간에 몰림.
-- 사람이 북마크로 들어오면 앞의 둘은 같지만 이 트래픽에서 10분 안에 다섯이
-- 겹치지는 않는다.
--
-- 들어올 때는 못 거른다 - 몰림은 뒤에 와야 보인다. 그래서 0008의 stats_since()
-- 처럼 행은 두고 읽는 쪽에서 끊는다 (판단 32). 검색 유입 지표(inflow_report)는
-- 리퍼러가 있는 행만 세므로 이 필터와 무관하다.
--
-- 기준(10분, 5명)은 9/8~10/12 기록으로 골랐다. 5분 8명은 9/19, 9/27의 느린
-- 크롤(시간당 30건 안팎)을 놓친다.

create view public.page_views_human
with (security_invoker = true) as
with single as (
  select visitor_id from page_views group by visitor_id having count(*) = 1
),
lone as (
  select pv.id,
         count(*) over (order by pv.created_at
                        range between interval '10 minutes' preceding
                                  and interval '10 minutes' following) as crowd
    from page_views pv
    join single s using (visitor_id)
   where pv.referrer_host is null
)
select pv.*
  from page_views pv
 where pv.id not in (select l.id from lone l where l.crowd >= 5);

-- 원본 표와 같이 바깥에는 안 연다. 읽는 것은 아래 security definer 함수뿐이다.
revoke all on public.page_views_human from anon, authenticated;

-- 0008의 읽는 쪽 넷을 그대로 두고 표만 바꾼다.
create or replace function public.admin_visitor_stats()
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
    (select count(distinct pv.visitor_id) from page_views_human pv
      where pv.created_at > now() - interval '5 minutes' and pv.created_at >= floor_at),
    (select count(distinct pv.visitor_id) from page_views_human pv
      where pv.created_at >= kst_midnight),
    (select count(distinct pv.visitor_id) from page_views_human pv
      where pv.created_at >= floor_at),
    (select count(*) from page_views_human pv where pv.created_at >= kst_midnight),
    (select count(*) from page_views_human pv where pv.created_at >= floor_at),
    (select min(pv.created_at) from page_views_human pv where pv.created_at >= floor_at),
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
    from page_views_human pv
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
     from page_views_human pv where pv.created_at >= since
     group by pv.path order by count(*) desc limit 20)
  union all
  (select 'referrer'::text, coalesce(pv.referrer_host, '(직접 유입)'),
          count(distinct pv.visitor_id), count(*)
     from page_views_human pv where pv.created_at >= since
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
      from page_views_human pv
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
