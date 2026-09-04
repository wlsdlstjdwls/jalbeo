# 관리자 대시보드 — 접속 현황

> 2026-09-04 신설. 경로 `/admin/`. 로그인은 없고 URL의 토큰이 열쇠다.

## 왜 필요한가

도메인을 붙이고 나면 제일 먼저 볼 숫자가 "사람이 들어오긴 하나"다. `docs/15`가
게이트 2를 폐기하면서 색인 여부를 중단 기준이 아니라 **관측 항목**으로 내렸다.
그 관측을 할 도구가 없었다.

## 무엇을 보여주나

접속정보만 본다. 콘텐츠 관리 기능은 없다.

- 타일 6개: 동시접속(최근 5분), 오늘 방문자, 오늘 조회수, 누적 방문자,
  누적 조회수, 방문당 조회
- 최근 14일 일별 막대 (조회수 기준, KST)
- 인기 경로 top 12 / 유입 호스트 top 12 (최근 7일)
- 1분마다 자동 갱신

## 어떻게 도나

```
방문자 브라우저 --(rpc track_page_view)--> Supabase page_views
관리자 브라우저 --(rpc admin_visitor_*  )--> 집계 결과
```

사이트는 정적이다(`docs/06`의 판단 3). 이 페이지도 정적으로 빌드되고, 숫자는
브라우저가 Supabase REST로 직접 가져온다. 서버는 여전히 없다.

| 파일 | 역할 |
|---|---|
| `db/migrations/0004_page_views.sql` | 테이블 2개 + RPC 4개 |
| `site/src/layouts/Base.astro` | 페이지뷰 1건 기록하는 인라인 스크립트 |
| `site/src/pages/admin.astro` | 대시보드 화면 |
| `site/src/lib/supabase-public.ts` | 빌드 때 anon 키를 읽어 페이지에 박는다 |

## 저장하는 것

브라우저별 무작위 UUID(localStorage), 경로, 유입 **호스트**뿐이다. IP도 UA도
쿼리스트링도 안 받는다. `/admin`으로 시작하는 경로는 클라이언트와 DB 함수
양쪽에서 거른다.

## 접근 통제

로그인이 없으므로 auth로 막을 수가 없다. 대신 토큰이다.

- 통계 RPC는 전부 `p_token`을 받고 `admin_tokens`에 그 값이 있어야만 답한다.
  없으면 `not authorized`로 끊는다
- 토큰은 **DB에만 있고 저장소에는 없다.** 주소는 `/admin/?k=<토큰>` 꼴이다
- 한 번 열면 그 탭의 sessionStorage에 남는다. 주소 없이 들어오면 입력창이 뜬다
- `page_views`, `admin_tokens` 둘 다 RLS를 켜고 정책을 하나도 안 열었다.
  anon 키로 테이블에 직접 붙으면 빈 배열이 온다. 읽기/쓰기는 SECURITY DEFINER
  함수로만 된다

토큰 교체:

```sql
delete from admin_tokens where label = 'owner';
insert into admin_tokens (token, label) values ('<새 토큰>', 'owner');
```

한계는 분명하다. 토큰이 든 URL을 흘리면 그 사람이 통계를 본다. 대신 통계 조회
말고는 아무 것도 못 한다 — 쓰기 함수는 `track_page_view` 하나뿐이고 그건 원래
누구나 부르는 것이다.

## 색인

`/admin`은 세 겹으로 막았다. `<meta name="robots" content="noindex, nofollow">`
(`Base.astro`의 `noindex` prop), `robots.txt`의 `Disallow: /admin`,
사이트맵 제외(`astro.config.mjs`의 sitemap filter).

## 아직 없는 것

- 어뷰징 방어. `track_page_view`는 누구나 부를 수 있어 스크립트로 도배하면
  숫자가 부푼다. 통계 왜곡 말고 피해가 없어 지금은 열어 둔다
- 봇 걸러내기. 크롤러는 JS를 안 돌리는 경우가 많아 대부분 안 잡히지만,
  잡히는 것도 사람과 구분하지 않는다
- 오래된 행 정리. 페이지뷰가 쌓이면 `created_at` 기준 보존 기간을 정해야 한다
