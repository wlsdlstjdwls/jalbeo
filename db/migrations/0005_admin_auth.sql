-- 관리자 접근을 URL 토큰에서 Supabase Auth 로그인으로 바꾼다.
--
-- 0004는 로그인이 없다는 전제로 admin_tokens에 평문 키를 두고 그걸 대조했다.
-- 무작위 32자면 실제로 안 뚫리지만, 외우기 쉬운 키를 쓰려는 순간 무너진다.
-- 통계 RPC가 공개라 무차별 대입을 막는 게 아무 것도 없었다.
--
-- 이제 판정 기준은 요청에 실린 JWT다. 비밀번호는 auth.users에 해시로만 있고,
-- 시도 제한, 세션 만료, 메일 재설정은 Supabase Auth가 한다.
-- 관리자 명단은 이메일로 둔다. 계정을 만들기 전에 미리 넣어둘 수 있다.

create table admins (
  email text primary key,
  label text,
  created_at timestamptz not null default now()
);

alter table admins enable row level security;

-- 로그인한 사용자의 이메일이 명단에 있는지 본다.
create function public.is_admin()
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1 from admins a
    where a.email = lower(nullif(auth.jwt() ->> 'email', ''))
  );
$$;

grant execute on function public.is_admin() to anon, authenticated;

-- 토큰을 받던 옛 함수들을 걷어낸다. 같이 두면 뒷문이 남는다.
drop function if exists public.admin_visitor_stats(text);
drop function if exists public.admin_visitor_daily(text, int);
drop function if exists public.admin_visitor_breakdown(text, int);
drop table if exists admin_tokens;

create function public.admin_visitor_stats()
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
  if not is_admin() then
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

grant execute on function public.admin_visitor_stats() to authenticated;

create function public.admin_visitor_daily(p_days int default 14)
returns table (day date, visitors bigint, views bigint)
language plpgsql
security definer
set search_path = public
as $$
begin
  if not is_admin() then
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

grant execute on function public.admin_visitor_daily(int) to authenticated;

create function public.admin_visitor_breakdown(p_since_days int default 7)
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

grant execute on function public.admin_visitor_breakdown(int) to authenticated;
