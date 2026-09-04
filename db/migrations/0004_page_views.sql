-- 방문자 집계: 익명 페이지뷰 적재 + 관리자 대시보드용 통계 RPC.
--
-- 개인정보는 저장하지 않는다. 브라우저별 무작위 UUID(localStorage), 경로,
-- 유입 호스트뿐이다. IP도 UA도 안 받는다.
--
-- 이 사이트에는 로그인이 없다. 그래서 통계 읽기는 auth가 아니라 토큰으로 막는다.
-- 관리자 URL(/admin/?k=<토큰>)의 k 값이 곧 열쇠다. 토큰은 admin_tokens에만
-- 있고 저장소에는 없다. 유출되면 그 행을 지우고 새로 넣으면 끝난다.
--
-- 테이블에 RLS 정책을 하나도 열지 않고, 쓰기/읽기 모두 SECURITY DEFINER 함수로만
-- 한다. anon 키로는 테이블에 직접 못 닿는다.

create table page_views (
  id bigint generated always as identity primary key,
  visitor_id uuid not null,
  path text not null,
  referrer_host text,
  created_at timestamptz not null default now()
);

create index page_views_created_idx on page_views (created_at desc);
create index page_views_visitor_idx on page_views (visitor_id, created_at desc);

alter table page_views enable row level security;

create table admin_tokens (
  token text primary key,
  label text,
  created_at timestamptz not null default now()
);

alter table admin_tokens enable row level security;

-- 페이지뷰 기록. 방문자가 직접 호출하므로 인증 요구 없음.
-- 스크립트 도배에는 열려 있는 구조다. 통계 왜곡 말고는 피해가 없어 지금은 허용한다.
create function public.track_page_view(
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
  -- 관리자 화면 조회는 통계에서 뺀다 (클라이언트에서도 거르지만 이중 방어)
  if p_path like '/admin%' then
    return;
  end if;
  insert into page_views (visitor_id, path, referrer_host)
  values (p_visitor_id, left(p_path, 200), left(nullif(p_referrer_host, ''), 100));
end;
$$;

grant execute on function public.track_page_view(uuid, text, text) to anon, authenticated;

-- 관리자 대시보드 통계. 동시접속은 최근 5분 내 기록을 남긴 방문자 수다.
-- '오늘'은 KST 자정 기준.
create function public.admin_visitor_stats(p_token text)
returns table (
  concurrent_visitors bigint,
  today_visitors bigint,
  total_visitors bigint,
  today_views bigint,
  total_views bigint,
  first_view_at timestamptz
)
language plpgsql
security definer
set search_path = public
as $$
declare
  kst_midnight timestamptz;
begin
  if not exists (select 1 from admin_tokens t where t.token = p_token) then
    raise exception 'not authorized';
  end if;

  kst_midnight := date_trunc('day', now() at time zone 'Asia/Seoul') at time zone 'Asia/Seoul';

  return query select
    (select count(distinct pv.visitor_id) from page_views pv
      where pv.created_at > now() - interval '5 minutes'),
    (select count(distinct pv.visitor_id) from page_views pv
      where pv.created_at >= kst_midnight),
    (select count(distinct pv.visitor_id) from page_views pv),
    (select count(*) from page_views pv where pv.created_at >= kst_midnight),
    (select count(*) from page_views pv),
    (select min(pv.created_at) from page_views pv);
end;
$$;

grant execute on function public.admin_visitor_stats(text) to anon, authenticated;

-- 최근 N일 일별 추이 (KST 기준). 빈 날짜도 0으로 채워 그래프가 끊기지 않게 한다.
create function public.admin_visitor_daily(p_token text, p_days int default 14)
returns table (day date, visitors bigint, views bigint)
language plpgsql
security definer
set search_path = public
as $$
begin
  if not exists (select 1 from admin_tokens t where t.token = p_token) then
    raise exception 'not authorized';
  end if;

  return query
  with span as (
    select generate_series(
      (now() at time zone 'Asia/Seoul')::date - (greatest(least(p_days, 90), 1) - 1),
      (now() at time zone 'Asia/Seoul')::date,
      interval '1 day'
    )::date as day
  ),
  agg as (
    select (pv.created_at at time zone 'Asia/Seoul')::date as day,
           count(distinct pv.visitor_id) as visitors,
           count(*) as views
    from page_views pv
    group by 1
  )
  select s.day, coalesce(a.visitors, 0), coalesce(a.views, 0)
  from span s left join agg a on a.day = s.day
  order by s.day;
end;
$$;

grant execute on function public.admin_visitor_daily(text, int) to anon, authenticated;

-- 인기 경로 / 유입 호스트. p_since_days가 null이면 전체 기간.
create function public.admin_visitor_breakdown(p_token text, p_since_days int default 7)
returns table (kind text, label text, visitors bigint, views bigint)
language plpgsql
security definer
set search_path = public
as $$
declare
  since timestamptz;
begin
  if not exists (select 1 from admin_tokens t where t.token = p_token) then
    raise exception 'not authorized';
  end if;

  since := case when p_since_days is null
                then '-infinity'::timestamptz
                else now() - make_interval(days => greatest(least(p_since_days, 365), 1)) end;

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

grant execute on function public.admin_visitor_breakdown(text, int) to anon, authenticated;
