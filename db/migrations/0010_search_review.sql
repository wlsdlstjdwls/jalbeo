-- 관리자 화면에서 검색어 로그 후보를 본다 (docs/63).
--
-- 지금까지는 scripts/search_log_candidates.py를 손으로 돌려야 후보가 보였다.
-- 관리자 대시보드가 이미 로그인과 is_admin() 판정을 갖고 있으므로 거기에
-- 붙인다. 리포 시크릿에 DB 계정을 넣는 자동 잡보다 열린 문이 적다.
--
-- 후보가 '이미 걸리는가'는 DB가 아니라 화면이 판정한다. 품목명과 별칭은
-- 빌드 때 페이지에 구워지는 items.json이 원본이고, 발행 직후 그 판정이
-- 저절로 바뀌어야 하기 때문이다 (판단 71 - 찍힌 값 말고 지금 어휘로 다시 잰다).
--
-- 여기에 쌓는 것은 사람이 내린 판정뿐이다. 오타, 입력 조각, 보류처럼
-- 어휘로는 안 지워지는 것을 다시 안 보이게 한다.

create table search_term_decisions (
  term text primary key,
  decision text not null check (decision in ('보류', '노이즈')),
  decided_at timestamptz not null default now()
);

alter table search_term_decisions enable row level security;

-- 못 찾은 검색(hit_count = 0)과 그 판정. 같은 방문자가 짧은 간격으로 친
-- 앞토막 접기는 화면이 한다 - 스크립트의 fold_prefixes와 같은 일이다.
create or replace function public.admin_search_misses(p_days int default 90)
returns table (
  term text,
  visitor_id uuid,
  created_at timestamptz,
  decision text
)
language plpgsql
security definer
set search_path = public
as $$
begin
  if not is_admin() then
    raise exception 'not authorized';
  end if;
  return query
    select q.term, q.visitor_id, q.created_at, d.decision
      from search_queries q
      left join search_term_decisions d on d.term = q.term
     where q.hit_count = 0
       and char_length(q.term) >= 2
       and q.created_at >= now() - make_interval(days => greatest(p_days, 1))
     order by q.created_at;
end;
$$;

-- 판정을 적거나(보류, 노이즈) 지운다(null).
create or replace function public.admin_set_search_decision(p_term text, p_decision text)
returns void
language plpgsql
security definer
set search_path = public
as $$
begin
  if not is_admin() then
    raise exception 'not authorized';
  end if;
  if p_decision is null then
    delete from search_term_decisions where term = p_term;
  else
    insert into search_term_decisions (term, decision) values (p_term, p_decision)
    on conflict (term) do update set decision = excluded.decision, decided_at = now();
  end if;
end;
$$;

revoke all on function public.admin_search_misses(int) from public, anon;
revoke all on function public.admin_set_search_decision(text, text) from public, anon;
grant execute on function public.admin_search_misses(int) to authenticated;
grant execute on function public.admin_set_search_decision(text, text) to authenticated;
