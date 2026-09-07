-- 로그 보관 기간을 정하고 자동으로 지운다.
--
-- 0004(페이지뷰)와 0007(검색어)은 개인정보를 안 담는다는 것만 적고 언제까지
-- 두는지를 안 정했다. 정해 두지 않으면 무기한이고, 개인정보처리방침에
-- 보관 기간을 적을 근거가 없다. 방침(/privacy)에 적은 숫자가 여기 있다.
--
--   페이지뷰  12개월 - 전년 같은 달과 비교하는 데까지만 필요하다
--   검색어    24개월 - 못 찾은 검색어가 품목 확장 원천이라 계절성을 두 해 본다
--
-- 지금 쌓인 건 나흘치(2026-09-04~)라 이 함수가 지우는 행은 아직 없다.
-- 방침에 적기 전에 장치를 먼저 붙이는 것이다 - 본문에 손으로 적은 숫자가
-- 데이터와 어긋나는 것이 이 저장소에서 이미 여러 번 나왔다(판단 19번).

create or replace function public.purge_old_logs()
returns table (purged_page_views bigint, purged_search_queries bigint)
language plpgsql
security definer
set search_path = public
as $$
declare
  v_pv bigint;
  v_sq bigint;
begin
  delete from page_views where created_at < now() - interval '12 months';
  get diagnostics v_pv = row_count;
  delete from search_queries where created_at < now() - interval '24 months';
  get diagnostics v_sq = row_count;
  return query select v_pv, v_sq;
end;
$$;

-- 방문자가 부를 이유가 없다. anon/authenticated 에는 실행 권한을 안 준다.
revoke all on function public.purge_old_logs() from public, anon, authenticated;

-- 매달 2일 04:00 KST(= 1일 19:00 UTC)에 돈다. pg_cron 은 UTC로 돌고 'L' 같은
-- 확장 문법을 안 받아서 날짜를 UTC 기준으로 적는다. pg_cron 이 없으면 아래
-- 블록만 조용히 건너뛴다 - 그때는 scripts/purge_logs.py 를 사람이 돌린다.
do $$
begin
  create extension if not exists pg_cron;
exception when others then
  raise notice 'pg_cron 사용 불가: %', sqlerrm;
end;
$$;

do $$
begin
  perform cron.unschedule('purge-old-logs');
exception when others then
  null;
end;
$$;

do $$
begin
  perform cron.schedule('purge-old-logs', '0 19 1 * *', 'select public.purge_old_logs()');
exception when others then
  raise notice 'cron 등록 실패(수동 실행으로 대체): %', sqlerrm;
end;
$$;
