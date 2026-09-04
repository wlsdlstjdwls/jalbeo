-- 사이트 내 검색창 질의 적재. 방문자가 찾다가 못 찾은 물건을 품목 확장
-- 후보로 쓰기 위해서다 (docs/20).
--
-- page_views(0004)와 같은 원칙: 개인정보 없음, RLS로 테이블 직접 접근을
-- 막고 SECURITY DEFINER 함수로만 쓴다. 저장하는 건 정규화한 검색어,
-- 그 순간 화면에 몇 건이 걸렸는지(hit_count), 방문자 무작위 UUID뿐이다.
--
-- hit_count = 0인 행이 핵심 신호다. 사이트에 없는 물건을 찾다가 못 찾은
-- 검색어라서, docs/18 13번("씨앗은 발행분에서 뽑는다")과 같은 자리에서
-- 품목 후보 원천으로 쓴다.
--
-- 읽기는 admin RPC를 따로 두지 않는다. 관리자 대시보드가 볼 통계가 아니라
-- 확장 작업(scripts/)이 DB 자격증명으로 직접 조회하는 원천 데이터다
-- (scripts/admin_admins.py의 psycopg2 접속 방식을 그대로 쓴다).

create table search_queries (
  id bigint generated always as identity primary key,
  term text not null,
  hit_count int not null,
  visitor_id uuid,
  created_at timestamptz not null default now()
);

create index search_queries_created_idx on search_queries (created_at desc);
create index search_queries_miss_idx on search_queries (term) where hit_count = 0;

alter table search_queries enable row level security;

-- 검색어 1건 기록. 방문자가 직접 호출하므로 인증 요구 없음(page_views와 동일 위험 인수).
-- 매 키 입력마다 쏘면 소음만 쌓이므로 클라이언트가 입력 멈춤(디바운스) 뒤에만 부른다.
create function public.track_search_query(
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
  insert into search_queries (term, hit_count, visitor_id)
  values (left(trim(p_term), 60), greatest(coalesce(p_hit_count, 0), 0), p_visitor_id);
end;
$$;

grant execute on function public.track_search_query(text, int, uuid) to anon, authenticated;
