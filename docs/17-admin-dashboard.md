# 관리자 대시보드 — 접속 현황

> 2026-09-04 신설. 경로 `/admin/`. Supabase Auth 이메일 로그인.

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
| `db/migrations/0004_page_views.sql` | page_views 테이블 + 집계 RPC |
| `db/migrations/0005_admin_auth.sql` | URL 토큰을 Supabase Auth 로그인으로 교체 |
| `site/src/layouts/Base.astro` | 페이지뷰 1건 기록하는 인라인 스크립트 |
| `site/src/pages/admin.astro` | 대시보드 화면 |
| `site/src/lib/supabase-public.ts` | 빌드 때 anon 키를 읽어 페이지에 박는다 |

## 저장하는 것

브라우저별 무작위 UUID(localStorage), 경로, 유입 **호스트**뿐이다. IP도 UA도
쿼리스트링도 안 받는다. `/admin`으로 시작하는 경로는 클라이언트와 DB 함수
양쪽에서 거른다.

## 접근 통제

Supabase Auth 로그인이다 (`db/migrations/0005`). 처음에는 URL 토큰이었는데
(`0004`), 외우기 쉬운 키를 쓰려는 순간 무너지는 구조였다. 통계 RPC가 공개라
무차별 대입을 막는 게 아무 것도 없었다.

- 비밀번호는 `auth.users`에 해시로만 있다. 시도 제한, 세션 만료, 메일 재설정은
  전부 Supabase Auth가 한다
- 통계 RPC는 인자를 안 받는다. 요청에 실린 JWT의 이메일이 `admins` 명단에
  있는지 `is_admin()`이 본다. 없으면 `not authorized`
- **계정이 있는 것과 관리자인 것은 다르다.** 가입은 누구나 할 수 있어도
  `admins`에 없으면 숫자를 못 본다
- 세션은 localStorage에 둔다. access_token은 한 시간이면 만료되고
  refresh_token으로 조용히 갱신한다. 상단 '로그아웃'으로 끊는다
- `page_views`, `admins` 둘 다 RLS를 켜고 정책을 하나도 안 열었다.
  테이블에 직접 붙으면 빈 배열이 온다. 읽기/쓰기는 SECURITY DEFINER 함수로만

계정 만들기 (한 번만):

```
Supabase 대시보드 > Authentication > Users > Add user
이메일과 비밀번호를 넣고 'Auto Confirm User'를 켠다
```

관리자 명단은 `scripts/admin_admins.py`가 관리한다.

```
python scripts/admin_admins.py list                명단 + 계정 유무
python scripts/admin_admins.py add <이메일> [라벨]  명단에 넣기
python scripts/admin_admins.py remove <이메일>      명단에서 빼기
```

명단에 넣는 것과 계정을 만드는 것은 순서 상관없다. 비밀번호는 이 스크립트를
지나가지 않는다.

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
