-- 인기 경로 / 유입 경로를 페이지 단위로 넘긴다.
--
-- 0005의 `admin_visitor_breakdown`은 두 축을 union all로 붙여 각 20행을
-- 한 번에 준다. 화면 요약(5행)에는 그게 맞지만, 전체보기 시트는 스크롤로
-- 계속 받아야 하므로 축을 하나만 골라 offset을 받는 함수가 따로 필요하다.
--
-- total_rows는 window count다. 시트가 "더 있나"를 알아야 스크롤 끝에서
-- 헛요청을 안 한다. 한 번 더 세는 비용은 이미 group by 한 결과 위라 싸다.
-- limit은 100으로 묶는다. 관리자만 부르는 함수지만 상한이 없으면
-- 실수로 한 번에 전부 끌어오는 요청이 나온다.

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

grant execute on function public.admin_visitor_breakdown_page(text, int, int, int) to authenticated;
